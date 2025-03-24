#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定时启动器图形界面 (Timed Launcher UI)

功能说明：
1. 图形化界面设置程序启动时间和并发实例数量
2. 倒计时显示距离程序启动的剩余时间
3. 统一实时监控所有启动实例的日志输出
4. 支持启动、停止、重置等操作

使用方法：
python timer_launcher_ui.py
"""

import os
import sys
import time
import datetime
import subprocess
import threading
import queue
import logging
import json
from typing import List, Dict, Optional, Tuple
import signal
import ctypes
from ctypes import wintypes
import win32api
import win32con

# 导入Chrome安装器模块
try:
    from chrome_setup_launcher import check_chrome_installed, run_chrome_setup, monitor_installation
    HAS_CHROME_SETUP = True
except ImportError:
    logging.warning("无法导入Chrome安装器模块，Chrome安装检查功能将不可用")
    HAS_CHROME_SETUP = False

# 导入pytz用于时区处理
try:
    import pytz
    import requests
    from requests.exceptions import RequestException
    HAS_PYTZ = True
except ImportError:
    logging.warning("无法导入pytz或requests模块，时间同步功能可能受限")
    HAS_PYTZ = False

# 导入默认配置
try:
    from default_config import DEFAULT_CONFIG, PRESET_TIMES, AVAILABLE_THEMES, USER_CONFIG_PATH
    HAS_DEFAULT_CONFIG = True
except ImportError:
    logging.warning("无法导入默认配置，将使用硬编码默认值")
    DEFAULT_CONFIG = {
        "exe_path": "wuyanzhengma.exe",
        "instances": 10,
        "default_time": "11:45",  # 修改为字符串格式的时间
        "launch_now": False,
        "sync_server_time": True,
        "time_format": "HH:mm",   # 修改为简单的时间格式
        "default_theme": "dark_teal.xml"
    }
    HAS_DEFAULT_CONFIG = False

# 统一设置环境变量，确保所有子进程使用UTF-8编码
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# 设置应用程序DPI自适应
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
# 设置为自适应DPI但不是自动缩放
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_FONT_DPI"] = "96"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QTextEdit, QGroupBox,
    QGridLayout, QTimeEdit, QDateTimeEdit, QSplitter, QProgressBar,
    QCheckBox, QComboBox, QFileDialog, QMessageBox, QMenu, QSlider, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDateTime, pyqtSignal, QProcess, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QTextCursor, QIcon, QTextCharFormat, QFontDatabase, QAction
from qt_material import apply_stylesheet, QtStyleTools

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],  # 确保日志输出到标准输出
    encoding="utf-8"  # 显式指定编码
)

# 确保Qt应用程序正确处理中文
def setup_ui_environment():
    """设置UI环境，确保正确处理中文"""
    # 设置标准字体列表
    chinese_fonts = [
        "Microsoft YaHei", 
        "微软雅黑", 
        "SimHei", 
        "黑体", 
        "SimSun", 
        "宋体", 
        "NSimSun", 
        "新宋体"
    ]
    
    # 注册系统字体
    try:
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyh.ttc")  # 微软雅黑
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyhbd.ttc")  # 微软雅黑粗体
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/simhei.ttf")  # 黑体
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/simsun.ttc")  # 宋体
    except Exception as e:
        logging.warning(f"无法加载系统字体: {str(e)}")
    
    # 注册所有可用字体
    all_fonts = QFontDatabase.families()
    available_chinese_fonts = []
    
    for font in chinese_fonts:
        if font in all_fonts:
            available_chinese_fonts.append(font)
    
    if available_chinese_fonts:
        logging.info(f"找到可用的中文字体: {', '.join(available_chinese_fonts)}")
        # 始终返回微软雅黑，如果可用
        if "Microsoft YaHei" in available_chinese_fonts:
            return "Microsoft YaHei"
        else:
            return available_chinese_fonts[0]  # 返回其他可用的中文字体
    else:
        logging.warning("未找到支持中文的字体，将使用系统默认字体")
        return "Microsoft YaHei"  # 尽量还是使用微软雅黑

class LogMonitor(QTextEdit):
    """日志监控组件，用于显示和高亮不同实例的日志"""
    
    def __init__(self, font_name=""):
        super().__init__()
        self.setReadOnly(True)
        
        # 使用支持中文的字体
        if font_name:
            self.setFont(QFont(font_name, 10))
        else:
            self.setFont(QFont("Microsoft YaHei", 10))
        
        # 设置文本编码和格式
        self.document().setDefaultStyleSheet("body { font-family: 'Microsoft YaHei', SimHei, sans-serif; }")
        
        self.instance_colors = [
            QColor(46, 204, 113),   # 绿色
            QColor(52, 152, 219),   # 蓝色
            QColor(155, 89, 182),   # 紫色
            QColor(241, 196, 15),   # 黄色
            QColor(231, 76, 60),    # 红色
            QColor(26, 188, 156),   # 青色
            QColor(230, 126, 34),   # 橙色
            QColor(149, 165, 166),  # 灰色
        ]
        
    def append_log(self, instance_id: int, message: str):
        """添加日志并根据实例ID设置不同颜色"""
        color = self.instance_colors[instance_id % len(self.instance_colors)]
        
        # 创建带颜色的格式
        format = QTextCharFormat()
        format.setForeground(color)
        
        # 添加日志
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        
        # 实例ID标签
        self.setCurrentCharFormat(format)
        self.insertPlainText(f"[实例 #{instance_id+1}] ")
        
        # 重置格式并添加消息
        format = QTextCharFormat()
        self.setCurrentCharFormat(format)
        self.insertPlainText(f"{message}\n")
        
        # 自动滚动到底部
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class ProcessManager:
    """进程管理器，用于启动和管理多个进程实例"""
    
    def __init__(self):
        self.processes = []
        self.output_queues = []
        self.exit_flag = False
        
    def start_instances(self, exe_path: str, instances: int, launch_params: str) -> List[QProcess]:
        """启动多个进程实例并收集它们的输出"""
        self.processes = []
        self.output_queues = []
        
        cmd_base = [exe_path] + (launch_params.split() if launch_params else [])
        
        for i in range(instances):
            # 创建输出队列
            output_queue = queue.Queue()
            self.output_queues.append(output_queue)
            
            # 创建进程
            process = QProcess()
            
            # 设置进程环境变量，确保使用UTF-8编码
            env = process.processEnvironment()
            env.insert("PYTHONIOENCODING", "utf-8")
            env.insert("PYTHONUTF8", "1")
            process.setProcessEnvironment(env)
            
            # 设置工作目录
            process.setWorkingDirectory(os.path.dirname(os.path.abspath(exe_path)))
            
            # 连接输出信号
            process.readyReadStandardOutput.connect(
                lambda p=process, q=output_queue, id=i: self._handle_stdout(p, q, id))
            process.readyReadStandardError.connect(
                lambda p=process, q=output_queue, id=i: self._handle_stderr(p, q, id))
            
            # 启动进程
            process.start(exe_path, launch_params.split() if launch_params else [])
            self.processes.append(process)
            
            logging.info(f"实例 #{i+1} 已启动")
            
            # 短暂延迟，避免同时启动过多实例
            if i < instances - 1:
                time.sleep(0.5)
        
        return self.processes
    
    def _handle_stdout(self, process: QProcess, output_queue: queue.Queue, instance_id: int):
        """处理标准输出"""
        try:
            data = process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            for line in data.splitlines():
                if line.strip():
                    output_queue.put((instance_id, line.strip()))
        except Exception as e:
            output_queue.put((instance_id, f"[错误] 读取标准输出时出错: {str(e)}"))
    
    def _handle_stderr(self, process: QProcess, output_queue: queue.Queue, instance_id: int):
        """处理错误输出"""
        try:
            data = process.readAllStandardError().data().decode('utf-8', errors='replace')
            for line in data.splitlines():
                if line.strip():
                    output_queue.put((instance_id, f"[错误] {line.strip()}"))
        except Exception as e:
            output_queue.put((instance_id, f"[错误] 读取错误输出时出错: {str(e)}"))
    
    def get_outputs(self):
        """获取所有进程的输出"""
        outputs = []
        for i, q in enumerate(self.output_queues):
            try:
                while not q.empty():
                    outputs.append(q.get_nowait())
            except queue.Empty:
                pass
        return outputs
    
    def stop_all(self):
        """停止所有进程"""
        for process in self.processes:
            if process.state() != QProcess.ProcessState.NotRunning:
                process.terminate()
                if not process.waitForFinished(5000):  # 等待最多5秒
                    process.kill()  # 如果进程没有终止，强制结束
        
        self.processes = []
        self.output_queues = []

# 获取Windows系统时间格式
def get_windows_time_format():
    """获取Windows系统时间格式"""
    # 首先检查是否在配置中指定了格式
    if HAS_DEFAULT_CONFIG and DEFAULT_CONFIG.get("time_format"):
        return DEFAULT_CONFIG.get("time_format")
        
    try:
        # 使用ctypes调用Windows API获取系统时间格式
        # LOCALE_STIMEFORMAT = 0x00001003
        LOCALE_STIMEFORMAT = 0x00001003
        LOCALE_USER_DEFAULT = 0x0400
        
        # 先获取所需的缓冲区大小
        size = ctypes.windll.kernel32.GetLocaleInfoW(LOCALE_USER_DEFAULT, LOCALE_STIMEFORMAT, None, 0)
        
        # 创建缓冲区并获取格式
        buffer = ctypes.create_unicode_buffer(size)
        ctypes.windll.kernel32.GetLocaleInfoW(LOCALE_USER_DEFAULT, LOCALE_STIMEFORMAT, buffer, size)
        
        # Windows格式到Qt格式的转换字典
        format_map = {
            'h': 'h',    # 12小时制小时 (1-12)
            'hh': 'hh',  # 12小时制小时，两位数 (01-12)
            'H': 'H',    # 24小时制小时 (0-23)
            'HH': 'HH',  # 24小时制小时，两位数 (00-23)
            'm': 'm',    # 分钟 (0-59)
            'mm': 'mm',  # 分钟，两位数 (00-59)
            's': 's',    # 秒 (0-59)
            'ss': 'ss',  # 秒，两位数 (00-59)
            'tt': 'AP',  # AM/PM指示器
            't': 'A'     # A/P指示器
        }
        
        # 将Windows格式转换为Qt格式 - 修复：按照字符串长度从长到短排序，避免替换错误
        qt_format = buffer.value
        for win_format in sorted(format_map.keys(), key=lambda x: -len(x)):
            qt_format = qt_format.replace(win_format, format_map[win_format])
        
        logging.info(f"获取到系统时间格式: {buffer.value}, 转换为Qt格式: {qt_format}")
        return qt_format
    except Exception as e:
        logging.warning(f"获取系统时间格式失败: {str(e)}，使用默认格式HH:mm:ss")
        return "yyyy-MM-dd HH:mm:ss"  # 返回默认的Qt格式

# 加载用户配置
def load_user_config():
    """加载用户配置文件"""
    if not HAS_DEFAULT_CONFIG:
        return DEFAULT_CONFIG
        
    config = DEFAULT_CONFIG.copy()
    
    try:
        if os.path.exists(USER_CONFIG_PATH):
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
            logging.info(f"已加载用户配置: {USER_CONFIG_PATH}")
        else:
            logging.info(f"未找到用户配置文件，使用默认配置")
    except Exception as e:
        logging.warning(f"加载用户配置失败: {str(e)}，使用默认配置")
    
    return config

# 保存用户配置
def save_user_config(config):
    """保存用户配置到文件"""
    if not HAS_DEFAULT_CONFIG:
        logging.warning("未导入默认配置模块，无法保存用户配置")
        return False
        
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(USER_CONFIG_PATH), exist_ok=True)
        
        with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logging.info(f"已保存用户配置到: {USER_CONFIG_PATH}")
        return True
    except Exception as e:
        logging.error(f"保存用户配置失败: {str(e)}")
        return False

# 添加时间格式验证函数
def is_valid_time_format(time_str):
    """验证时间字符串是否符合HH:MM格式"""
    try:
        # 检查基本格式
        if not time_str or ":" not in time_str:
            return False
            
        # 尝试解析时间
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
            
        hours = int(parts[0])
        minutes = int(parts[1])
        
        # 验证范围
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            return False
            
        return True
    except ValueError:
        return False

# 修改时间字符串转换为datetime对象的函数
def time_str_to_datetime(time_str):
    """将HH:MM格式的时间字符串转换为今天或明天的datetime对象"""
    try:
        hours, minutes = map(int, time_str.split(":"))
        now = datetime.datetime.now()
        target = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # 如果时间已过，设置为明天
        if target < now:
            target += datetime.timedelta(days=1)
            
        return target
    except ValueError as e:
        logging.error(f"时间格式转换错误: {e}")
        # 默认返回今天的11:45
        now = datetime.datetime.now()
        return now.replace(hour=11, minute=45, second=0, microsecond=0)

def get_server_time(retries=3, timeout=20):
    """从迪士尼服务器获取准确时间"""
    if not HAS_PYTZ:
        return None
        
    url = "https://www.hongkongdisneyland.com"
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    
    for attempt in range(retries):
        try:
            logging.info(f"尝试使用代理获取服务器时间... (尝试 {attempt + 1}/{retries})")
            response = requests.head(url, proxies=proxies, timeout=timeout)
            server_time = response.headers.get('Date')
            
            if server_time:
                server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                server_time = server_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Hong_Kong'))
                return server_time
            else:
                logging.info("无法通过代理获取服务器时间，尝试使用系统默认网络...")
        except RequestException as e:
            logging.warning(f"使用代理获取服务器时间时发生错误: {e}")
        
        # 尝试使用系统默认网络
        try:
            logging.info(f"切换到系统默认网络... (尝试 {attempt + 1}/{retries})")
            response = requests.head(url, timeout=timeout)
            server_time = response.headers.get('Date')
            
            if server_time:
                server_time = datetime.datetime.strptime(server_time, '%a, %d %b %Y %H:%M:%S %Z')
                server_time = server_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Hong_Kong'))
                return server_time
            else:
                logging.info("无法获取服务器时间")
        except RequestException as e:
            logging.warning(f"使用系统默认网络获取服务器时间时发生错误: {e}")
        
        time.sleep(5)  # 等待几秒钟后重试
    
    logging.error("多次尝试后仍无法获取服务器时间")
    return None

def set_system_time(target_time: datetime.datetime) -> bool:
    """
    设置系统时间
    
    Args:
        target_time: 目标时间
        
    Returns:
        bool: 是否成功设置系统时间
    """
    try:
        # 将datetime转换为win32api需要的格式
        win_time = win32api.GetSystemTime()
        win_time = (target_time.year,
                   target_time.month,
                   target_time.weekday(),
                   target_time.day,
                   target_time.hour,
                   target_time.minute,
                   target_time.second,
                   target_time.microsecond // 1000)  # 转换为毫秒
                   
        # 设置系统时间
        win32api.SetSystemTime(*win_time)
        logging.info(f"系统时间已设置为: {target_time}")
        return True
    except Exception as e:
        logging.error(f"设置系统时间失败: {e}")
        return False

def synchronize_with_server_time(server_time: datetime.datetime) -> Tuple[bool, str]:
    """
    将本地时间与服务器时间同步
    
    Args:
        server_time: 服务器时间
        
    Returns:
        Tuple[bool, str]: (是否成功, 同步结果消息)
    """
    if not HAS_PYTZ:
        return False, "缺少必要的pytz模块，无法进行时间同步"
        
    try:
        now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
        time_difference = (server_time - now).total_seconds()
        
        if abs(time_difference) > 0.001:
            message = f"本地时间与服务器时间相差 {time_difference:.3f} 秒"
            logging.info(message)
            
            # 设置系统时间
            if set_system_time(server_time):
                return True, f"{message}，系统时间已调整"
            else:
                return False, f"{message}，但调整系统时间失败"
        else:
            return True, "本地时间与服务器时间已同步"
            
    except Exception as e:
        error_msg = f"同步时间时发生错误: {e}"
        logging.error(error_msg)
        return False, error_msg

class TimedLauncherUI(QMainWindow, QtStyleTools):
    """定时启动器图形界面主窗口"""
    
    # 定义信号
    update_countdown_signal = pyqtSignal(int)
    update_log_signal = pyqtSignal(int, str)
    
    def __init__(self, font_name=""):
        super().__init__()
        
        # 加载用户配置
        self.config = load_user_config()
        
        # 应用Material主题 - 设置为实色风格
        apply_stylesheet(QApplication.instance(), theme=self.config.get("default_theme", "dark_teal.xml"), invert_secondary=True, extra={
            # 自定义Material样式参数
            'density_scale': '0',  # 调整密度
            'font_size': '9px',    # 基本字体大小
            'primaryColor': '#009688',  # 主色调
        })
        
        # 设置文本框和选项框样式，使用微软雅黑字体和白色文字，实色背景
        self.setStyleSheet("""
            QLineEdit, QSpinBox, QDateTimeEdit, QTimeEdit, QComboBox {
                font-family: "Microsoft YaHei";
                color: white;
                font-weight: normal;
                border: none;
                background-color: rgba(45, 45, 45, 255);
                font-size: 9pt;
                min-height: 28px;
                padding: 2px 5px;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDateTimeEdit::up-button, QDateTimeEdit::down-button {
                width: 20px;
                height: 14px;
                background-color: rgba(55, 55, 55, 255);
                border: none;
            }
            QSpinBox, QDateTimeEdit {
                selection-color: white;
                background-color: rgba(45, 45, 45, 255);
                border: none;
                padding-right: 15px;
            }
            QCheckBox {
                font-family: "Microsoft YaHei";
                color: white;
                font-weight: bold;
                font-size: 9pt;
                min-height: 24px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QTextEdit {
                font-family: "Microsoft YaHei";
                font-weight: normal;
                background-color: rgba(45, 45, 45, 255);
                border: none;
                font-size: 9pt;
            }
            QLabel {
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton {
                font-weight: bold;
                min-width: 80px;
                min-height: 28px;
                border: none;
                border-radius: 4px;
                font-size: 9pt;
                padding: 5px 10px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid rgba(60, 60, 60, 255);
                font-size: 10pt;
                margin-top: 15px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
            /* 滚动条样式 */
            QScrollBar:vertical {
                background-color: rgba(45, 45, 45, 255);
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(100, 100, 100, 255);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            /* 自定义实色背景按钮样式 */
            QPushButton.success {
                background-color: #009688;
                color: white;
            }
            QPushButton.danger {
                background-color: #f44336;
                color: white;
            }
            QPushButton.warning {
                background-color: #ff9800;
                color: white;
            }
            QPushButton.primary {
                background-color: #2196f3;
                color: white;
            }
            QPushButton.info {
                background-color: #00bcd4;
                color: white;
            }
            /* 按钮悬停效果 */
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            /* 进度条样式 */
            QProgressBar {
                border: none;
                background-color: rgba(45, 45, 45, 255);
                border-radius: 3px;
                text-align: center;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #009688;
                border-radius: 3px;
            }
        """)
        
        # 初始化进程管理器
        self.process_manager = ProcessManager()
        
        # 初始化UI状态变量
        self.countdown_timer = None
        self.launch_timer = None
        self.running = False
        self.target_time = None
        
        # 设置窗口
        self.setWindowTitle("定时多实例启动器")
        self.setMinimumSize(
            self.config.get("window_width", 800), 
            self.config.get("window_height", 600)
        )
        
        # 定义默认字体
        self.default_font = font_name if font_name else "Microsoft YaHei"
        
        # 设置应用程序字体
        app_font = QFont(self.default_font, 9)
        QApplication.setFont(app_font)
        
        # 获取系统时间格式
        self.system_time_format = self.config.get("time_format", get_windows_time_format())
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部控制面板和底部日志面板
        top_panel = QWidget()
        bottom_panel = QWidget()
        
        # 创建分割器，允许调整面板大小
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(top_panel)
        splitter.addWidget(bottom_panel)
        splitter.setSizes([200, 400])  # 初始大小分配
        
        main_layout.addWidget(splitter)
        
        # 设置顶部面板（控制面板）
        top_layout = QVBoxLayout(top_panel)
        
        # 创建配置组
        config_group = QGroupBox("程序配置")
        config_group.setFont(QFont(self.default_font, 9))
        config_layout = QGridLayout()
        config_group.setLayout(config_layout)
        
        # 添加配置项
        config_label1 = QLabel("目标程序:")
        config_label1.setFont(QFont(self.default_font, 9))
        config_layout.addWidget(config_label1, 0, 0)
        
        self.exe_path_edit = QLineEdit(self.config.get("exe_path", "wuyanzhengma.exe"))
        self.exe_path_edit.setFont(QFont("Microsoft YaHei", 9))
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.setFont(QFont(self.default_font, 9))
        self.browse_button.clicked.connect(self.browse_exe)
        self.browse_button.setProperty('class', 'success') # 添加Material风格类
        
        exe_path_layout = QHBoxLayout()
        exe_path_layout.addWidget(self.exe_path_edit)
        exe_path_layout.addWidget(self.browse_button)
        config_layout.addLayout(exe_path_layout, 0, 1)
        
        config_label2 = QLabel("实例数量:")
        config_label2.setFont(QFont(self.default_font, 9))
        config_layout.addWidget(config_label2, 1, 0)
        
        # 改用滑块替代数字输入框
        instances_layout = QHBoxLayout()
        
        self.instances_slider = QSlider(Qt.Orientation.Horizontal)
        self.instances_slider.setRange(1, 100)
        self.instances_slider.setValue(self.config.get("instances", 10))
        self.instances_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.instances_slider.setTickInterval(10)
        
        self.instances_spinbox = QSpinBox()
        self.instances_spinbox.setRange(1, 100)
        self.instances_spinbox.setValue(self.config.get("instances", 10))
        self.instances_spinbox.setMinimumSize(70, 25)
        self.instances_spinbox.setFont(QFont("Microsoft YaHei", 9))
        
        # 连接滑块和数字输入框
        self.instances_slider.valueChanged.connect(self.instances_spinbox.setValue)
        self.instances_spinbox.valueChanged.connect(self.instances_slider.setValue)
        
        instances_layout.addWidget(self.instances_slider)
        instances_layout.addWidget(self.instances_spinbox)
        
        config_layout.addLayout(instances_layout, 1, 1)
        
        # 启动时间标签和输入框现在移到第2行
        config_label3 = QLabel("启动时间:")
        config_label3.setFont(QFont(self.default_font, 9))
        config_layout.addWidget(config_label3, 2, 0)
        
        time_layout = QHBoxLayout()
        
        # 改用文本输入框
        self.target_time_edit = QLineEdit(self.config.get("default_time", "11:45"))
        self.target_time_edit.setFont(QFont("Microsoft YaHei", 9))
        self.target_time_edit.setPlaceholderText("格式: HH:MM")
        self.target_time_edit.setToolTip("请输入24小时制时间，格式为 HH:MM，例如 11:45")
        self.target_time_edit.setInputMask("99:99")  # 添加输入掩码限制格式
        self.target_time_edit.setMinimumSize(100, 25)
        self.target_time_edit.setMaximumWidth(100)
        
        # 创建复制当前时间按钮（添加Material风格）
        self.copy_time_button = QPushButton("现在")
        self.copy_time_button.setFont(QFont(self.default_font, 9))
        self.copy_time_button.setToolTip("点击设置为当前时间")
        self.copy_time_button.clicked.connect(self.copy_current_time)
        self.copy_time_button.setMinimumSize(60, 28)
        self.copy_time_button.setMaximumWidth(60)
        self.copy_time_button.setProperty('class', 'info')  # 添加Material风格类
        
        self.use_now_checkbox = QCheckBox("立即启动")
        self.use_now_checkbox.setFont(QFont("Microsoft YaHei", 9))
        self.use_now_checkbox.setChecked(self.config.get("launch_now", False))
        self.use_now_checkbox.stateChanged.connect(self.toggle_time_edit)
        
        time_layout.addWidget(self.target_time_edit)
        time_layout.addWidget(self.copy_time_button)
        time_layout.addWidget(self.use_now_checkbox)
        time_layout.addStretch()  # 添加伸缩器填充剩余空间
        config_layout.addLayout(time_layout, 2, 1)
        
        # 同步时间选项移到第3行
        config_label4 = QLabel("同步时间:")
        config_label4.setFont(QFont(self.default_font, 9))
        config_layout.addWidget(config_label4, 3, 0)
        
        self.sync_time_checkbox = QCheckBox("与服务器同步时间")
        self.sync_time_checkbox.setFont(QFont("Microsoft YaHei", 9))
        self.sync_time_checkbox.setChecked(self.config.get("sync_server_time", True))
        config_layout.addWidget(self.sync_time_checkbox, 3, 1)
        
        # 添加保存配置按钮到第4行
        config_label5 = QLabel("用户配置:")
        config_label5.setFont(QFont(self.default_font, 9))
        config_layout.addWidget(config_label5, 4, 0)
        
        config_buttons_layout = QHBoxLayout()
        
        self.save_config_button = QPushButton("保存当前配置")
        self.save_config_button.setFont(QFont(self.default_font, 9))
        self.save_config_button.clicked.connect(self.save_current_config)
        self.save_config_button.setProperty('class', 'primary')
        
        self.reset_config_button = QPushButton("恢复默认配置")
        self.reset_config_button.setFont(QFont(self.default_font, 9))
        self.reset_config_button.clicked.connect(self.reset_to_default_config)
        self.reset_config_button.setProperty('class', 'warning')
        
        config_buttons_layout.addWidget(self.save_config_button)
        config_buttons_layout.addWidget(self.reset_config_button)
        config_layout.addLayout(config_buttons_layout, 4, 1)
        
        # 添加配置组到顶部布局
        top_layout.addWidget(config_group)
        
        # 创建控制组
        control_group = QGroupBox("控制面板")
        control_group.setFont(QFont(self.default_font, 9))
        control_layout = QVBoxLayout()
        control_group.setLayout(control_layout)
        
        # 添加倒计时显示
        self.countdown_label = QLabel("准备就绪，等待启动")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont(self.default_font, 14))
        self.countdown_label.setObjectName("titleLabel")  # 设置对象名称，方便CSS选择器定位
        self.countdown_label.setStyleSheet("font-size: 14pt; margin: 5px 0;")
        control_layout.addWidget(self.countdown_label)
        
        # 添加进度条 (Material风格)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(16)
        control_layout.addWidget(self.progress_bar)
        
        # 添加控制按钮 (添加Material风格)
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始")
        self.start_button.setFont(QFont(self.default_font, 9))
        self.start_button.clicked.connect(self.start_launcher)
        self.start_button.setProperty('class', 'success')  # 设置Material风格按钮
        
        self.stop_button = QPushButton("停止")
        self.stop_button.setFont(QFont(self.default_font, 9))
        self.stop_button.clicked.connect(self.stop_launcher)
        self.stop_button.setEnabled(False)
        self.stop_button.setProperty('class', 'danger')  # 设置Material风格按钮
        
        self.reset_button = QPushButton("重置")
        self.reset_button.setFont(QFont(self.default_font, 9))
        self.reset_button.clicked.connect(self.reset_launcher)
        self.reset_button.setProperty('class', 'warning')  # 设置Material风格按钮
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.reset_button)
        
        control_layout.addLayout(buttons_layout)
        
        # 添加控制组到顶部布局
        top_layout.addWidget(control_group)
        
        # 设置底部面板（日志面板）
        bottom_layout = QVBoxLayout(bottom_panel)
        
        log_group = QGroupBox("日志监控")
        log_group.setFont(QFont(self.default_font, 9))
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        # 创建日志显示区域
        self.log_monitor = LogMonitor(font_name)
        log_layout.addWidget(self.log_monitor)
        
        # 添加日志控制按钮
        log_control_layout = QHBoxLayout()
        
        self.clear_log_button = QPushButton("清除日志")
        self.clear_log_button.setFont(QFont(self.default_font, 9))
        self.clear_log_button.clicked.connect(self.clear_logs)
        
        self.save_log_button = QPushButton("保存日志")
        self.save_log_button.setFont(QFont(self.default_font, 9))
        self.save_log_button.clicked.connect(self.save_logs)
        
        log_control_layout.addWidget(self.clear_log_button)
        log_control_layout.addWidget(self.save_log_button)
        log_control_layout.addStretch()
        
        log_layout.addLayout(log_control_layout)
        
        # 添加日志组到底部布局
        bottom_layout.addWidget(log_group)
        
        # 连接信号
        self.update_countdown_signal.connect(self.update_countdown)
        self.update_log_signal.connect(self.update_log)
        
        # 初始化倒计时计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown_slot)
        
        # 初始化日志更新计时器
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.check_process_output)
        self.log_timer.start(100)  # 每100毫秒检查一次输出
        
        # 初始界面添加一条欢迎信息
        self.log_monitor.append_log(-1, "欢迎使用定时多实例启动器，程序已准备就绪")
    
    def toggle_time_edit(self, state):
        """切换时间编辑器的启用状态"""
        self.target_time_edit.setEnabled(not state)
        self.copy_time_button.setEnabled(not state)
    
    def browse_exe(self):
        """浏览选择可执行文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择可执行文件", "", "可执行文件 (*.exe)"
        )
        if file_path:
            self.exe_path_edit.setText(file_path)
    
    def start_launcher(self):
        """启动定时器和启动进程"""
        if self.running:
            return
        
        # 获取配置
        exe_path = self.exe_path_edit.text().strip()
        if not os.path.exists(exe_path):
            QMessageBox.warning(self, "错误", f"找不到可执行文件: {exe_path}")
            return
        
        instances = self.instances_spinbox.value()
        
        # 添加点击动画
        self.animate_button(self.start_button)
        
        # 检查是否需要同步时间
        if self.sync_time_checkbox.isChecked():
            self.log_monitor.append_log(-1, "正在与服务器同步时间...")
            
            # 获取服务器时间
            server_time = get_server_time()
            if not server_time:
                reply = QMessageBox.question(
                    self,
                    "时间同步失败",
                    "无法获取服务器时间，是否继续启动？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    self.log_monitor.append_log(-1, "用户取消启动")
                    return
            else:
                # 同步系统时间
                success, message = synchronize_with_server_time(server_time)
                self.log_monitor.append_log(-1, message)
                
                if not success:
                    reply = QMessageBox.question(
                        self,
                        "时间同步失败",
                        f"{message}\n是否继续启动？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        self.log_monitor.append_log(-1, "用户取消启动")
                        return
        
        # 检查Chrome安装
        if HAS_CHROME_SETUP:
            try:
                if not check_chrome_installed():
                    # 显示Chrome安装提示
                    reply = QMessageBox.question(
                        self, 
                        "Chrome安装", 
                        "启动器需要Chrome浏览器。未检测到Chrome，是否立即安装？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        self.log_monitor.append_log(-1, "正在启动Chrome安装程序...")
                        # 禁用启动按钮，防止重复点击
                        self.start_button.setEnabled(False)
                        
                        # 创建进度对话框
                        progress_dialog = QMessageBox(self)
                        progress_dialog.setWindowTitle("Chrome安装")
                        progress_dialog.setText("正在安装Chrome浏览器，请稍候...")
                        progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
                        
                        # 启动安装进程
                        def install_chrome():
                            try:
                                process = run_chrome_setup()
                                success = monitor_installation(process)
                                
                                # 安装完成后关闭进度对话框并继续启动
                                progress_dialog.done(0)
                                
                                if success:
                                    self.log_monitor.append_log(-1, "Chrome安装成功，继续启动...")
                                    self.start_launcher_impl(exe_path, instances)
                                else:
                                    self.log_monitor.append_log(-1, "Chrome安装失败，无法继续。")
                                    QMessageBox.critical(self, "错误", "Chrome安装失败，无法继续启动。")
                                    self.start_button.setEnabled(True)
                            except Exception as e:
                                self.log_monitor.append_log(-1, f"Chrome安装过程中出错: {str(e)}")
                                progress_dialog.done(0)
                                QMessageBox.critical(self, "错误", f"Chrome安装过程中出错: {str(e)}")
                                self.start_button.setEnabled(True)
                        
                        # 在后台线程中执行安装
                        install_thread = threading.Thread(target=install_chrome)
                        install_thread.daemon = True
                        install_thread.start()
                        
                        # 显示进度对话框
                        progress_dialog.exec()
                        return
                    else:
                        # 用户选择不安装Chrome，继续启动
                        self.log_monitor.append_log(-1, "用户选择跳过Chrome安装，继续启动...")
                else:
                    self.log_monitor.append_log(-1, "已检测到Chrome浏览器，继续启动...")
            except Exception as e:
                self.log_monitor.append_log(-1, f"Chrome检查过程中出错: {str(e)}")
                # 错误不应阻止启动，继续执行
        
        # 继续原来的启动流程
        self.start_launcher_impl(exe_path, instances)
    
    def start_launcher_impl(self, exe_path, instances):
        """实际的启动逻辑实现"""
        # 检查是否立即启动
        if self.use_now_checkbox.isChecked():
            self.immediate_launch(exe_path, instances)
            return
        
        # 验证时间格式
        time_str = self.target_time_edit.text().strip()
        if not is_valid_time_format(time_str):
            QMessageBox.warning(self, "错误", "时间格式不正确，请使用格式 HH:MM")
            return
        
        # 设置目标时间
        self.target_time = time_str_to_datetime(time_str)
        current_datetime = datetime.datetime.now()
        time_diff_seconds = (self.target_time - current_datetime).total_seconds()
        
        # 保存原始目标时间，用于进度计算
        self.original_target_time = datetime.datetime.now()
        self.original_time_diff_seconds = time_diff_seconds
        
        # 更新UI状态
        self.running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.exe_path_edit.setEnabled(False)
        self.instances_spinbox.setEnabled(False)
        self.target_time_edit.setEnabled(False)
        self.use_now_checkbox.setEnabled(False)
        self.sync_time_checkbox.setEnabled(False)
        
        # 开始倒计时
        self.timer.start(1000)  # 每秒更新一次
        
        # 添加日志
        self.log_monitor.append_log(-1, f"系统已启动，将在 {self.target_time.strftime('%Y-%m-%d %H:%M:%S')} 启动 {instances} 个实例")
        self.log_monitor.append_log(-1, f"目标程序: {exe_path}")
        
        # 设置启动定时器
        self.launch_timer = threading.Timer(
            time_diff_seconds, 
            self.launch_instances,
            args=[exe_path, instances]
        )
        self.launch_timer.daemon = True
        self.launch_timer.start()
    
    def immediate_launch(self, exe_path, instances):
        """立即启动程序实例"""
        self.running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.exe_path_edit.setEnabled(False)
        self.instances_spinbox.setEnabled(False)
        self.target_time_edit.setEnabled(False)
        self.use_now_checkbox.setEnabled(False)
        self.sync_time_checkbox.setEnabled(False)
        
        self.countdown_label.setText("立即启动模式")
        self.progress_bar.setValue(100)
        
        # 添加日志
        self.log_monitor.append_log(-1, f"系统已启动，立即启动 {instances} 个实例")
        self.log_monitor.append_log(-1, f"目标程序: {exe_path}")
        
        # 启动实例
        self.launch_instances(exe_path, instances)
    
    def launch_instances(self, exe_path, instances):
        """启动指定数量的程序实例"""
        # 在UI线程中执行
        QApplication.instance().processEvents()
        
        self.countdown_label.setText("正在启动实例...")
        self.log_monitor.append_log(-1, "开始启动实例...")
        
        # 启动实例
        try:
            self.process_manager.start_instances(exe_path, instances, "")
            self.log_monitor.append_log(-1, f"成功启动 {instances} 个实例")
            self.countdown_label.setText(f"已启动 {instances} 个实例")
        except Exception as e:
            self.log_monitor.append_log(-1, f"启动实例时出错: {str(e)}")
            self.countdown_label.setText("启动失败")
            self.stop_launcher()
    
    def stop_launcher(self):
        """停止所有进程和定时器"""
        if not self.running:
            return
        
        # 停止定时器
        if self.timer.isActive():
            self.timer.stop()
        
        if self.launch_timer and self.launch_timer.is_alive():
            self.launch_timer.cancel()
        
        # 停止所有进程
        self.process_manager.stop_all()
        
        # 更新UI状态
        self.running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.exe_path_edit.setEnabled(True)
        self.instances_spinbox.setEnabled(True)
        self.target_time_edit.setEnabled(not self.use_now_checkbox.isChecked())
        self.use_now_checkbox.setEnabled(True)
        self.sync_time_checkbox.setEnabled(True)
        
        self.countdown_label.setText("已停止")
        self.progress_bar.setValue(0)
        
        # 添加日志
        self.log_monitor.append_log(-1, "系统已停止，所有实例已终止")
    
    def reset_launcher(self):
        """重置所有设置"""
        self.stop_launcher()
        
        if HAS_DEFAULT_CONFIG:
            # 重置为默认配置
            self.reset_to_default_config()
        else:
            # 硬编码默认值
            self.exe_path_edit.setText("wuyanzhengma.exe")
            self.instances_spinbox.setValue(10)
            self.instances_slider.setValue(10)
            self.target_time_edit.setText("11:45")
            self.use_now_checkbox.setChecked(False)
            self.sync_time_checkbox.setChecked(True)
        
        self.countdown_label.setText("准备就绪，等待启动")
        self.progress_bar.setValue(0)
        
        # 添加日志
        self.log_monitor.append_log(-1, "系统已重置，所有设置恢复默认")
    
    def update_countdown_slot(self):
        """更新倒计时定时器槽函数"""
        if not self.running or not self.target_time:
            return
        
        current_time = datetime.datetime.now()
        time_diff = (self.target_time - current_time).total_seconds()
        
        if time_diff <= 0:
            self.timer.stop()
            self.countdown_label.setText("正在启动...")
            self.progress_bar.setValue(100)
            return
        
        # 计算倒计时文本
        hours, remainder = divmod(int(time_diff), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        countdown_text = f"倒计时: "
        if hours > 0:
            countdown_text += f"{hours}时 "
        countdown_text += f"{minutes}分 {seconds}秒"
        
        # 计算进度百分比 - 使用保存的原始时间差进行计算
        if hasattr(self, 'original_time_diff_seconds') and self.original_time_diff_seconds > 0:
            elapsed = self.original_time_diff_seconds - time_diff
            progress = (elapsed / self.original_time_diff_seconds) * 100
            self.progress_bar.setValue(int(progress))
        
        self.countdown_label.setText(countdown_text)
    
    def update_countdown(self, seconds_left):
        """更新倒计时显示"""
        hours, remainder = divmod(seconds_left, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        countdown_text = f"倒计时: "
        if hours > 0:
            countdown_text += f"{hours}时 "
        countdown_text += f"{minutes}分 {seconds}秒"
        
        self.countdown_label.setText(countdown_text)
    
    def update_log(self, instance_id, message):
        """更新日志显示"""
        self.log_monitor.append_log(instance_id, message)
    
    def check_process_output(self):
        """检查进程输出并更新日志"""
        if not self.running:
            return
        
        # 获取所有进程输出
        outputs = self.process_manager.get_outputs()
        for instance_id, message in outputs:
            self.update_log(instance_id, message)
    
    def clear_logs(self):
        """清除日志"""
        self.log_monitor.clear()
        self.log_monitor.append_log(-1, "日志已清除")
    
    def save_logs(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_monitor.toPlainText())
                self.log_monitor.append_log(-1, f"日志已保存到 {file_path}")
            except Exception as e:
                self.log_monitor.append_log(-1, f"保存日志失败: {str(e)}")
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        if self.running:
            reply = QMessageBox.question(
                self, "确认退出", 
                "程序正在运行中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_launcher()
                event.accept()
            else:
                event.ignore()
    
    def copy_current_time(self):
        """将当前时间复制到时间编辑框"""
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%H:%M")
        self.target_time_edit.setText(time_str)
        
        # 添加动画效果
        self.animate_button(self.copy_time_button)
        
        self.log_monitor.append_log(-1, f"已设置时间为当前时间: {time_str}")
    
    def animate_button(self, button):
        """为按钮添加点击动画效果"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(100)
        
        start_geometry = button.geometry()
        
        # 缩小按钮
        mid_geometry = start_geometry
        mid_geometry.setWidth(int(start_geometry.width() * 0.9))
        mid_geometry.setHeight(int(start_geometry.height() * 0.9))
        mid_geometry.moveCenter(start_geometry.center())
        
        animation.setStartValue(start_geometry)
        animation.setEndValue(mid_geometry)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 恢复按钮大小
        animation_2 = QPropertyAnimation(button, b"geometry")
        animation_2.setDuration(100)
        animation_2.setStartValue(mid_geometry)
        animation_2.setEndValue(start_geometry)
        animation_2.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        animation.finished.connect(animation_2.start)
        animation.start()

    def save_current_config(self):
        """保存当前配置到用户配置文件"""
        # 收集当前UI上的配置
        current_config = {
            "exe_path": self.exe_path_edit.text(),
            "instances": self.instances_spinbox.value(),
            "default_time": self.target_time_edit.text(),  # 直接保存时间字符串
            "launch_now": self.use_now_checkbox.isChecked(),
            "sync_server_time": self.sync_time_checkbox.isChecked(),
            "time_format": "HH:mm"  # 固定格式
        }
        
        # 保存配置
        if save_user_config(current_config):
            self.log_monitor.append_log(-1, "已成功保存当前配置")
            # 更新当前配置
            self.config.update(current_config)
        else:
            self.log_monitor.append_log(-1, "保存配置失败")
    
    def reset_to_default_config(self):
        """重置为默认配置"""
        if HAS_DEFAULT_CONFIG:
            # 重置为默认值
            self.config = DEFAULT_CONFIG.copy()
            
            # 更新UI
            self.exe_path_edit.setText(self.config.get("exe_path", "wuyanzhengma.exe"))
            self.instances_spinbox.setValue(self.config.get("instances", 10))
            self.instances_slider.setValue(self.config.get("instances", 10))
            
            # 设置默认时间
            self.target_time_edit.setText(self.config.get("default_time", "11:45"))
            
            self.use_now_checkbox.setChecked(self.config.get("launch_now", False))
            self.sync_time_checkbox.setChecked(self.config.get("sync_server_time", True))
            
            # 如果有用户配置文件，则删除
            if os.path.exists(USER_CONFIG_PATH):
                try:
                    os.remove(USER_CONFIG_PATH)
                    self.log_monitor.append_log(-1, "已删除用户配置文件，恢复默认配置")
                except Exception as e:
                    self.log_monitor.append_log(-1, f"删除用户配置文件失败: {str(e)}")
            else:
                self.log_monitor.append_log(-1, "已恢复默认配置")
        else:
            self.log_monitor.append_log(-1, "未找到默认配置模块，无法恢复默认配置")

def main():
    """主函数"""
    # 处理Ctrl+C信号
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 确保正确的环境变量设置在程序一开始就被设置
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    try:
        # 高DPI支持
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except:
        logging.warning("无法设置高DPI支持，将使用默认DPI设置")
    
    # 强制使用微软雅黑字体
    default_font = QFont("Microsoft YaHei", 9)
    QApplication.setFont(default_font)
    
    # 统一设置DPI缩放因子
    app.setStyleSheet("""
        * {
            font-family: "Microsoft YaHei";
            font-size: 9pt;
        }
        QLabel#titleLabel {
            font-family: "Microsoft YaHei";
            font-size: 14pt;
            font-weight: bold;
        }
        QPushButton {
            font-family: "Microsoft YaHei";
            font-size: 9pt;
            padding: 5px 10px;
            font-weight: bold;
        }
        QGroupBox {
            font-family: "Microsoft YaHei";
            font-size: 10pt;
            font-weight: bold;
        }
    """)
    
    # 设置UI环境并获取合适的字体
    font_name = setup_ui_environment()
    
    # 创建并显示窗口
    window = TimedLauncherUI("Microsoft YaHei")
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
