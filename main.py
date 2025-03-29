import schedule
import time
import config
from joke_fetcher import JokeFetcher
from notification_sender import NotificationSender

def send_joke():
    """获取并发送笑话"""
    # 获取笑话内容
    joke = JokeFetcher.get_joke()
    title = JokeFetcher.get_joke_title()
    
    # 输出到控制台
    print(f"\n{title}\n{'-' * 30}\n{joke}\n{'-' * 30}")
    
    # 发送通知
    results = NotificationSender.send_all(title, joke)
    
    # 返回发送结果状态
    return any(results.values())

def start_scheduler(time_str=None):
    """启动定时任务"""
    # 使用配置的时间或者默认时间
    push_time = time_str or config.DEFAULT_PUSH_TIME
    
    # 设置每日定时任务
    schedule.every().day.at(push_time).do(send_joke)
    print(f"已设置每日 {push_time} 定时发送笑话")
    
    # 运行调度程序
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    import argparse
    
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="每日笑话/土味情话推送工具")
    parser.add_argument("--now", action="store_true", help="立即发送一条笑话")
    parser.add_argument("--time", type=str, help="设置每日推送时间，格式如 08:00")
    args = parser.parse_args()
    
    # 初始化提示
    print("===== 每日笑话/土味情话推送 =====")
    
    # 立即发送一条
    if args.now:
        print("立即发送一条笑话...")
        send_joke()
    
    # 启动定时任务
    start_scheduler(args.time) 