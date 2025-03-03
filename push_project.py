#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
功能: 推送当前项目到GitHub
作者: 中国红客联盟技术团队
日期: 2025-03-02
"""

import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_command(command, error_message=None):
    """运行命令并处理错误"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        if error_message:
            print(f"错误: {error_message}")
            print(f"命令: {command}")
            print(f"错误详情: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"错误输出: {e.stderr}")
        return False

def push_project(branch="main", commit_message="更新代码"):
    """
    推送当前项目到GitHub
    
    参数:
    - branch: 分支名称
    - commit_message: 提交消息
    """
    try:
        print("=" * 50)
        print("项目推送工具")
        print("=" * 50)
        
        # 1. 获取环境变量
        github_token = os.getenv("GITHUB_TOKEN")
        gh_username = os.getenv("GH_USERNAME")
        
        if not github_token or not gh_username:
            print("❌ 未找到GitHub配置，请确保.env文件中包含GITHUB_TOKEN和GH_USERNAME")
            return False
            
        # 2. 添加文件
        print("添加文件到Git...")
        if not run_command("git add .", "添加文件失败"):
            return False
        print("✅ 文件添加成功")
        
        # 3. 提交更改
        print("\n提交更改...")
        if not run_command(f'git commit -m "{commit_message}"', "提交更改失败"):
            return False
        print("✅ 更改提交成功")
        
        # 4. 获取远程仓库URL并更新为带token的URL
        try:
            result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
            repo_url = result.stdout.strip()
            
            if "https://" in repo_url:
                token_url = repo_url.replace("https://", f"https://{gh_username}:{github_token}@")
                run_command(f"git remote set-url origin {token_url}", "设置远程URL失败")
                print("✅ 已配置带Token的远程URL")
        except Exception as e:
            print(f"⚠️ 获取/设置远程URL时出错: {str(e)}")
            return False
        
        # 5. 推送到GitHub
        print("\n推送到GitHub...")
        if not run_command(f"git push -u origin {branch}", "推送到GitHub失败"):
            return False
        print("✅ 推送成功")
        
        # 6. 如果修改了远程URL，改回原来的URL
        if "https://" in repo_url:
            run_command(f"git remote set-url origin {repo_url}", "重置远程URL失败")
        
        print("\n" + "=" * 50)
        print("✨ 成功! 项目已推送到GitHub")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 推送过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 推送到main分支
    push_project() 
