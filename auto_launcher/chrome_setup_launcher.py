#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chrome安装启动器

该模块用于自动安装Chrome浏览器并启动定时启动器程序。
功能包括：
1. 检查系统是否已安装Chrome浏览器
2. 如果未安装，自动运行ChromeSetup.exe进行安装
3. 安装完成后自动启动timer_launcher_ui.py（图形界面版）
4. 或根据需要启动timed_multi_launcher.py（命令行版）

使用方法：
python chrome_setup_launcher.py [--ui] [--multi] [--wait-time <秒>]

参数说明：
--ui: 安装后启动图形界面版(timer_launcher_ui.py)
--multi: 安装后启动命令行版(timed_multi_launcher.py)
--wait-time: 等待安装完成的最长时间(秒)，默认300秒
"""

import os
import sys
import time
import subprocess
import argparse
import logging
import winreg
import threading
import psutil
from typing import Optional, List, Tuple

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# 是否正在运行标志
RUNNING = True

def check_chrome_installed() -> bool:
    """
    检查系统是否已安装Chrome浏览器
    
    Returns:
        bool: 如果已安装返回True，否则返回False
    """
    try:
        # 方法1: 检查注册表
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                chrome_path = winreg.QueryValue(key, None)
                if os.path.exists(chrome_path):
                    logging.info(f"通过注册表找到Chrome: {chrome_path}")
                    return True
        except FileNotFoundError:
            pass
        
        # 方法2: 检查默认安装目录
        default_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), "Google\\Chrome\\Application\\chrome.exe")
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                logging.info(f"在默认位置找到Chrome: {path}")
                return True
        
        logging.info("未找到Chrome安装")
        return False
    except Exception as e:
        logging.error(f"检查Chrome安装时出错: {str(e)}")
        return False

def run_chrome_setup() -> subprocess.Popen:
    """
    运行ChromeSetup.exe安装Chrome浏览器
    
    Returns:
        subprocess.Popen: 安装进程对象
    """
    try:
        # 获取ChromeSetup.exe的完整路径
        setup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ChromeSetup.exe")
        if not os.path.exists(setup_path):
            raise FileNotFoundError(f"找不到Chrome安装程序: {setup_path}")
        
        logging.info(f"开始运行Chrome安装程序: {setup_path}")
        
        # 静默安装参数
        # /silent - 静默安装，不显示任何界面
        # /install - 安装模式
        process = subprocess.Popen(
            [setup_path, "/silent", "/install"],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        logging.info(f"Chrome安装程序已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        logging.error(f"运行Chrome安装程序时出错: {str(e)}")
        raise

def monitor_installation(process: subprocess.Popen, max_wait_time: int = 300) -> bool:
    """
    监控Chrome安装进程
    
    Args:
        process: 安装进程对象
        max_wait_time: 最大等待时间(秒)
    
    Returns:
        bool: 安装是否成功
    """
    global RUNNING
    
    start_time = time.time()
    logging.info(f"开始监控Chrome安装进程，最长等待{max_wait_time}秒")
    
    # 显示进度条
    progress_thread = threading.Thread(target=show_progress, args=(max_wait_time,))
    progress_thread.daemon = True
    progress_thread.start()
    
    while RUNNING and (time.time() - start_time) < max_wait_time:
        # 检查进程是否还在运行
        if process.poll() is not None:
            exit_code = process.returncode
            logging.info(f"Chrome安装程序已结束，退出代码: {exit_code}")
            
            # 检查是否安装成功
            if exit_code == 0 or check_chrome_installed():
                RUNNING = False
                return True
            else:
                RUNNING = False
                return False
        
        # 检查Chrome进程是否已经启动（说明安装快结束了）
        chrome_processes = [p for p in psutil.process_iter(['name']) if p.info['name'] == 'chrome.exe']
        if chrome_processes:
            logging.info("检测到Chrome进程已启动")
            
            # 等待几秒让Chrome初始化
            time.sleep(5)
            
            # 关闭所有Chrome窗口
            for p in chrome_processes:
                try:
                    p.terminate()
                except:
                    pass
            
            RUNNING = False
            return True
        
        time.sleep(1)
    
    # 如果超时
    if time.time() - start_time >= max_wait_time:
        logging.warning(f"Chrome安装超时（{max_wait_time}秒）")
        
        # 尝试终止安装进程
        try:
            process.terminate()
        except:
            pass
    
    RUNNING = False
    return check_chrome_installed()

def show_progress(total_time: int):
    """
    显示安装进度条
    
    Args:
        total_time: 总时间(秒)
    """
    start_time = time.time()
    
    while RUNNING:
        elapsed = time.time() - start_time
        if elapsed > total_time:
            break
            
        progress = int((elapsed / total_time) * 100)
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r安装进度: |{bar}| {progress}% ')
        sys.stdout.flush()
        
        time.sleep(0.5)
    
    sys.stdout.write('\n')
    sys.stdout.flush()

def launch_timer_ui() -> subprocess.Popen:
    """
    启动图形界面版定时启动器
    
    Returns:
        subprocess.Popen: 启动的进程对象
    """
    try:
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timer_launcher_ui.py")
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"找不到图形界面启动器: {ui_path}")
        
        logging.info(f"启动图形界面版定时启动器: {ui_path}")
        
        # 启动进程
        process = subprocess.Popen(
            [sys.executable, ui_path],
            shell=True
        )
        
        logging.info(f"图形界面启动成功 (PID: {process.pid})")
        return process
    except Exception as e:
        logging.error(f"启动图形界面版定时启动器时出错: {str(e)}")
        raise

def launch_timed_multi() -> subprocess.Popen:
    """
    启动命令行版多实例定时启动器
    
    Returns:
        subprocess.Popen: 启动的进程对象
    """
    try:
        multi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timed_multi_launcher.py")
        if not os.path.exists(multi_path):
            raise FileNotFoundError(f"找不到命令行版启动器: {multi_path}")
        
        logging.info(f"启动命令行版多实例定时启动器: {multi_path}")
        
        # 启动进程
        process = subprocess.Popen(
            [sys.executable, multi_path],
            shell=True
        )
        
        logging.info(f"命令行版启动成功 (PID: {process.pid})")
        return process
    except Exception as e:
        logging.error(f"启动命令行版多实例定时启动器时出错: {str(e)}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Chrome安装启动器 - 安装Chrome并启动定时启动器')
    parser.add_argument('--ui', action='store_true', help='安装后启动图形界面版(timer_launcher_ui.py)')
    parser.add_argument('--multi', action='store_true', help='安装后启动命令行版(timed_multi_launcher.py)')
    parser.add_argument('--wait-time', type=int, default=300, help='等待安装完成的最长时间(秒)，默认300秒')
    args = parser.parse_args()
    
    # 如果没有指定启动选项，默认启动图形界面版
    if not args.ui and not args.multi:
        args.ui = True
    
    try:
        # 检查Chrome是否已安装
        if check_chrome_installed():
            logging.info("Chrome已安装，跳过安装步骤")
        else:
            # 运行安装程序
            try:
                process = run_chrome_setup()
                success = monitor_installation(process, args.wait_time)
                
                if not success:
                    logging.error("Chrome安装失败")
                    return 1
                
                logging.info("Chrome安装成功")
            except Exception as e:
                logging.error(f"Chrome安装过程出错: {str(e)}")
                return 1
        
        # 启动定时启动器
        if args.ui:
            ui_process = launch_timer_ui()
        
        if args.multi:
            multi_process = launch_timed_multi()
        
        logging.info("所有程序已成功启动")
        return 0
        
    except KeyboardInterrupt:
        logging.info("\n操作被用户中断")
        return 1
    except Exception as e:
        logging.error(f"运行过程中出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
