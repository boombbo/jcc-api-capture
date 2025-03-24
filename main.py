"""
主程序入口
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
from core.utils import get_logger

def main():
    """主程序入口"""
    # 初始化日志
    logger = get_logger(__name__)
    logger.info("启动应用程序")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

def test_ui():
    """UI测试函数"""
    import pytest
    from PyQt6.QtWidgets import QApplication
    from ui.widgets import (
        InfoWidget, CreateWidget, CloneWidget, BackupWidget,
        BasicControlWidget, WindowControlWidget, AppManagementWidget,
        DisplaySettingsWidget, PerformanceSettingsWidget,
        NetworkSettingsWidget, DeviceSettingsWidget,
        CommandWidget, ShellWidget,
        SimulationWidget, DriverWidget
    )
    
    # 创建测试应用
    app = QApplication(sys.argv)
    
    # 测试各个组件
    widgets = [
        InfoWidget(),
        CreateWidget(),
        CloneWidget(),
        BackupWidget(),
        BasicControlWidget(),
        WindowControlWidget(),
        AppManagementWidget(),
        DisplaySettingsWidget(),
        PerformanceSettingsWidget(),
        NetworkSettingsWidget(),
        DeviceSettingsWidget(),
        CommandWidget(),
        ShellWidget(),
        SimulationWidget(),
        DriverWidget()
    ]
    
    # 显示每个组件
    for widget in widgets:
        widget.show()
    
    # 运行应用
    return app.exec()

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 运行UI测试
        sys.exit(test_ui())
    else:
        # 运行主程序
        main() 