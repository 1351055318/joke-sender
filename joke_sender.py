import os
import json
import random
import requests
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class JokeSender:
    def __init__(self):
        self.jokes_file = "jokes.json"
        self.server_chan_key = os.getenv("SERVER_CHAN_KEY", "")
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.email_to = os.getenv("EMAIL_TO", "")
        
    def get_joke_from_api(self):
        """从API获取笑话"""
        try:
            # 使用天行数据API获取笑话
            api_key = os.getenv("TIANXING_API_KEY", "")
            if api_key:
                url = "http://api.tianapi.com/joke/index"
                params = {
                    "key": api_key,
                    "num": 1,
                }
                response = requests.get(url, params=params)
                data = response.json()
                if data.get("code") == 200:
                    return data.get("newslist", [{}])[0].get("content", "获取笑话失败")
            
            # 备选方案：随机从本地笑话库获取
            return self.get_random_joke_from_file()
        except Exception as e:
            print(f"API获取笑话出错: {e}")
            return self.get_random_joke_from_file()
    
    def get_random_joke_from_file(self):
        """从本地文件随机获取笑话"""
        try:
            if os.path.exists(self.jokes_file):
                with open(self.jokes_file, "r", encoding="utf-8") as f:
                    jokes = json.load(f)
                return random.choice(jokes)
            return "今天没有笑话，因为笑话文件不存在。"
        except Exception as e:
            print(f"获取本地笑话出错: {e}")
            return "笑话走丢了，明天再来看吧！"
    
    def send_desktop_notification(self, message):
        """发送桌面通知"""
        try:
            if os.name == "nt":  # Windows
                from win32api import GetModuleHandle
                from win32gui import Shell_NotifyIcon, NIM_ADD, NIM_MODIFY, NIM_DELETE
                from win32gui import NIIF_INFO, NIF_INFO, NIF_ICON, NIF_MESSAGE, NIF_TIP
                import win32con
                import win32gui
                
                class WindowsBalloonTip:
                    def __init__(self, title, msg):
                        message_map = {win32con.WM_DESTROY: self.OnDestroy}
                        
                        # 注册窗口类
                        wc = win32gui.WNDCLASS()
                        hinst = wc.hInstance = GetModuleHandle(None)
                        wc.lpszClassName = "PythonTaskbar"
                        wc.lpfnWndProc = message_map
                        class_atom = win32gui.RegisterClass(wc)
                        
                        # 创建窗口
                        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
                        self.hwnd = win32gui.CreateWindow(
                            class_atom, "Taskbar", style,
                            0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                            0, 0, hinst, None
                        )
                        
                        # 设置通知图标
                        hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
                        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP | NIF_INFO
                        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "笑话推送", msg, 200, title, NIIF_INFO)
                        Shell_NotifyIcon(NIM_ADD, nid)
                        
                        # 显示5秒后关闭
                        time.sleep(5)
                        Shell_NotifyIcon(NIM_DELETE, (self.hwnd, 0))
                        win32gui.DestroyWindow(self.hwnd)
                    
                    def OnDestroy(self, hwnd, msg, wparam, lparam):
                        win32gui.PostQuitMessage(0)
                
                WindowsBalloonTip("每日笑话", message)
                
            else:  # Linux/Mac
                os.system(f'notify-send "每日笑话" "{message}"')
                
            print("已发送桌面通知")
            return True
        except Exception as e:
            print(f"发送桌面通知失败: {e}")
            return False
    
    def send_server_chan(self, title, message):
        """使用Server酱发送微信推送"""
        if not self.server_chan_key:
            print("未配置Server酱key，跳过微信推送")
            return False
            
        try:
            url = f"https://sctapi.ftqq.com/{self.server_chan_key}.send"
            data = {
                "title": title,
                "desp": message
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("Server酱推送成功")
                    return True
                else:
                    print(f"Server酱推送失败: {result.get('message')}")
            else:
                print(f"Server酱推送请求失败，状态码: {response.status_code}")
            return False
        except Exception as e:
            print(f"Server酱推送出错: {e}")
            return False
            
    def send_email(self, subject, body):
        """发送邮件"""
        if not (self.email_user and self.email_password and self.email_to):
            print("未配置邮箱信息，跳过邮件推送")
            return False
            
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.header import Header
            
            # 创建邮件
            message = MIMEText(body, 'plain', 'utf-8')
            message['From'] = Header(f"笑话推送 <{self.email_user}>", 'utf-8')
            message['To'] = Header(self.email_to, 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')
            
            # 发送邮件
            if "@qq.com" in self.email_user:
                server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            elif "@163.com" in self.email_user:
                server = smtplib.SMTP_SSL("smtp.163.com", 465)
            elif "@gmail.com" in self.email_user:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            else:
                print(f"未知的邮箱服务提供商: {self.email_user}")
                return False
                
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_user, self.email_to, message.as_string())
            server.quit()
            
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def send_joke(self):
        """发送笑话"""
        joke = self.get_joke_from_api()
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = f"每日笑话 ({date_str})"
        
        # 发送桌面通知
        self.send_desktop_notification(joke)
        
        # 发送微信推送
        self.send_server_chan(title, joke)
        
        # 发送邮件
        self.send_email(title, joke)
        
        print(f"今日笑话: {joke}")
        
    def schedule_job(self, time_str="08:00"):
        """定时发送任务"""
        schedule.every().day.at(time_str).do(self.send_joke)
        print(f"已设置每日 {time_str} 定时发送笑话")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    sender = JokeSender()
    
    # 立即发送一次
    sender.send_joke()
    
    # 设置定时任务
    sender.schedule_job("08:00") 