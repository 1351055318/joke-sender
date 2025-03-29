import os
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config

class NotificationSender:
    """负责发送不同类型的通知"""
    
    @staticmethod
    def send_all(title, message):
        """发送所有已配置的通知方式"""
        results = {}
        
        # 桌面通知
        if config.ENABLE_DESKTOP_NOTIFICATION:
            results['desktop'] = NotificationSender.send_desktop_notification(message)
            
        # 微信推送
        if config.ENABLE_WECHAT:
            results['wechat'] = NotificationSender.send_server_chan(title, message)
            
        # 邮件推送
        if config.ENABLE_EMAIL:
            results['email'] = NotificationSender.send_email(title, message)
            
        return results
    
    @staticmethod
    def send_desktop_notification(message):
        """发送桌面通知"""
        try:
            if os.name == "nt":  # Windows
                NotificationSender._send_windows_notification("每日笑话", message)
            else:  # Linux/Mac
                os.system(f'notify-send "每日笑话" "{message}"')
                
            print("已发送桌面通知")
            return True
        except Exception as e:
            print(f"发送桌面通知失败: {e}")
            return False
    
    @staticmethod
    def _send_windows_notification(title, message):
        """发送Windows桌面通知"""
        try:
            from win32api import GetModuleHandle
            from win32gui import Shell_NotifyIcon, NIM_ADD, NIM_DELETE
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
                    
                    # 显示设定时间后关闭
                    time.sleep(config.NOTIFICATION_DURATION)
                    Shell_NotifyIcon(NIM_DELETE, (self.hwnd, 0))
                    win32gui.DestroyWindow(self.hwnd)
                
                def OnDestroy(self, hwnd, msg, wparam, lparam):
                    win32gui.PostQuitMessage(0)
            
            WindowsBalloonTip(title, message)
            return True
        except Exception as e:
            print(f"Windows通知创建失败: {e}")
            return False
    
    @staticmethod
    def send_server_chan(title, message):
        """使用Server酱发送微信推送"""
        if not config.SERVER_CHAN_KEY:
            print("未配置Server酱key，跳过微信推送")
            return False
            
        try:
            url = f"https://sctapi.ftqq.com/{config.SERVER_CHAN_KEY}.send"
            data = {
                "title": title,
                "desp": message
            }
            response = requests.post(url, data=data, timeout=10)
            
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
            
    @staticmethod
    def send_email(subject, body):
        """发送邮件"""
        if not (config.EMAIL_USER and config.EMAIL_PASSWORD and config.EMAIL_TO):
            print("未配置完整邮箱信息，跳过邮件推送")
            return False
            
        try:
            # 创建邮件
            message = MIMEText(body, 'plain', 'utf-8')
            message['From'] = Header(f"笑话推送 <{config.EMAIL_USER}>", 'utf-8')
            message['To'] = Header(config.EMAIL_TO, 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')
            
            # 根据邮箱类型选择服务器
            if "@qq.com" in config.EMAIL_USER:
                server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            elif "@163.com" in config.EMAIL_USER:
                server = smtplib.SMTP_SSL("smtp.163.com", 465)
            elif "@gmail.com" in config.EMAIL_USER:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            else:
                print(f"未知的邮箱服务提供商: {config.EMAIL_USER}")
                return False
                
            # 登录并发送
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USER, config.EMAIL_TO, message.as_string())
            server.quit()
            
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False 