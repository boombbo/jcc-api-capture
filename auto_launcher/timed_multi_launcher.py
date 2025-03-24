"""
定时多实例启动器 (Timed Multi-Instance Launcher)

功能说明：
1. 与迪士尼服务器校准时间
2. 在指定时间(默认11:45)准时并发启动多个程序实例
3. 在同一终端窗口集中查看所有实例的实时输出
4. 支持ESC键快速退出所有实例

使用方法：
python timed_multi_launcher.py [--instances 10] [--time 11:45] [--exe wuyanzhengma.exe] [--params "参数"]

参数说明：
--instances: 要启动的实例数量，默认10个
--time: 启动时间，格式为HH:MM，默认11:45
--exe: 要启动的可执行文件名称，默认wuyanzhengma.exe
--params: 启动参数
--now: 立即启动，不等待指定时间
--no-sync: 不与服务器同步时间，使用本地系统时间
"""

import os
import sys
import time
import logging
import argparse
import subprocess
import threading
import signal
import queue
import datetime
import requests
import re
from typing import List, Dict, Optional, Tuple, Any
import colorama
from colorama import Fore, Style

# 尝试导入pytz，用于时区处理
try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    print("警告: 未安装pytz库，将使用本地时区")

# 尝试导入keyboard库，用于监听ESC键
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("警告: 未安装keyboard库，ESC键退出功能不可用")

# 初始化colorama
colorama.init()

# 全局变量
EXIT_FLAG = False
PROCESSES = []
OUTPUT_QUEUES = []
INSTANCE_COLORS = [
    Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, 
    Fore.BLUE, Fore.RED, Fore.WHITE, 
    Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX,
    Fore.LIGHTRED_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX
]

# 设置日志
def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'timed_multi_launcher_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"日志文件: {log_file}")
    return log_file

# 监听ESC键
def listen_for_esc_key():
    global EXIT_FLAG
    if not KEYBOARD_AVAILABLE:
        print("未安装keyboard库，ESC键退出功能不可用")
        return
    
    try:
        print(f"{Fore.YELLOW}ESC键监听已启动，按ESC键可随时退出程序{Style.RESET_ALL}")
        keyboard.wait('esc')
        EXIT_FLAG = True
        print(f"\n{Fore.RED}[ESC] 正在安全退出所有程序，请稍候...{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}键盘监听出错: {str(e)}{Style.RESET_ALL}")

# 从迪士尼服务器获取时间
def get_server_time(retries: int = 3, timeout: int = 20) -> Optional[datetime.datetime]:
    """
    从迪士尼服务器获取准确时间
    
    Args:
        retries: 重试次数
        timeout: 超时时间(秒)
    
    Returns:
        datetime.datetime: 服务器时间，获取失败则返回None
    """
    url = "https://www.hongkongdisneyland.com"
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    
    for attempt in range(retries):
        try:
            print(f"{Fore.CYAN}尝试使用代理获取服务器时间... (尝试 {attempt + 1}/{retries}){Style.RESET_ALL}")
            response = requests.head(url, proxies=proxies, timeout=timeout)
            server_time = response.headers.get('Date')
            
            if server_time:
                # RFC标准时间格式: Wed, 05 Jan 2022 12:34:56 GMT
                # 尝试解析Date头
                if PYTZ_AVAILABLE:
                    server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                    server_time = server_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Hong_Kong'))
                else:
                    # 如果没有pytz，简单地转换为本地时间
                    server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                    # 假设GMT+8
                    server_time = server_time + datetime.timedelta(hours=8)
                return server_time
            else:
                print(f"{Fore.YELLOW}无法通过代理获取服务器时间，尝试使用系统默认网络...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}使用代理获取服务器时间时发生错误: {str(e)}{Style.RESET_ALL}")
        
        # 尝试使用系统默认网络
        try:
            print(f"{Fore.CYAN}切换到系统默认网络... (尝试 {attempt + 1}/{retries}){Style.RESET_ALL}")
            response = requests.head(url, timeout=timeout)
            server_time = response.headers.get('Date')
            
            if server_time:
                if PYTZ_AVAILABLE:
                    server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                    server_time = server_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Hong_Kong'))
                else:
                    # 如果没有pytz，简单地转换为本地时间
                    server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                    # 假设GMT+8
                    server_time = server_time + datetime.timedelta(hours=8)
                return server_time
            else:
                print(f"{Fore.YELLOW}无法获取服务器时间{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}使用系统默认网络获取服务器时间时发生错误: {str(e)}{Style.RESET_ALL}")
        
        time.sleep(5)  # 等待几秒钟后重试
    
    print(f"{Fore.RED}多次尝试后仍无法获取服务器时间{Style.RESET_ALL}")
    return None

