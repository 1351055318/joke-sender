from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
import os
import json
from datetime import datetime

from joke_fetcher import JokeFetcher
from notification_sender import NotificationSender
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

# 初始化调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 历史记录文件
HISTORY_FILE = "joke_history.json"

def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
    return []

def save_history(joke, title):
    """保存历史记录"""
    history = load_history()
    history.append({
        "joke": joke,
        "title": title,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # 只保留最近50条记录
    if len(history) > 50:
        history = history[-50:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存历史记录失败: {e}")

def send_joke_task():
    """定时任务：发送笑话"""
    joke = JokeFetcher.get_joke()
    title = JokeFetcher.get_joke_title()
    
    # 发送通知
    NotificationSender.send_all(title, joke)
    
    # 保存到历史记录
    save_history(joke, title)
    
    return joke, title

# 注入当前年份到所有模板
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# 路由：首页
@app.route('/')
def index():
    # 加载历史记录
    history = load_history()
    # 反转顺序，最新的在前
    history.reverse()
    
    # 获取当前定时任务信息
    jobs = scheduler.get_jobs()
    next_run = None
    if jobs:
        for job in jobs:
            if job.id == "send_joke_job":
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                break
    
    return render_template(
        'index.html', 
        history=history, 
        next_run=next_run,
        server_chan_key=config.SERVER_CHAN_KEY,
        config=config
    )

# 路由：立即发送
@app.route('/send_now', methods=['POST'])
def send_now():
    joke, title = send_joke_task()
    flash(f"已发送笑话: {joke}", "success")
    return redirect(url_for('index'))

# 路由：设置定时
@app.route('/schedule', methods=['POST'])
def schedule():
    time_str = request.form.get('time', '08:00')
    
    # 移除现有的定时任务
    for job in scheduler.get_jobs():
        if job.id == "send_joke_job":
            scheduler.remove_job(job.id)
    
    # 添加新的定时任务
    scheduler.add_job(
        send_joke_task, 
        'cron', 
        hour=int(time_str.split(':')[0]),
        minute=int(time_str.split(':')[1]),
        id="send_joke_job"
    )
    
    flash(f"已设置每日 {time_str} 发送笑话", "success")
    return redirect(url_for('index'))

# 路由：更新配置
@app.route('/settings', methods=['POST'])
def update_settings():
    # 获取表单数据
    server_chan_key = request.form.get('server_chan_key', '')
    email_user = request.form.get('email_user', '')
    email_password = request.form.get('email_password', '')
    email_to = request.form.get('email_to', '')
    
    # 更新环境变量
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"SERVER_CHAN_KEY={server_chan_key}\n")
        f.write(f"EMAIL_USER={email_user}\n")
        f.write(f"EMAIL_PASSWORD={email_password}\n")
        f.write(f"EMAIL_TO={email_to}\n")
    
    # 重新加载配置
    os.environ["SERVER_CHAN_KEY"] = server_chan_key
    os.environ["EMAIL_USER"] = email_user
    os.environ["EMAIL_PASSWORD"] = email_password
    os.environ["EMAIL_TO"] = email_to
    
    # 刷新配置模块
    import importlib
    importlib.reload(config)
    
    flash("配置已更新", "success")
    return redirect(url_for('index'))

# API路由：获取随机笑话
@app.route('/api/joke', methods=['GET'])
def api_joke():
    joke = JokeFetcher.get_joke()
    return jsonify({"joke": joke})

# 启动定时任务（如果未设置）
@app.before_first_request
def init_scheduler():
    jobs = scheduler.get_jobs()
    if not any(job.id == "send_joke_job" for job in jobs):
        # 默认设置为每天早上8点
        scheduler.add_job(
            send_joke_task, 
            'cron', 
            hour=8, 
            minute=0,
            id="send_joke_job"
        )
        print("已设置默认定时任务：每天 08:00")

if __name__ == '__main__':
    # 确保环境变量文件存在
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write("SERVER_CHAN_KEY=\n")
            f.write("EMAIL_USER=\n")
            f.write("EMAIL_PASSWORD=\n")
            f.write("EMAIL_TO=\n")
            f.write("TIANXING_API_KEY=\n")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True) 