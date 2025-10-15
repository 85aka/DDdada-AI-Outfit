# DD搭搭 – AI 智能穿搭推薦系統
（DD Dada – AI Outfit Recommendation System）

> 👤 **Developer:** cheng yenchen  
> 💡 **Role:** Backend & AI Integration / System Architecture / Frontend Coordination  
> 🛠 **Built with:** Flask, OpenAI API, MongoDB, HTML, CSS, JavaScript

---

## Overview
DD Dada is an AI-powered outfit recommendation system. Users upload clothing images and receive AI-generated outfit suggestions via image-to-text prompts and rule-based filtering.

**Features**
- Personal closet management (upload tops/bottoms)
- AI outfit recommendations (OpenAI API)
- Interactive chatbot for styling
- “Today’s outfit” suggestions
- Outfit history management

**Tech Stack**
- Backend: Flask (Python)  
- AI: OpenAI API  
- Database: MongoDB  
- Frontend: HTML / CSS / JavaScript  

---

## 安裝與執行
```bash
pip install -r DiDiDaDa/requirements.txt
copy DiDiDaDa/.env.example DiDiDaDa/.env  # Windows PowerShell 請手動複製
python DiDiDaDa/main.py
```
預設伺服器：`http://127.0.0.1:8000`

**環境變數**
- 建立 `.env`（勿提交版本控制）：
```
OPENAI_API_KEY=your_key_here
MONGODB_URI=mongodb://127.0.0.1:27017/DiDiDaDa
FLASK_SECRET_KEY=change-me
MAX_CONTENT_LENGTH=5242880
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
PROMPTPERFECT_API_KEY=your_promptperfect_key
PROMPTPERFECT_URL=https://api.promptperfect.jina.ai/optimize
CWB_FORECAST_URL=https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=YOUR-CWB-TOKEN
```

---
## 範例指令

```bash
# 1) Clone repository
git clone https://github.com/chengyenchen/DDdada-AI-Outfit.git
cd DDdada-AI-Outfit

# 2) 安裝依賴
pip install -r DiDiDaDa/requirements.txt

# 3) 設定環境變數（僅限本機，勿提交）
# 請依照 .env.example 建立 DiDiDaDa/.env

# 4) 啟動伺服器
python DiDiDaDa/main.py

# 5) 瀏覽器開啟
http://127.0.0.1:8000
```

---
## API 路由

| Method(s) | Path | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/error` | Error page |
| GET | `/Login` | Login page |
| GET | `/Signup` | Signup page |
| POST | `/4SignupPG` | Handle signup form submit |
| GET | `/signout` | Logout user |
| GET | `/Mycloset` | User closet UI |
| POST | `/upload` | Upload clothing image |
| POST | `/getPrompt` | Generate outfit prompt |
| GET | `/Todays` | 今日穿搭頁面 |
| POST | `/generate_image` | AI image generation |
| POST | `/chat` | Chatbot reply |
| POST | `/optimize_prompt` | Optimize styling prompt |
| POST | `/weather` | Fetch/process weather info |


---

## 專案結構
```
DiDiDaDa/
├── main.py
├── requirements.txt
├── .env              # 僅本機使用，勿提交
├── app/
│   ├── __init__.py
│   ├── route.py
│   ├── models/
│   │   └── upload.py
│   ├── static/
│   │   ├── assets/
│   │   ├── css/
│   │   └── js/
│   └── templates/
└── tt/
```

_Last updated: 2025-10-13_
