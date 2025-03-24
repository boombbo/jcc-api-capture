#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定时启动器默认配置
"""

import os
from datetime import time

# 基本配置
DEFAULT_CONFIG = {
    # 程序执行文件
    "exe_path": "wuyanzhengma.exe",
    
    # 启动参数（默认为空）
    "launch_params": "",
    
    # 默认实例数量
    "instances": 10,
    
    # 默认启动时间（11:45:00）
    "default_hour": 11,
    "default_minute": 45,
    "default_second": 0,
    
    # 是否立即启动（默认否）
    "launch_now": False,
    
    # 是否同步服务器时间（默认是）
    "sync_server_time": True,
    
    # 时间显示格式（Qt格式）
    "time_format": "yyyy-MM-dd HH:mm:ss",
    
    # 日志配置
    "log_level": "INFO",
    "log_to_file": False,
    "log_file_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "launcher.log"),
    
    # UI配置
    "window_width": 800,
    "window_height": 600,
    "default_theme": "dark_teal.xml"  # Material主题
}

# 主题选项
AVAILABLE_THEMES = [
    "dark_teal.xml",
    "dark_blue.xml",
    "dark_pink.xml",
    "light_blue.xml",
    "light_cyan.xml",
    "light_cyan_500.xml",
    "light_red.xml"
]

# 预设启动时间（快速选择）
PRESET_TIMES = [
    {"label": "9:00", "hour": 9, "minute": 0, "second": 0},
    {"label": "11:45", "hour": 11, "minute": 45, "second": 0},
    {"label": "12:00", "hour": 12, "minute": 0, "second": 0},
    {"label": "15:00", "hour": 15, "minute": 0, "second": 0},
    {"label": "18:00", "hour": 18, "minute": 0, "second": 0}
]

# 用户配置文件路径
USER_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_config.json") 
