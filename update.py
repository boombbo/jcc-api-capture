#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
功能: 简单的项目更新脚本
日期: 2025-03-02
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote

# 加载环境变量
load_dotenv()

def get_git_remote_url():
    """获取并更新远程仓库URL，使用token认证"""
    try:
        # 获取原始URL
        try:
            result = subprocess.run("git remote get-url origin", shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                encoding='utf-8')
            original_url = result.stdout.strip()
        except subprocess.CalledProcessError:
            print("⚠️ 无法获取远程仓库URL，将使用默认URL")
            # 使用默认URL
            original_url = "https://github.com/boombbo/jcc-api-capture.git"
        
        # 获取环境变量
        github_token = os.getenv("GITHUB_TOKEN")
        gh_username = os.getenv("GH_USERNAME")
        
        if not github_token or not gh_username:
            print("❌ 未找到GitHub配置，请确保.env文件中包含GITHUB_TOKEN和GH_USERNAME")
            return original_url, original_url
            
        # 构建带token的URL
        if "https://" in original_url:
            # 对token进行URL编码，确保没有特殊字符
            encoded_token = quote(github_token.strip())
            # 移除URL中可能的尾部斜杠
            clean_url = original_url.rstrip('/')
            token_url = clean_url.replace(
                "https://", 
                f"https://{gh_username.strip()}:{encoded_token}@"
            )
            return original_url, token_url
            
        return original_url, original_url
    except Exception as e:
        print(f"❌ 处理仓库URL时发生错误: {str(e)}")
        return original_url, original_url

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding='utf-8')
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)

def setup_git_config():
    """设置Git配置"""
    gh_username = os.getenv("GH_USERNAME")
    gh_email = os.getenv("GH_EMAIL")
    
    if gh_username and gh_email:
        run_command(f'git config --global user.name "{gh_username}"')
        run_command(f'git config --global user.email "{gh_email}"')
        print("✅ Git用户信息已配置")
    else:
        print("⚠️ 未找到Git用户配置信息")

def update_project(commit_message="更新代码", force_push=False):
    """
    更新项目并推送到GitHub
    
    参数:
    - commit_message: 提交信息
    - force_push: 是否强制推送
    """
    try:
        print("=" * 50)
        print("项目更新工具")
        print("=" * 50)
        
        # 1. 设置Git配置
        setup_git_config()
        
        # 2. 获取远程仓库URL
        original_url, token_url = get_git_remote_url()
        if token_url != original_url:
            run_command(f'git remote set-url origin "{token_url}"')
        
        # 3. 只添加指定的脚本文件，而不是所有更改
        print("\n添加更改...")
        script_files = [
            "api_capture.py",
            "github_push.py",
            "update.bat",
            "README.md",
            "requirements.txt",
            "update.py",
            "utilities.py",
            ".gitignore"
        ]
        
        # 逐个添加文件
        for file in script_files:
            if os.path.exists(file):
                success, output = run_command(f'git add "{file}"')
                if not success:
                    print(f"❌ 添加文件 {file} 失败: {output}")
        
        # 4. 检查是否有更改
        success, status = run_command("git status --porcelain")
        if not success:
            print(f"❌ 检查状态失败: {status}")
            return False
        
        if not status.strip():
            print("✨ 没有需要更新的内容")
            return True
        
        # 5. 提交更改
        print("\n提交更改...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_message = f"{commit_message} ({timestamp})"
        success, output = run_command(f'git commit -m "{full_message}"')
        if not success:
            print(f"❌ 提交失败: {output}")
            return False
        print("✅ 提交成功")
        
        # 6. 推送到GitHub
        print("\n推送到GitHub...")
        
        # 根据是否强制推送选择命令
        if force_push:
            print("使用强制推送...")
            push_command = "git push --force origin main"
        else:
            push_command = "git push origin main"
            
        success, output = run_command(push_command)
        if not success:
            print(f"❌ 推送失败: {output}")
            
            if not force_push:
                print("\n尝试使用强制推送...")
                success, output = run_command("git push --force origin main")
                if not success:
                    print(f"❌ 强制推送失败: {output}")
                    return False
            else:
                return False
        
        print("✅ 推送成功")
        
        # 7. 恢复原始URL
        if token_url != original_url:
            run_command(f'git remote set-url origin "{original_url}"')
        
        print("\n" + "=" * 50)
        print("✨ 更新完成！GitHub Actions将自动处理版本更新和发布。")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    # 获取命令行参数
    commit_message = "更新项目代码"
    force_push = False
    
    if len(sys.argv) > 1:
        commit_message = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2].lower() in ['force', '--force', '-f', 'true']:
        force_push = True
    
    update_project(commit_message, force_push)
