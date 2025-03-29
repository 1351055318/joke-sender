import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Server酱配置
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY", "")

# 邮箱配置
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# 天行数据API配置
TIANXING_API_KEY = os.getenv("TIANXING_API_KEY", "")

# 笑话文件路径
JOKES_FILE = "jokes.json"

# 默认推送时间
DEFAULT_PUSH_TIME = "08:00"

# 是否启用各种推送方式
ENABLE_DESKTOP_NOTIFICATION = True
ENABLE_EMAIL = bool(EMAIL_USER and EMAIL_PASSWORD and EMAIL_TO)
ENABLE_WECHAT = bool(SERVER_CHAN_KEY)

# 桌面通知持续时间（秒）
NOTIFICATION_DURATION = 5 