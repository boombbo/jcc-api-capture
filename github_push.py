#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
功能: 自动创建GitHub仓库并推送代码
作者: 中国红客联盟技术团队
日期: 2025-03-02
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
import webbrowser
import time
import re
from dotenv import load_dotenv
from github import Github, GithubException
import base64

# 加载环境变量
load_dotenv()

# 获取环境变量
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GH_USERNAME = os.getenv("GH_USERNAME")
GH_EMAIL = os.getenv("GH_EMAIL")

def run_command(command, error_message=None, capture_output=False):
    """
    运行命令并处理可能的错误
    
    参数:
    - command: 要执行的命令（字符串或列表）
    - error_message: 错误时显示的消息
    - capture_output: 是否捕获输出
    
    返回:
    - 如果capture_output为True，返回命令输出；否则返回None
    """
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   encoding='utf-8')
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        if error_message:
            print(f"错误: {error_message}")
            print(f"命令: {command}")
            print(f"错误详情: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"错误输出: {e.stderr}")
        sys.exit(1)

def check_git_installed():
    """检查Git是否已安装"""
    try:
        run_command("git --version", "Git未安装。请先安装Git: https://git-scm.com/downloads", capture_output=True)
        print("✅ Git已安装")
        return True
    except:
        return False

def setup_git_config():
    """设置Git配置"""
    if GH_USERNAME and GH_EMAIL:
        print(f"设置Git用户信息: {GH_USERNAME} <{GH_EMAIL}>")
        run_command(f'git config --global user.name "{GH_USERNAME}"', "设置Git用户名失败")
        run_command(f'git config --global user.email "{GH_EMAIL}"', "设置Git邮箱失败")
        print("✅ Git用户信息设置成功")
    else:
        # 检查是否已设置用户信息
        try:
            user_name = run_command("git config --global user.name", capture_output=True)
            user_email = run_command("git config --global user.email", capture_output=True)
            
            if not user_name or not user_email:
                print("⚠️ Git用户信息未设置，请设置后再试")
                user_name = input("请输入您的GitHub用户名: ")
                user_email = input("请输入您的GitHub邮箱: ")
                
                run_command(f'git config --global user.name "{user_name}"', "设置Git用户名失败")
                run_command(f'git config --global user.email "{user_email}"', "设置Git邮箱失败")
                print("✅ Git用户信息设置成功")
        except:
            print("⚠️ 无法获取Git用户信息")

def get_github_instance():
    """
    获取GitHub实例
    
    返回:
    - Github实例或None
    """
    if GITHUB_TOKEN:
        try:
            # 使用token创建Github实例
            g = Github(GITHUB_TOKEN)
            # 测试连接
            user = g.get_user()
            print(f"✅ 已连接到GitHub (用户: {user.login})")
            return g
        except Exception as e:
            print(f"⚠️ GitHub API连接失败: {str(e)}")
    
    print("❌ 未找到有效的GitHub Token")
    return None

def create_github_repo_api(repo_name, description, is_private=False):
    """
    使用PyGithub API创建GitHub仓库
    
    参数:
    - repo_name: 仓库名称
    - description: 仓库描述
    - is_private: 是否为私有仓库
    
    返回:
    - 仓库URL或None
    """
    g = get_github_instance()
    if not g:
        return None
    
    try:
        user = g.get_user()
        print(f"正在创建GitHub仓库: {repo_name}...")
        
        # 检查仓库是否已存在
        try:
            repo = user.get_repo(repo_name)
            print(f"⚠️ 仓库 {repo_name} 已存在")
            return repo.html_url
        except:
            # 创建新仓库
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=is_private,
                has_issues=True,
                has_wiki=True,
                has_projects=True,
                auto_init=False
            )
            print(f"✅ GitHub仓库创建成功: {repo.html_url}")
            
            # 设置远程仓库
            run_command(f"git remote add origin {repo.clone_url}", "添加远程仓库失败")
            
            return repo.html_url
    except GithubException as e:
        print(f"❌ 创建仓库失败: {e.data.get('message', str(e))}")
        return None
    except Exception as e:
        print(f"❌ 创建仓库时发生错误: {str(e)}")
        return None

