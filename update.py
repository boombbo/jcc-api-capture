#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
功能: 简单的项目更新脚本
日期: 2025-03-02
"""

import os
import subprocess
from datetime import datetime

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding='utf-8')
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)

def update_project(commit_message="更新代码"):
    """
    更新项目并推送到GitHub
    
    参数:
    - commit_message: 提交信息
    """
    try:
        print("=" * 50)
        print("项目更新工具")
        print("=" * 50)
        
        # 1. 添加所有更改
        print("\n添加更改...")
        success, output = run_command("git add .")
        if not success:
            print(f"❌ 添加失败: {output}")
            return False
        
        # 2. 检查是否有更改
        success, status = run_command("git status --porcelain")
        if not success:
            print(f"❌ 检查状态失败: {status}")
            return False
        
        if not status.strip():
            print("✨ 没有需要更新的内容")
            return True
        
        # 3. 提交更改
        print("\n提交更改...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_message = f"{commit_message} ({timestamp})"
        success, output = run_command(f'git commit -m "{full_message}"')
        if not success:
            print(f"❌ 提交失败: {output}")
            return False
        print("✅ 提交成功")
        
        # 4. 推送到GitHub
        print("\n推送到GitHub...")
        success, output = run_command("git push")
        if not success:
            print(f"❌ 推送失败: {output}")
            return False
        print("✅ 推送成功")
        
        print("\n" + "=" * 50)
        print("✨ 更新完成！GitHub Actions将自动处理版本更新和发布。")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 可以自定义提交信息
    update_project("更新项目代码") 
