@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 设置标题
title GitHub项目自动更新工具

:: 显示彩色文本
color 0A

echo ================================================
echo              GitHub项目自动更新工具
echo ================================================
echo.

:: 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
)

:: 获取提交信息
set /p commit_message=请输入更新说明（直接回车使用默认信息）: 
if "!commit_message!"=="" set commit_message=更新项目代码

:: 运行Python更新脚本
echo.
echo 正在执行更新...
python update.py "!commit_message!"

:: 等待用户确认
echo.
echo ================================================
echo 按任意键退出...
pause > nul 
