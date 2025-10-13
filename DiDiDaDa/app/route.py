import openai, requests, os
from flask import *
from datetime import datetime, timedelta
from .import app, db  
from .models.upload import *
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# 設定 OpenAI API Key（從環境變數讀取）
openai.api_key = os.getenv('OPENAI_API_KEY')

URL = os.getenv("CWB_FORECAST_URL")
app.secret_key = app.secret_key or os.getenv('FLASK_SECRET_KEY', 'change-me-in-.env')

# 全域變數來儲存訊息與上一個 AI 回應
messages = []
last_ai_response = ""
# 用於儲存對話歷史的全域變數（限制最近 N 輪）
max_history = 10
dialog_history = []

# 設定 PromptPerfect API（從環境變數讀取）
promptperfect_api_key = os.getenv("PROMPTPERFECT_API_KEY")
promptperfect_url = os.getenv("PROMPTPERFECT_URL", "https://api.promptperfect.jina.ai/optimize")


@app.route("/")
def Index():
    return render_template('index.html')

# /error?msg=錯誤訊息
@app.route("/error")
def error():
    message = request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", message=message)


@app.route("/Login")
def Login():
    if "username" in session:
        return render_template("mycloset.html")
    else:
        return render_template("login.html")  # 權限管理，未登入無法進入 Todays
    # return render_template('login.html')

@app.route("/Signup")
def signup():
    return render_template('signup.html')

@app.route('/4SignupPG', methods=['POST'])
def forSignupPG():
    #　從前端接收資料
    action = request.form.get('action')
    username = request.form.get('username')
    password = request.form.get('password')
    sex = request.form.get('sex')  # 性別
    height = float(request.form.get('height', 180))  # 新增接收身高
    weight = float(request.form.get('weight', 80))  # 新增接收體重

    # 計算 BMI
    bmi = weight / (height/100)**2

    if action == 'signup': 
        collection = db.user
        # 檢查使用者是否已存在
        if collection.find_one({"username": username}):
            return redirect("/error?msg=用戶名已經被註冊")
        # 寫入資料庫，完成註冊（雜湊密碼）
        password_hash = generate_password_hash(password)
        collection.insert_one({
            "username": username,
            "password_hash": password_hash,
            'sex': sex,
            "height": height,
            "weight": weight,
            "bmi": bmi  # 存入計算的 BMI
        })
        return redirect("/Login")
    elif action == '2signup':       return redirect("/Signup")
    elif action == '2login':        return redirect("/signout")
    elif action == 'login':
        if not username or not password:
            return redirect("/error?msg=用戶和密碼不得為空")

        # 與資料庫互動
        collection = db.user
        # 以 username 取得使用者
        result = collection.find_one({"username": username})
        # 找不到對應資料，登入失敗
        if not result:
            return redirect("/error?msg=帳號或密碼輸入錯誤")
        # 檢查密碼：支援 password_hash，或後援舊版明碼欄位
        password_ok = False
        if "password_hash" in result:
            password_ok = check_password_hash(result["password_hash"], password)
        elif "password" in result:
            password_ok = (result["password"] == password)
        if not password_ok:
            return redirect("/error?msg=帳號或密碼輸入錯誤")

        # 登入成功，於 Session 紀錄會員資訊
        session["username"] = result["username"]
        global usersex, userbmi
        usersex = result.get("sex", "person")
        userbmi = result.get("bmi", 22.0)
        return redirect("/Mycloset")

@app.route("/signout")
def signout():
    if "username" in session:
        del session["username"]  # 移除 Session 中的會員資訊
        return redirect("/Login")
    else:
        return redirect("/Login")




@app.route("/Mycloset")
def mycloset():
    # 檢查是否有登入使用者
    if 'username' in session:
        current_username = session['username']
        
        # 根據用戶名稱檢索相關的圖像數據
        lower_body_images = db.user_images.find({"category": "lower_body", "userid": current_username})
        upper_body_images = db.user_images.find({"category": "upper_body", "userid": current_username})
        
        return render_template('mycloset.html', lower_body_images=lower_body_images, upper_body_images=upper_body_images)
    else:
        return redirect("/error?msg=尚未登入")
    
@app.route('/upload', methods=['POST'])
def upload():
    # 取得上傳檔案、使用者名稱、部位分類
    if 'fileToUpload' not in request.files:
        return jsonify({'error': '未提供上傳檔案'}), 400
    file = request.files['fileToUpload']
    username = session.get("username")
    category = request.form.get('category')

    if not username:
        return jsonify({'error': '未登入'}), 401
    if not file or file.filename == '':
        return jsonify({'error': '未選擇檔案'}), 400
    if category not in {"upper_body", "lower_body"}:
        return jsonify({'error': '分類不正確'}), 400
    if not is_allowed_file(file.filename):
        return jsonify({'error': '不支援的檔案格式'}), 400

    # 呼叫函式上傳並儲存檔案
    upload_image(file, username, category)

    # 回傳空響應
    return ('', 200)


