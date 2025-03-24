@echo off

:: 创建主目录结构
mkdir jcc_front
cd jcc_front

:: 创建主要文件
type nul > main.py
type nul > requirements.txt
type nul > README.md

:: 创建配置目录及文件
mkdir config
type nul > config\\__init__.py
type nul > config\\settings.py
type nul > config\\constants.py

:: 创建核心功能目录及文件
mkdir core
type nul > core\\__init__.py
type nul > core\\mumu_manager.py
type nul > core\\adb_controller.py
type nul > core\\utils.py

:: 创建UI目录结构
mkdir ui
mkdir ui\\resources
mkdir ui\\widgets
type nul > ui\\__init__.py
type nul > ui\\main_window.py

:: 创建widgets子目录及文件
cd ui\\widgets
type nul > __init__.py

:: 创建模拟器管理目录及文件
mkdir emulator_management
type nul > emulator_management\\__init__.py
type nul > emulator_management\\info_widget.py
type nul > emulator_management\\create_widget.py
type nul > emulator_management\\clone_widget.py
type nul > emulator_management\\backup_widget.py

:: 创建模拟器控制目录及文件
mkdir emulator_control
type nul > emulator_control\\__init__.py
type nul > emulator_control\\basic_control.py
type nul > emulator_control\\window_control.py
type nul > emulator_control\\app_management.py

:: 创建设置相关目录及文件
mkdir settings
type nul > settings\\__init__.py
type nul > settings\\display_settings.py
type nul > settings\\performance_settings.py
type nul > settings\\network_settings.py
type nul > settings\\device_settings.py

:: 创建ADB功能目录及文件
mkdir adb
type nul > adb\\__init__.py
type nul > adb\\command_widget.py
type nul > adb\\shell_widget.py

:: 创建硬件管理目录及文件
mkdir hardware
type nul > hardware\\__init__.py
type nul > hardware\\simulation_widget.py
type nul > hardware\\driver_widget.py

:: 返回项目根目录
cd ..\\..\\..

:: 创建测试目录
mkdir tests
type nul > tests\\__init__.py

echo Project structure created successfully!