def create_github_repo(repo_name, description, is_private=False):
    """
    创建GitHub仓库
    
    参数:
    - repo_name: 仓库名称
    - description: 仓库描述
    - is_private: 是否为私有仓库
    
    返回:
    - 仓库URL
    """
    # 首先尝试使用PyGithub API
    repo_url = create_github_repo_api(repo_name, description, is_private)
    if repo_url:
        return repo_url
    
    # 如果API方式失败，尝试使用GitHub CLI
    visibility = "--private" if is_private else "--public"
    
    if check_github_cli_installed() and github_login():
        # 使用GitHub CLI创建仓库
        print(f"尝试使用GitHub CLI创建仓库: {repo_name}...")
        result = run_command(
            f'gh repo create {repo_name} {visibility} --description "{description}" --source=. --remote=origin',
            f"创建仓库 {repo_name} 失败",
            capture_output=True
        )
        print("✅ GitHub仓库创建成功")
        
        # 获取仓库URL
        repo_url = run_command("git remote get-url origin", "获取仓库URL失败", capture_output=True)
        return repo_url
    else:
        # 手动方式
        print("\n由于GitHub API和CLI都失败，请按照以下步骤手动创建仓库:")
        print("1. 访问 https://github.com/new")
        print(f"2. 仓库名称输入: {repo_name}")
        print(f"3. 描述输入: {description}")
        print(f"4. 选择{'私有' if is_private else '公开'}")
        print("5. 点击'创建仓库'")
        print("6. 按照页面上的指示，将本地仓库推送到GitHub")
        
        # 打开浏览器
        webbrowser.open("https://github.com/new")
        
        # 等待用户手动创建
        repo_url = input("\n创建完成后，请输入仓库URL (例如 https://github.com/username/repo): ")
        
        # 添加远程仓库
        run_command(f"git remote add origin {repo_url}", "添加远程仓库失败")
        
        return repo_url

def check_github_cli_installed():
    """检查GitHub CLI是否已安装"""
    try:
        run_command("gh --version", "GitHub CLI未安装", capture_output=True)
        print("✅ GitHub CLI已安装")
        return True
    except:
        print("❌ GitHub CLI未安装。将使用API或手动方式创建仓库。")
        return False

def github_login():
    """登录GitHub CLI"""
    # 如果有GITHUB_TOKEN，使用token登录
    if GITHUB_TOKEN:
        try:
            # 使用环境变量设置token
            os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
            # 检查是否已登录
            auth_status = run_command("gh auth status", capture_output=True, error_message=None)
            if "Logged in to" in auth_status:
                print("✅ 已使用Token登录GitHub")
                return True
            else:
                print("使用Token登录GitHub...")
                # 使用token登录
                run_command(f'echo "{GITHUB_TOKEN}" | gh auth login --with-token', "GitHub Token登录失败")
                print("✅ GitHub Token登录成功")
                return True
        except Exception as e:
            print(f"⚠️ Token登录失败: {str(e)}")
    
    # 如果没有token或token登录失败，尝试交互式登录
    try:
        # 检查是否已登录
        auth_status = run_command("gh auth status", capture_output=True, error_message=None)
        if "Logged in to" in auth_status:
            print("✅ 已登录GitHub")
            return True
    except:
        pass
    
    print("需要登录GitHub...")
    try:
        run_command("gh auth login -w", "GitHub登录失败")
        print("✅ GitHub登录成功")
        return True
    except:
        return False

def init_git_repo():
    """初始化Git仓库"""
    # 检查是否已经是Git仓库
    if Path(".git").exists():
        print("✅ Git仓库已初始化")
        return
    
    print("初始化Git仓库...")
    run_command("git init", "Git初始化失败")
    print("✅ Git仓库初始化成功")