@app.route('/getPrompt', methods=['POST'])
def get_prompt():
    global combined_prompt
    if userbmi < 18.5:
        category = 'slimmer'
    elif 18.5 <= userbmi < 24.9:
        category = 'moderate'
    elif 24.9 <= userbmi < 29.9:
        category = 'fat'
    else:
        category = 'heavier'
    # 清除舊的會話變數
    session.pop('generated_image_url', None)
    session.pop('combined_prompt', None)

    top_image_url = request.form['topImageURL']
    bottom_image_url = request.form['bottomImageURL']

    # 查詢 MongoDB 以找到與這些圖像相關的記錄
    top_image_prompt = db.user_images.find_one({'url': top_image_url})
    bottom_image_prompt = db.user_images.find_one({'url': bottom_image_url})

    if top_image_prompt and bottom_image_prompt:
        top_prompt = top_image_prompt.get('prompt', 'Prompt not found')
        bottom_prompt = bottom_image_prompt.get('prompt', 'Prompt not found')

        combined_prompt = f"A {category} {usersex} full-body portrait of a person wearing  with {top_prompt} And are also wearing {bottom_prompt}"
        session.pop('generated_image_url', None)  # 清除已存在的圖片 URL
        session['combined_prompt'] = combined_prompt
        print(combined_prompt)
        return jsonify({'success': True, 'redirect_url': url_for('Todays'),'combined_prompt': combined_prompt})
    else:
        return jsonify({'success': False, 'error': 'Image not found in database'})



@app.route("/Todays")
def Todays():
    if "username" in session:
        # 取得城市名稱列表
        response = requests.get(URL)
        data = response.json()
        locations = data['records']['locations'][0]['location']
        city_names = [location['locationName'] for location in locations]

        # 檢查 session 是否有 combined_prompt
        combined_prompt = session.get('combined_prompt')


        if combined_prompt:
            # 如果有，呼叫 generate_image 生成圖片
            generation_response = openai.Image.create(
                prompt=combined_prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3",
                response_format="url"
            )
            generated_image_url = generation_response["data"][0]["url"]

            # 清除 session 中的 combined_prompt
            session.pop('combined_prompt', None)

            # 將生成的圖片 URL 傳遞給模板
            return render_template('todays.html', city_names=city_names, image_url=generated_image_url)
        else:
            # 若 session 中沒有 combined_prompt，正常顯示 todays 頁面
            return render_template('todays.html', city_names=city_names, image_url=None)
    else:
        return redirect("/error?msg=尚未登入")


@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.get_json()
    optimized_prompt = data.get('optimized_prompt')

    if not optimized_prompt:
        return jsonify({'error': 'No optimized prompt provided'}), 400

    try:
        generation_response = openai.Image.create(
            prompt=optimized_prompt,
            n=1,
            size="1024x1024",
            model="dall-e-3",
            response_format="url"
        )

        generated_image_url = generation_response["data"][0]["url"]
        return jsonify({'image_url': generated_image_url})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500


@app.route('/chat', methods=['POST'])
def chat():
    global last_ai_response
    global dialog_history

    data = request.get_json()
    user_message = data.get('user_message')

    if not user_message:
        return jsonify({"ai_msg": "No message received"}), 400

    try:
        if len(dialog_history) >= max_history:
            dialog_history.pop(0)

        dialog_history.append({"role": "user", "content": user_message})

        # 这里直接发送一个翻译的指令给 AI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Translate the following to English: " + user_message}
            ] + dialog_history,
        )
        ai_response = response.choices[0].message['content']

        dialog_history.append({"role": "assistant", "content": ai_response})
        last_ai_response = ai_response
        print(last_ai_response)

        return jsonify({"ai_msg": ai_response})
    except Exception as e:
        return jsonify({"ai_msg": f"Error: {str(e)}"}), 500
    
    
@app.route('/optimize_prompt', methods=['POST'])
def optimize_prompt():
    # 從請求中取得 AI 的回覆
    last_ai_response = request.get_json().get('last_ai_response')


    if not last_ai_response:
        return jsonify({'error': 'No AI response to optimize'}), 400

    try:
        headers = {
            "x-api-key": promptperfect_api_key or "",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "prompt": combined_prompt+ last_ai_response ,
                "targetModel": "dall-e"
            }
        }

        # 发送请求到 PromptPerfect API
        response = requests.post(promptperfect_url, headers=headers, json=payload)

        if response.status_code == 200:
            response_json = response.json()
            optimized_prompt = response_json.get('result', {}).get('promptOptimized')
            return jsonify({'optimized_prompt': optimized_prompt})
        else:
            return jsonify({'error': f"請求失敗，狀態碼：{response.status_code}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route('/weather', methods=['POST'])
def get_weather():
    selected_city = request.form.get('city')

    response = requests.get(URL)
    data = response.json()
    locations = data['records']['locations'][0]['location']

    # 獲取當前日期和星期，只取五天的日期
    today = datetime.now()
    days = [(today + timedelta(days=i)).strftime('%m/%d') for i in range(5)]
    chinese_days = [(today + timedelta(days=i)).strftime('%A') for i in range(5)]
    chinese_day_dict = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日'
    }
    chinese_days = [chinese_day_dict[day] for day in chinese_days]

    temperatures = []
    rain_chances = []

    for location in locations:
        if location['locationName'] == selected_city:
            for weather_element in location['weatherElement']:
                element_name = weather_element['elementName']

                if element_name == "T":
                    temperatures = [t['elementValue'][0]['value'] for t in weather_element['time']][:5]
                if element_name == "PoP12h":
                    rain_chances = [pop['elementValue'][0]['value'] for pop in weather_element['time']][:5]

    weather_data = []
    for i, day in enumerate(days):
        if i < len(temperatures) and i < len(rain_chances):
            weather_data.append({
                'date': day,
                'day': chinese_days[i],
                'temperature': temperatures[i],
                'rain_chance': rain_chances[i]
            })

    return jsonify(weather_data)

