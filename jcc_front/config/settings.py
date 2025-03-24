"""
基础配置文件
定义配置常量和验证规则
"""
import os
import json
import string
from typing import Dict, Any, List, Tuple
import re

# 默认配置路径
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(os.path.dirname(CONFIG_DIR), "cache")
LOG_DIR = os.path.join(os.path.dirname(CONFIG_DIR), "logs")

# 配置文件路径
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

# 系统盘符列表 (A-Z)
SYSTEM_DRIVES = [f"{drive}:\\" for drive in string.ascii_uppercase]

# MuMu模拟器默认路径模板
MUMU_PATH_TEMPLATE = "Program Files\\Netease\\MuMu Player 12\\shell"

# 生成默认MuMu路径列表
DEFAULT_MUMU_PATHS = [
    os.path.join(drive, MUMU_PATH_TEMPLATE)
    for drive in SYSTEM_DRIVES
]

# 默认配置
DEFAULT_CONFIG = {
    "mumu": {
        "path": "",  # 初始为空，由find_mumu_path函数自动查找
        "adb": {
            "device": "192.168.0.112:5555",
            "timeout": 30,
            "retry_count": 3,
            "retry_interval": 1
        }
    },
    "game": {
        "package": "com.tencent.tmgp.jcc",
        "launch_params": "",
        "auto_restart": False
    },
    "window": {
        "width": 800,
        "height": 600,
        "theme": "dark",
        "language": "zh_CN"
    },
    "emulator": {
        "last_index": 0,
        "settings": {
            "apk_association": "true",
            "app_keptlive": "false",
            "dynamic_adjust_frame_rate": "false",
            "dynamic_low_frame_rate_limit": "15",
            "force_discrete_graphics": "true",
            "gpu_mode": "middle",
            "max_frame_rate": "60",
            "performance_mode": "middle",
            "renderer_mode": "vk",
            "resolution_mode": "tablet.1",
            "root_permission": "false",
            "screen_brightness": "50",
            "show_frame_rate": "false",
            "system_disk_readonly": "true",
            "vertical_sync": "false",
            "window_auto_rotate": "true",
            "window_save_rect": "false",
            "window_size_fixed": "false"
        },
        "performance": {
            "max_concurrent_tasks": 5,
            "thread_pool_size": 10
        }
    },
    "cache": {
        "max_size": 104857600,
        "expire_time": 86400
    },
    "log": {
        "level": "INFO",
        "max_days": 7,
        "max_lines": 1000
    }
}

