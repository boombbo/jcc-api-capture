"""
MuMu模拟器管理工具主程序入口
"""
import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

# 设置工作目录
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# 添加当前目录到路径
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入主题管理器
from jcc_front.themes.theme_manager import theme_manager, DARK_THEME
from jcc_front.main_window import MainWindow

def main():
    """主程序入口"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序名称
    app.setApplicationName("MuMu模拟器管理工具")
    
    # 应用主题
    theme_manager.apply_theme(app, DARK_THEME)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
