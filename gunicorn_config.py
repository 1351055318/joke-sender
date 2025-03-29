import multiprocessing

# 绑定的IP和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 最大请求数
max_requests = 1000

# 超时时间
timeout = 30

# 是否后台运行
daemon = False

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info" 