from flask import Flask
import os, pymongo, cloudinary, tempfile
from dotenv import load_dotenv

# 載入環境變數（僅本機開發使用）
load_dotenv()

# 初始化資料庫連線
mongo_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/DiDiDaDa")
tls_allow_invalid = os.getenv("MONGODB_TLS_ALLOW_INVALID", "false").lower() == "true"
client = pymongo.MongoClient(mongo_uri, tlsAllowInvalidCertificates=tls_allow_invalid)

db = client.DiDiDaDa
# print("Database connection established successfully")

# 初始化 Flask 伺服器
app = Flask( __name__, static_folder="static", static_url_path="/" )
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me-in-.env")
# 限制上傳大小（例如 5MB）
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["db"] = client.DiDiDaDa

# 設定 Cloudinary（從環境變數讀取）
cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', ''),  
  api_key = os.getenv('CLOUDINARY_API_KEY', ''),  
  api_secret = os.getenv('CLOUDINARY_API_SECRET', '')  
)
# 引入路由設定
from . import route