# 同步服务器时间
def synchronize_with_server_time(server_time: datetime.datetime) -> datetime.datetime:
    """
    将本地时间与服务器时间同步
    
    Args:
        server_time: 服务器时间
    
    Returns:
        datetime.datetime: 同步后的本地时间
    """
    if PYTZ_AVAILABLE:
        now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    else:
        now = datetime.datetime.now()
    
    time_difference = (server_time - now).total_seconds()

    if abs(time_difference) > 0.001:
        print(f"{Fore.CYAN}本地时间与服务器时间相差 {time_difference:.6f} 秒{Style.RESET_ALL}")
        if time_difference > 0:
            # 如果服务器时间比本地时间快，等待追赶
            target_time = time.perf_counter() + time_difference
            while time.perf_counter() < target_time:
                pass
        print(f"{Fore.GREEN}时间已校准{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}本地时间与服务器时间基本同步{Style.RESET_ALL}")

    if PYTZ_AVAILABLE:
        return datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    else:
        return datetime.datetime.now()

# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description='定时多实例启动器 - 在指定时间准时启动多个程序实例，并集中监控输出')
    parser.add_argument('--instances', type=int, default=10, help='要启动的实例数量 (默认: 10)')
    parser.add_argument('--time', type=str, default='11:45', help='启动时间，格式为HH:MM (默认: 11:45)')
    parser.add_argument('--exe', type=str, default='wuyanzhengma.exe', help='要启动的可执行文件名称 (默认: wuyanzhengma.exe)')
    parser.add_argument('--params', type=str, default='', help='启动参数')
    parser.add_argument('--now', action='store_true', help='立即启动，不等待指定时间')
    parser.add_argument('--no-sync', action='store_true', help='不与服务器同步时间，使用本地系统时间')
    parser.add_argument('--no-keyboard', action='store_true', help='禁用键盘监听（ESC键退出功能）')
    return parser.parse_args()

# 读取进程输出并将其放入队列
def reader_thread(pipe, queue, instance_id):
    try:
        while True:
            line = pipe.readline()
            if not line:
                break
            queue.put((instance_id, line.decode('utf-8', errors='replace').rstrip()))
    except Exception as e:
        queue.put((instance_id, f"[错误] 读取输出时出错: {str(e)}"))
    finally:
        pipe.close()