def add_files_to_git():
    """添加文件到Git"""
    print("添加文件到Git...")
    run_command("git add .", "添加文件失败")
    print("✅ 文件添加成功")

def commit_changes(message):
    """提交更改"""
    print("提交更改...")
    run_command(f'git commit -m "{message}"', "提交更改失败")
    print("✅ 更改提交成功")

def push_to_github(branch="main"):
    """推送到GitHub"""
    print(f"推送到GitHub ({branch}分支)...")
    
    # 如果有GITHUB_TOKEN，使用token进行推送
    if GITHUB_TOKEN and GH_USERNAME:
        # 提取仓库URL
        repo_url = run_command("git remote get-url origin", "获取仓库URL失败", capture_output=True)
        
        # 替换为带token的URL
        if "https://" in repo_url:
            # 如果是HTTPS URL，添加token
            token_url = re.sub(r'https://(.+)', f'https://{GH_USERNAME}:{GITHUB_TOKEN}@\\1', repo_url)
            run_command(f"git remote set-url origin {token_url}", "设置远程URL失败")
            print("✅ 已配置带Token的远程URL")
    
    # 推送到GitHub
    run_command(f"git push -u origin {branch}", "推送到GitHub失败")
    print("✅ 推送成功")
    
    # 如果修改了远程URL，改回原来的URL
    if GITHUB_TOKEN and GH_USERNAME and "https://" in repo_url:
        run_command(f"git remote set-url origin {repo_url}", "重置远程URL失败")

def setup_github_pages_api():
    """使用PyGithub API设置GitHub Pages"""
    g = get_github_instance()
    if not g:
        return False
    
    try:
        # 获取当前仓库名称
        remote_url = run_command("git remote get-url origin", "获取仓库URL失败", capture_output=True)
        repo_name = remote_url.split("/")[-1].replace(".git", "")
        user_name = remote_url.split("/")[-2].split(":")[-1]
        
        # 获取仓库
        repo = g.get_user().get_repo(repo_name)
        
        # 启用GitHub Pages
        print("设置GitHub Pages...")
        repo.enable_pages(source={"branch": "main", "path": "/"})
        print(f"✅ GitHub Pages设置成功: https://{user_name}.github.io/{repo_name}/")
        return True
    except Exception as e:
        print(f"⚠️ 设置GitHub Pages失败: {str(e)}")
        return False

def setup_github_pages():
    """设置GitHub Pages"""
    # 首先尝试使用PyGithub API
    if setup_github_pages_api():
        return
    
    # 如果API方式失败，尝试使用GitHub CLI
    if check_github_cli_installed() and github_login():
        print("尝试使用GitHub CLI设置GitHub Pages...")
        try:
            run_command("gh api repos/:owner/:repo/pages -F build_type=workflow", 
                       "设置GitHub Pages失败", capture_output=True)
            print("✅ GitHub Pages设置成功")
        except:
            print("⚠️ GitHub Pages设置失败，请手动设置")
    else:
        print("\n要设置GitHub Pages，请按照以下步骤操作:")
        print("1. 访问仓库设置页面")
        print("2. 点击'Pages'选项")
        print("3. 在'Source'下选择'GitHub Actions'")

def create_readme_if_not_exists():
    """如果README.md不存在，则创建"""
    if not Path("README.md").exists():
        print("创建README.md...")
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# JCC API接口监听与分析工具\n\n")
            f.write("这是一款基于Playwright的高级网络请求监听工具，专门设计用于捕获并分析jcc.qq.com网站上的所有API接口。\n")
        print("✅ README.md创建成功")

