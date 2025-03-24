"""
兼容性处理工具

提供跨平台和跨Qt绑定的兼容性处理函数
"""

import os
import sys
import platform
from typing import Optional

from qtpy import QtCore, QtGui, QtWidgets


def is_dark_mode() -> bool:
    """检测系统是否为暗色模式
    
    Returns:
        如果系统为暗色模式则返回True，否则返回False
    """
    # Windows 10/11
    if sys.platform == 'win32':
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return value == 0
        except Exception:
            # 如果无法获取注册表值，使用QPalette检测
            pass
    
    # macOS
    elif sys.platform == 'darwin':
        try:
            import subprocess
            cmd = 'defaults read -g AppleInterfaceStyle'
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return result.stdout.strip() == 'Dark'
        except Exception:
            pass
    
    # Linux (基于GTK)
    elif sys.platform == 'linux':
        try:
            import subprocess
            cmd = 'gsettings get org.gnome.desktop.interface color-scheme'
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return 'dark' in result.stdout.lower()
        except Exception:
            pass
    
    # 使用QPalette检测
    app = QtWidgets.QApplication.instance()
    if app:
        palette = app.palette()
        bg_color = palette.color(QtGui.QPalette.Window)
        text_color = palette.color(QtGui.QPalette.WindowText)
        return bg_color.lightness() < text_color.lightness()
    
    # 默认返回False
    return False


def get_qt_version() -> str:
    """获取Qt版本
    
    Returns:
        Qt版本字符串
    """
    return QtCore.QT_VERSION_STR


def get_binding_name() -> str:
    """获取当前使用的Qt绑定名称
    
    Returns:
        Qt绑定名称：'PyQt5', 'PySide2', 'PyQt6' 或 'PySide6'
    """
    from qtpy import API_NAME
    return API_NAME


def is_high_dpi() -> bool:
    """检测是否为高DPI环境
    
    Returns:
        如果为高DPI环境则返回True，否则返回False
    """
    if hasattr(QtCore, 'QCoreApplication'):
        app = QtCore.QCoreApplication.instance()
        if app:
            # Qt 5.6+
            if hasattr(app, 'devicePixelRatio'):
                return app.devicePixelRatio() > 1.0
            # Qt 5.0+
            elif hasattr(QtWidgets.QApplication, 'primaryScreen'):
                screen = QtWidgets.QApplication.primaryScreen()
                if screen:
                    return screen.devicePixelRatio() > 1.0
    
    # 默认返回False
    return False


def set_theme_env(theme_name: str):
    """设置主题环境变量
    
    Args:
        theme_name: 主题名称
    """
    # QDarkTheme环境变量
    if theme_name.startswith('qdarktheme_'):
        mode = theme_name.replace('qdarktheme_', '')
        os.environ['QDARKTHEME_MODE'] = mode
    
    # QDarkStyle环境变量
    elif theme_name.startswith('qdarkstyle_'):
        mode = theme_name.replace('qdarkstyle_', '')
        os.environ['QDARKSTYLE_MODE'] = mode 
