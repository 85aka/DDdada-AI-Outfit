import os, tempfile, replicate, cloudinary.uploader
from werkzeug.utils import secure_filename
from flask import current_app
from dotenv import load_dotenv

load_dotenv()

def upload_image(file, username, category):
    filename = secure_filename(file.filename)

    # 生成一個臨時文件保存上傳的文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_filepath = temp_file.name

    # 上傳圖片並從 Cloudinary 獲取 URL
    upload_result = cloudinary.uploader.upload(temp_filepath, folder=username)
    image_url = upload_result['url']

    # 生成 prompt（改為從環境變數讀取）
    api_token = os.getenv('REPLICATE_API_TOKEN')
    if api_token is None:
        raise Exception('缺少 REPLICATE_API_TOKEN 環境變數')
    prompt = describe_cloth(temp_filepath, api_token)

    # 儲存到 MongoDB
    db = current_app.config["db"]
    user_images_collection = db.user_images
    document = {
        "filename": filename,
        "userid": username,       
        'url': image_url,
        "prompt": prompt,
        'category': category
    }
    user_images_collection.insert_one(document)

    # 刪除臨時文件
    os.remove(temp_filepath)



def describe_cloth(filepath, api_token):
    prompt_text = "Describe the cloth strictly following the format: 'The [type of cloth] is [color] with a [design] on it.' Make sure not to add any additional details."
    
    for attempt in range(10):  # 最多重试10次
        output = replicate.run(
            "daanelson/minigpt-4:b96a2f33cc8e4b0aa23eacfce731b9c41a7d9466d9ed4e167375587b54db9423",
            input={
                "image": open(filepath, "rb"),
                "prompt": prompt_text,
            },
            token=api_token
        )

        if len(output) <= 20:  # 检查生成的描述是否不超过20个字符
            break  # 如果不超过20个字符，就退出循环
        else:
            print(f"Attempt {attempt + 1}: Description too long, retrying...")
    
    return output



def is_allowed_file(filename):
    # 添加文件验证逻辑，检查文件类型或其他验证规则
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