def ensure_gitignore_has_env():
    """确保.gitignore文件包含.env"""
    gitignore_path = Path(".gitignore")
    
    # 如果.gitignore不存在，创建它
    if not gitignore_path.exists():
        print("创建.gitignore文件...")
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("# 环境变量\n.env\n\n")
            f.write("# Python\n__pycache__/\n*.py[cod]\n*$py.class\n")
        print("✅ .gitignore文件创建成功")
        return
    
    # 检查.gitignore是否已包含.env
    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if ".env" not in content:
        print("更新.gitignore文件，添加.env...")
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\n# 环境变量\n.env\n")
        print("✅ .gitignore文件更新成功")

def create_workflow_file():
    """创建GitHub Actions工作流文件"""
    workflow_dir = Path(".github/workflows")
    workflow_file = workflow_dir / "python-app.yml"
    
    if workflow_file.exists():
        print("✅ GitHub Actions工作流文件已存在")
        return
    
    print("创建GitHub Actions工作流文件...")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    with open(workflow_file, "w", encoding="utf-8") as f:
        f.write("""name: Python Application

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        
    - name: Install Playwright browsers
      run: |
        if grep -q "playwright" requirements.txt; then
          python -m playwright install chromium
        fi
        
    - name: Lint with flake8
      run: |
        pip install flake8
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        
    - name: Check code formatting with black
      run: |
        pip install black
        black --check . || echo "Code formatting issues found. Consider running 'black .' locally."
""")
    print("✅ GitHub Actions工作流文件创建成功")

def process_github_workflow(repo_name="jcc-api-capture", 
                          description="腾讯JCC API接口监听与分析工具",
                          is_private=False,
                          commit_message="初始提交",
                          branch="main",
                          setup_pages=False):
    """
    整合的GitHub工作流程函数
    
    参数:
    - repo_name: 仓库名称
    - description: 仓库描述
    - is_private: 是否为私有仓库
    - commit_message: 提交消息
    - branch: 分支名称
    - setup_pages: 是否设置GitHub Pages
    
    返回:
    - 仓库URL或None（如果失败）
    """
    try:
        print("=" * 50)
        print("GitHub仓库创建和代码推送工具")
        print("=" * 50)
        
        # 1. 检查Git安装
        if not check_git_installed():
            print("请先安装Git: https://git-scm.com/downloads")
            return None
        
        # 2. 设置Git配置
        setup_git_config()
        
        # 3. 初始化Git仓库
        init_git_repo()
        
        # 4. 创建必要文件
        create_readme_if_not_exists()
        ensure_gitignore_has_env()
        create_workflow_file()
        
        # 5. Git操作
        add_files_to_git()
        commit_changes(commit_message)
        
        # 6. 创建并推送到GitHub
        repo_url = create_github_repo(repo_name, description, is_private)
        if not repo_url:
            print("❌ 创建GitHub仓库失败")
            return None
            
        push_to_github(branch)
        
        # 7. 设置GitHub Pages（如果需要）
        if setup_pages:
            setup_github_pages()
        
        print("\n" + "=" * 50)
        print(f"✨ 成功! 仓库已创建并推送到: {repo_url}")
        print("=" * 50)
        
        # 8. 打开浏览器访问仓库
        webbrowser.open(repo_url)
        
        return repo_url
        
    except Exception as e:
        print(f"❌ 工作流程执行失败: {str(e)}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GitHub仓库创建和代码推送工具")
    parser.add_argument("--name", default="jcc-api-capture", help="GitHub仓库名称")
    parser.add_argument("--desc", default="腾讯JCC API接口监听与分析工具", help="仓库描述")
    parser.add_argument("--private", action="store_true", help="创建私有仓库")
    parser.add_argument("--message", default="初始提交", help="提交消息")
    parser.add_argument("--branch", default="main", help="分支名称")
    parser.add_argument("--setup-pages", action="store_true", help="设置GitHub Pages")
    
    args = parser.parse_args()
    
    # 使用整合的工作流程函数
    process_github_workflow(
        repo_name=args.name,
        description=args.desc,
        is_private=args.private,
        commit_message=args.message,
        branch=args.branch,
        setup_pages=args.setup_pages
    )

if __name__ == "__main__":
    main() 