# 创建多个进程实例
def create_instances(exe_path: str, instances: int, launch_params: str) -> List[subprocess.Popen]:
    processes = []
    output_queues = []
    
    print(f"{Fore.CYAN}正在创建{instances}个进程实例...{Style.RESET_ALL}")
    
    cmd_base = [exe_path] + (launch_params.split() if launch_params else [])
    
    for i in range(instances):
        try:
            # 使用PIPE模式捕获输出
            process = subprocess.Popen(
                cmd_base,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            processes.append(process)
            
            # 为每个进程创建输出队列
            output_queue = queue.Queue()
            output_queues.append(output_queue)
            
            # 为stdout和stderr创建读取线程
            stdout_thread = threading.Thread(
                target=reader_thread, 
                args=(process.stdout, output_queue, i)
            )
            stderr_thread = threading.Thread(
                target=reader_thread, 
                args=(process.stderr, output_queue, i)
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            print(f"{INSTANCE_COLORS[i % len(INSTANCE_COLORS)]}实例 #{i+1} 已启动 (PID: {process.pid}){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}启动实例 #{i+1} 失败: {str(e)}{Style.RESET_ALL}")
    
    return processes, output_queues

# 显示进程输出
def display_output(output_queues: List[queue.Queue], processes: List[subprocess.Popen]):
    print(f"\n{Fore.GREEN}======== 所有实例已启动，开始监控输出 ========{Style.RESET_ALL}")
    
    while not EXIT_FLAG and any(p.poll() is None for p in processes):
        for i, q in enumerate(output_queues):
            try:
                # 非阻塞方式获取输出
                while not q.empty():
                    instance_id, line = q.get_nowait()
                    color = INSTANCE_COLORS[instance_id % len(INSTANCE_COLORS)]
                    print(f"{color}[实例 #{instance_id+1}] {line}{Style.RESET_ALL}")
            except queue.Empty:
                pass
            except Exception as e:
                print(f"{Fore.RED}处理输出时出错: {str(e)}{Style.RESET_ALL}")
        
        time.sleep(0.1)  # 短暂休眠，避免CPU占用过高
    
    # 检查是哪些进程已经结束
    for i, process in enumerate(processes):
        if process.poll() is not None:
            print(f"{Fore.YELLOW}实例 #{i+1} (PID: {process.pid}) 已结束，退出代码: {process.poll()}{Style.RESET_ALL}")

# 清理所有进程
def cleanup_all_processes():
    print(f"{Fore.YELLOW}正在终止所有进程...{Style.RESET_ALL}")
    
    for i, process in enumerate(PROCESSES):
        try:
            if process.poll() is None:  # 如果进程仍在运行
                process.terminate()
                try:
                    # 等待进程终止，最多5秒
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 如果超时，强制终止
                    process.kill()
                print(f"{Fore.YELLOW}已终止实例 #{i+1} (PID: {process.pid}){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}终止实例 #{i+1} 失败: {str(e)}{Style.RESET_ALL}")
            try:
                process.kill()
            except:
                pass
    
    print(f"{Fore.GREEN}所有进程已清理完成{Style.RESET_ALL}")

# 等待直到指定时间
def wait_until_time(target_time_str: str, sync_with_server: bool = True) -> None:
    """
    等待直到指定时间
    
    Args:
        target_time_str: 目标时间，格式为HH:MM
        sync_with_server: 是否与服务器同步时间
    """
    hour, minute = map(int, target_time_str.split(':'))
    
    if sync_with_server:
        print(f"{Fore.CYAN}开始与迪士尼服务器同步时间...{Style.RESET_ALL}")
        
        while True:
            server_time = get_server_time()
            if not server_time:
                print(f"{Fore.YELLOW}无法获取服务器时间，30秒后重试...{Style.RESET_ALL}")
                time.sleep(30)
                continue
                
            print(f"{Fore.GREEN}服务器时间: {server_time}{Style.RESET_ALL}")
            precise_time = synchronize_with_server_time(server_time)
            print(f"{Fore.GREEN}校准后的本地时间: {precise_time}{Style.RESET_ALL}")
            
            # 构建今天的目标时间
            if PYTZ_AVAILABLE:
                target_time = precise_time.replace(
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0
                )
            else:
                target_time = datetime.datetime(
                    precise_time.year,
                    precise_time.month,
                    precise_time.day,
                    hour,
                    minute,
                    0,
                    0
                )
            
            # 如果目标时间已过，设置为明天
            if target_time < precise_time:
                target_time = target_time + datetime.timedelta(days=1)
            
            # 计算时间差(秒)
            time_diff = (target_time - precise_time).total_seconds()
            
            # 如果距离目标时间还有超过5分钟，每30秒同步一次服务器时间
            if time_diff > 300:
                # 计算剩余时间的小时、分钟和秒
                hours = int(time_diff // 3600)
                minutes = int((time_diff % 3600) // 60)
                seconds = int(time_diff % 60)
                
                # 构建倒计时显示文本
                countdown_text = f"{Fore.CYAN}倒计时: "
                if hours > 0:
                    countdown_text += f"{hours}时 "
                if minutes > 0:
                    countdown_text += f"{minutes}分 "
                countdown_text += f"{seconds}秒{Style.RESET_ALL}"
                
                print(f"\r{countdown_text}", end='', flush=True)
                print(f"\n{Fore.CYAN}距离目标时间还有 {int(time_diff)} 秒 ({int(time_diff/60)} 分钟)，继续同步服务器时间...{Style.RESET_ALL}")
                time.sleep(30)
                continue
                
            # 如果距离目标时间不到5分钟，进入精确倒计时
            print(f"\n{Fore.GREEN}进入精确倒计时阶段...{Style.RESET_ALL}")
            
            # 倒计时直到目标时间前0.5秒
            while True:
                if EXIT_FLAG:
                    print(f"\n{Fore.YELLOW}倒计时已取消{Style.RESET_ALL}")
                    return
                
                if PYTZ_AVAILABLE:
                    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                else:
                    now = datetime.datetime.now()
                
                time_diff = (target_time - now).total_seconds()
                
                if time_diff <= 0.5:
                    print(f"\n{Fore.GREEN}时间到！开始启动实例...{Style.RESET_ALL}")
                    return
                
                # 计算剩余时间的小时、分钟和秒
                hours = int(time_diff // 3600)
                minutes = int((time_diff % 3600) // 60)
                seconds = int(time_diff % 60)
                
                # 构建倒计时显示文本
                countdown_text = f"{Fore.CYAN}倒计时: "
                if hours > 0:
                    countdown_text += f"{hours}时 "
                if minutes > 0:
                    countdown_text += f"{minutes}分 "
                countdown_text += f"{seconds}秒{Style.RESET_ALL}"
                
                print(f"\r{countdown_text}", end='', flush=True)
                time.sleep(0.1)
    else:
        # 不与服务器同步，使用本地时间
        now = datetime.datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # 如果目标时间已过，设置为明天
        if target_time < now:
            target_time = target_time + datetime.timedelta(days=1)
        
        # 计算时间差(秒)
        time_diff = (target_time - now).total_seconds()
        
        print(f"{Fore.CYAN}使用本地时间，目标启动时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}距离目标时间还有 {int(time_diff)} 秒 ({int(time_diff/60)} 分钟){Style.RESET_ALL}")
        
        # 如果时间差大于5分钟，每分钟更新一次倒计时
        if time_diff > 300:
            update_interval = 60  # 每分钟更新一次
        else:
            update_interval = 1  # 每秒更新一次
        
        start_time = time.time()
        last_update = 0
        
        while True:
            if EXIT_FLAG:
                print(f"\n{Fore.YELLOW}倒计时已取消{Style.RESET_ALL}")
                return
            
            elapsed = time.time() - start_time
            remaining = time_diff - elapsed
            
            if remaining <= 0.5:
                print(f"\n{Fore.GREEN}时间到！开始启动实例...{Style.RESET_ALL}")
                return
            
            # 定期更新倒计时
            current_update = int(remaining / update_interval)
            if current_update != last_update:
                last_update = current_update
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                seconds = int(remaining % 60)
                
                # 构建倒计时显示文本
                countdown_text = f"{Fore.CYAN}倒计时: "
                if hours > 0:
                    countdown_text += f"{hours}时 "
                if minutes > 0:
                    countdown_text += f"{minutes}分 "
                countdown_text += f"{seconds}秒{Style.RESET_ALL}"
                
                print(f"\r{countdown_text}", end='', flush=True)
            
            time.sleep(0.1)

# 主函数
def main():
    global PROCESSES, OUTPUT_QUEUES, EXIT_FLAG
    
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志
    log_file = setup_logging()
    
    # 启动ESC键监听线程
    if KEYBOARD_AVAILABLE and not args.no_keyboard:
        esc_thread = threading.Thread(target=listen_for_esc_key)
        esc_thread.daemon = True
        esc_thread.start()
    
    # 注册信号处理器
    def signal_handler(sig, frame):
        global EXIT_FLAG
        EXIT_FLAG = True
        print(f"\n{Fore.RED}收到中断信号，正在安全退出...{Style.RESET_ALL}")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 验证exe文件是否存在
        exe_path = os.path.join(os.getcwd(), args.exe)
        if not os.path.exists(exe_path):
            print(f"{Fore.RED}找不到目标程序: {exe_path}{Style.RESET_ALL}")
            return 1
        
        print(f"{Fore.GREEN}=============== 定时多实例启动器 ==============={Style.RESET_ALL}")
        print(f"{Fore.CYAN}目标程序: {args.exe}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}启动实例数: {args.instances}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}启动参数: {args.params}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}日志文件: {log_file}{Style.RESET_ALL}")
        
        # 是否立即启动
        if args.now:
            print(f"{Fore.YELLOW}使用立即启动模式，跳过倒计时{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}目标启动时间: {args.time}{Style.RESET_ALL}")
            # 等待直到指定时间
            wait_until_time(args.time, not args.no_sync)
            if EXIT_FLAG:
                print(f"{Fore.YELLOW}启动已取消{Style.RESET_ALL}")
                return 0
        
        # 创建并启动实例
        print(f"{Fore.GREEN}准备启动 {args.instances} 个 {args.exe} 实例...{Style.RESET_ALL}")
        PROCESSES, OUTPUT_QUEUES = create_instances(exe_path, args.instances, args.params)
        
        # 监控并显示输出
        display_output(OUTPUT_QUEUES, PROCESSES)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}收到键盘中断，正在退出...{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}运行时错误: {str(e)}{Style.RESET_ALL}")
    finally:
        # 清理所有进程
        cleanup_all_processes()
    
    print(f"{Fore.GREEN}程序已安全退出{Style.RESET_ALL}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