# 配置验证规则
CONFIG_SCHEMA = {
    "mumu.path": {
        "type": str,
        "required": True,
        "validator": lambda x: os.path.exists(os.path.join(x, "MuMuManager.exe"))
    },
    "mumu.adb.device": {
        "type": str,
        "required": True,
        "pattern": r"^(\d{1,3}\.){3}\d{1,3}:(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})$"
    },
    "mumu.adb.timeout": {
        "type": int,
        "required": True,
        "min": 1,
        "max": 300
    },
    "mumu.adb.retry_count": {
        "type": int,
        "required": True,
        "min": 1,
        "max": 10
    },
    "mumu.adb.retry_interval": {
        "type": int,
        "required": True,
        "min": 1,
        "max": 10
    },
    "mumu.adb.shell_encoding": {
        "type": str,
        "required": True,
        "enum": ["utf-8", "gbk", "gb2312", "ascii"]
    },
    "mumu.adb.default_commands": {
        "type": dict,
        "required": True,
        "validator": lambda x: all(isinstance(k, str) and isinstance(v, str) for k, v in x.items())
    },
    "game.package": {
        "type": str,
        "required": True,
        "pattern": r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*$"
    },
    "game.auto_restart": {
        "type": bool,
        "required": True
    },
    "emulator.last_index": {
        "type": int,
        "required": True,
        "min": 0
    },
    "emulator.performance.max_concurrent_tasks": {
        "type": int,
        "required": True,
        "min": 1,
        "max": 20
    },
    "emulator.performance.thread_pool_size": {
        "type": int,
        "required": True,
        "min": 1,
        "max": 50
    }
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_DAYS = 7

# 图像识别配置
TEMPLATE_THRESHOLD = 0.8
SCREENSHOT_PATH = "screenshot.png"

# 游戏状态定义
GAME_STATES = {
    "MAIN_MENU": "main_menu",
    "IN_GAME": "in_game",
    "SHOP": "shop"
}

# ADB配置
ADB_CONFIG = {
    "TIMEOUT": 30,
    "RETRY_COUNT": 3,
    "RETRY_INTERVAL": 1
}

# UI配置
UI_CONFIG = {
    "REFRESH_INTERVAL": 1000,  # 界面刷新间隔(毫秒)
    "TABLE_ROW_HEIGHT": 30,
    "MAX_LOG_LINES": 1000,
    "THEME": "dark"
}

# 缓存配置
CACHE_CONFIG = {
    "MAX_SIZE": 100 * 1024 * 1024,  # 100MB
    "EXPIRE_TIME": 24 * 60 * 60     # 24小时
}

# 性能配置
PERFORMANCE_CONFIG = {
    "MAX_CONCURRENT_TASKS": 5,
    "THREAD_POOL_SIZE": 10
}

# MuMu模拟器相关常量
MUMU_CONSTANTS = {
    # 命令类型
    "CMD_TYPES": {
        "INFO": "info",
        "CREATE": "create",
        "CLONE": "clone",
        "DELETE": "delete",
        "RENAME": "rename",
        "IMPORT": "import",
        "EXPORT": "export",
        "CONTROL": "control",
        "SETTING": "setting",
        "ADB": "adb",
        "SIMULATION": "simulation"
    },
    
    # 应用状态
    "APP_STATES": {
        "RUNNING": "running",
        "STOPPED": "stopped",
        "NOT_INSTALLED": "not_installed"
    },
    
    # 性能模式
    "PERFORMANCE_MODES": {
        "LOW": "low",
        "MIDDLE": "middle",
        "HIGH": "high"
    },
    
    # 渲染模式
    "RENDER_MODES": {
        "OPENGL": "gl",
        "VULKAN": "vk",
        "DIRECTX": "dx"
    },
    
    # 分辨率预设
    "RESOLUTION_MODES": {
        "PHONE": "phone",
        "TABLET": "tablet.1",
        "CUSTOM": "custom"
    },

    # ADB 命令
    "ADB_COMMANDS": {
        "INPUT_TEXT": "input_text",
        "CONNECT": "connect",
        "DISCONNECT": "disconnect",
        "GET_PROP": "getprop",
        "SET_PROP": "setprop",
        "GO_BACK": "go_back",
        "GO_HOME": "go_home",
        "GO_TASK": "go_task",
        "VOLUME_UP": "volume_up",
        "VOLUME_DOWN": "volume_down",
        "VOLUME_MUTE": "volume_mute",
        "SHELL": "shell"
    }
}

# UI相关常量
UI_CONSTANTS = {
    # 窗口标题
    "WINDOW_TITLES": {
        "MAIN": "JCC模拟器管理工具",
        "INFO": "模拟器信息",
        "CREATE": "创建模拟器",
        "SETTINGS": "设置",
        "ADB": "ADB工具"
    },
    
    # 按钮文本
    "BUTTON_TEXTS": {
        "REFRESH": "刷新",
        "CREATE": "创建",
        "DELETE": "删除",
        "LAUNCH": "启动",
        "SHUTDOWN": "关闭",
        "APPLY": "应用",
        "CANCEL": "取消"
    },
    
    # 标签页名称
    "TAB_NAMES": {
        "MANAGEMENT": "模拟器管理",
        "CONTROL": "模拟器控制",
        "SETTINGS": "配置",
        "ADB": "ADB工具",
        "HARDWARE": "硬件管理"
    },
    
    # 表格列名
    "TABLE_COLUMNS": {
        "EMULATOR_INFO": ["索引", "名称", "状态", "PID", "ADB端口"],
        "APP_INFO": ["包名", "应用名", "版本", "状态"]
    }
}

# 错误代码
ERROR_CODES = {
    "SUCCESS": 0,
    "INVALID_PATH": 1001,
    "LAUNCH_FAILED": 1002,
    "ADB_ERROR": 1003,
    "CONFIG_ERROR": 1004,
    "PERMISSION_ERROR": 1005,
    "NETWORK_ERROR": 1006,
    "UNKNOWN_ERROR": 9999
}

def find_mumu_path() -> str:
    """查找MuMu模拟器安装路径"""
    config = load_config()
    if 'mumu' in config and 'path' in config['mumu'] and os.path.exists(config['mumu']['path']):
        return config['mumu']['path']
    
    for path in DEFAULT_MUMU_PATHS:
        if os.path.exists(path):
            return path
    
    return ""

def get_config() -> Dict[str, Any]:
    """获取配置"""
    config = load_config()
    
    # 验证并设置mumu_path
    if 'mumu' not in config:
        config['mumu'] = {}
    if 'path' not in config['mumu'] or not os.path.exists(config['mumu']['path']):
        mumu_path = find_mumu_path()
        if mumu_path:
            config['mumu']['path'] = mumu_path
            save_config(config)
    
    return config

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证配置是否合法"""
    errors = []
    for path, rules in CONFIG_SCHEMA.items():
        try:
            value = get_nested_value(config, path)
            if not validate_value(value, rules):
                errors.append(f"配置项 {path} 验证失败")
        except KeyError:
            if rules.get("required", False):
                errors.append(f"缺少必需的配置项 {path}")
    
    return len(errors) == 0, errors

def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """获取嵌套字典中的值"""
    keys = path.split('.')
    value = data
    for key in keys:
        value = value[key]
    return value

def validate_value(value: Any, rules: Dict[str, Any]) -> bool:
    """验证单个配置值"""
    if rules.get("required", False) and value is None:
        return False
        
    if "type" in rules and not isinstance(value, rules["type"]):
        return False
        
    if "min" in rules and value < rules["min"]:
        return False
        
    if "max" in rules and value > rules["max"]:
        return False
        
    if "pattern" in rules and not re.match(rules["pattern"], str(value)):
        return False
        
    if "enum" in rules and value not in rules["enum"]:
        return False
        
    if "validator" in rules and not rules["validator"](value):
        return False
        
    return True

def get_config() -> Dict[str, Any]:
    """获取配置"""
    config = load_config()
    
    # 验证并设置mumu_path
    if 'mumu' not in config:
        config['mumu'] = {}
    if 'path' not in config['mumu'] or not os.path.exists(config['mumu']['path']):
        mumu_path = find_mumu_path()
        if mumu_path:
            config['mumu']['path'] = mumu_path
            save_config(config)
    
    return config 