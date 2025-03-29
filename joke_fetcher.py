import os
import json
import random
import requests
from datetime import datetime
import config

class JokeFetcher:
    """负责从不同来源获取笑话"""
    
    @staticmethod
    def get_joke():
        """获取笑话的主方法，会尝试多种获取方式"""
        # 先尝试API获取
        joke = JokeFetcher._get_from_tianxing_api()
        if joke:
            return joke
            
        # 如果API失败，从本地获取
        return JokeFetcher._get_from_local_file()
    
    @staticmethod
    def _get_from_tianxing_api():
        """从天行数据API获取笑话"""
        if not config.TIANXING_API_KEY:
            return None
            
        try:
            url = "http://api.tianapi.com/joke/index"
            params = {
                "key": config.TIANXING_API_KEY,
                "num": 1,
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("code") == 200:
                return data.get("newslist", [{}])[0].get("content", "")
            return None
        except Exception as e:
            print(f"从天行数据API获取笑话失败: {e}")
            return None
    
    @staticmethod
    def _get_from_local_file():
        """从本地文件随机获取笑话"""
        try:
            if os.path.exists(config.JOKES_FILE):
                with open(config.JOKES_FILE, "r", encoding="utf-8") as f:
                    jokes = json.load(f)
                return random.choice(jokes)
            return "今天没有笑话，因为笑话文件不存在。"
        except Exception as e:
            print(f"从本地文件获取笑话失败: {e}")
            return "笑话走丢了，明天再来看吧！"
            
    @staticmethod
    def get_joke_title():
        """生成笑话标题"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"每日笑话 ({date_str})" 