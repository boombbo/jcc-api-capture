#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
功能: 使用Playwright监听网络请求并提取API信息
作者: 中国红客联盟技术团队
日期: 2023-07-10
"""

import asyncio
import json
import re
import csv
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from playwright.async_api import async_playwright
import aiofiles

# 导入工具类
from utilities import (
    PathManager, 
    FileManager, 
    APIDataManager, 
    LogManager, 
    ROOT_DIR,
    DATA_DIR,
    API_DIR
)


class APICapture:
    def __init__(self):
        self.target_url = "https://jcc.qq.com"
        self.requests_data = []
        
        # 使用utilities.py中定义的路径
        self.data_dir = DATA_DIR
        self.api_base_dir = API_DIR
        
        # 版本目录定义
        self.version_dirs = {
            "4": self.api_base_dir / "天选福星",
            "13": self.api_base_dir / "双城传说II",
        }
        
        # 获取当前时间戳用于文件命名
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 日志设置
        self.log_dir = ROOT_DIR / "logs"
        PathManager.ensure_dir(self.log_dir)
        self.logger = self._setup_logger()

        # API配置
        self.api_config = {
            "chess": {
                "pattern": r"chess\.js",
                "description": "英雄数据",
                "required": True,
                "urls": [],
                "save_dir": "hero",
            },
            "race": {
                "pattern": r"race\.js",
                "description": "种族数据",
                "required": True,
                "urls": [],
                "save_dir": "synergy",
            },
            "job": {
                "pattern": r"job\.js",
                "description": "职业数据",
                "required": True,
                "urls": [],
                "save_dir": "synergy",
            },
            "trait": {
                "pattern": r"trait\.js",
                "description": "羁绊数据",
                "required": True,
                "urls": [],
                "save_dir": "synergy",
            },
            "hex": {
                "pattern": r"hex\.js",
                "description": "海克斯数据",
                "required": True,
                "urls": [],
                "save_dir": "hex",
            },
            "equip": {
                "pattern": r"(equip\.js|equipment\.js|items\.js)",
                "description": "装备数据",
                "required": True,
                "urls": [],
                "backup_urls": [
                    "https://game.gtimg.cn/images/lol/act/jkzlk/js/equip/equip.js",
                    "https://jcc.qq.com/images/lol/act/jkzlk/js/equip/equip.js",
                ],
                "selectors": [".equipment-list", ".equip-list", "#equipment-container"],
                "save_dir": "equipment",
            },
            "lineup": {
                "pattern": r"lineup_detail_total\.json",
                "description": "阵容数据",
                "required": True,
                "urls": [],
                "versions": {"4": "天选福星", "13": "双城传说II"},
                "save_dir": "lineup",
            },
            "version": {
                "pattern": r"version.*\.js",
                "description": "版本数据",
                "required": False,
                "urls": [],
                "save_dir": "common",
            },
            "rank": {
                "pattern": r"rank\.js",
                "description": "段位数据",
                "required": True,
                "urls": [],
                "save_dir": "common",
            },
            "other": {
                "pattern": r".*",  # 捕获其他所有API
                "description": "其他API数据",
                "required": False,
                "urls": [],
                "save_dir": "misc", 
            }
        }

        # 添加版本配置
        self.version_config = {
            "4": {
                "name": "天选福星",
                "mode": "4",
                "base_url": "/4/14.13.6-S14/",
                "lineup_url": "/m14/11/4/",
                "selector": ".tab-bar a:nth-child(1)",
            },
            "13": {
                "name": "双城传说II",
                "mode": "13",
                "base_url": "/13/14.13.6-S14/",
                "lineup_url": "/m14/11/13/",
                "selector": ".tab-bar a:nth-child(2)",
            },
        }
        
        # URL列表
        self.urls_to_visit = [
            "https://jcc.qq.com/#/index",
            "https://jcc.qq.com/#/lineup",
            "https://jcc.qq.com/#/hero",
            "https://jcc.qq.com/#/hex",
            "https://jcc.qq.com/#/synergy",
            "https://jcc.qq.com/#/quipment"
        ]
        
        # 按页面分类存储的请求数据
        self.page_requests = {}
        
        # 按版本分类存储的请求数据
        self.version_requests = {
            "4": [],  # 天选福星
            "13": [], # 双城传说II
            "common": []  # 共通API
        }
        
        # 确保所有目录存在
        self._create_directories()

    def _create_directories(self):
        """
        功能: 创建所有必要的目录结构
        
        步骤:
        1. 创建版本目录: 为每个游戏版本创建目录
        2. 创建API类型目录: 为每种API类型创建子目录
        """
        # 确保版本目录存在
        for version_dir in self.version_dirs.values():
            PathManager.ensure_dir(version_dir)
            
            # 为每个版本创建API类型子目录
            for api_info in self.api_config.values():
                save_dir = api_info.get("save_dir", "misc")
                PathManager.ensure_dir(version_dir / save_dir)
                
        # 日志目录
        PathManager.ensure_dir(self.log_dir)
        
        # 创建页面数据目录
        PathManager.ensure_dir(self.data_dir / "pages")
        
        self.logger.info(f"目录结构创建完成")

    def _setup_logger(self):
        """配置日志"""
        logging_format = "%(asctime)s - %(levelname)s - %(message)s"
        log_file = self.log_dir / f"api_capture_{self.timestamp}.log"
        
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format=logging_format,
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger("APICapture")

    async def generate_curl(self, request):
        """
        功能: 生成cURL命令
        
        步骤:
        1. 获取请求的URL、方法、头信息和数据: 从请求对象中提取必要信息
        2. 构建cURL命令: 将提取的信息组装成标准的cURL命令格式
        3. 处理请求体: 如果有请求体，添加适当的参数
        
        返回值:
        - 返回格式化的cURL命令字符串
        """
        url = request.url
        method = request.method
        headers = request.headers
        
        # 开始构建cURL命令
        curl_command = f'curl -X {method} "{url}"'
        
        # 添加头信息
        for key, value in headers.items():
            curl_command += f' -H "{key}: {value}"'
        
        # 如果是POST请求且有请求体
        post_data = None
        if method == "POST" and hasattr(request, "post_data") and request.post_data:
            post_data = request.post_data
            curl_command += f" --data '{post_data}'"
        
        return curl_command

    async def generate_fetch(self, request, use_node=False):
        """
        功能: 生成fetch API调用代码
        
        步骤:
        1. 获取请求信息: 提取URL、方法、头信息和数据
        2. 构建fetch选项: 组装method、headers和body
        3. 根据平台生成不同版本: 浏览器版或Node.js版
        
        返回值:
        - 返回格式化的fetch API调用代码
        """
        url = request.url
        method = request.method
        headers = request.headers
        
        # 构建fetch选项
        options = {
            "method": method,
            "headers": headers
        }
        
        if method == "POST" and hasattr(request, "post_data") and request.post_data:
            options["body"] = request.post_data
        
        options_str = json.dumps(options, indent=2)
        
        if use_node:
            # Node.js版本
            return f"""
const fetch = require('node-fetch');

fetch("{url}", {options_str})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
"""
        else:
            # 浏览器版本
            return f"""
fetch("{url}", {options_str})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
"""

    async def extract_request_info(self, request):
        """
        功能: 提取请求的关键信息
        
        步骤:
        1. 获取基本请求信息: URL、方法、头信息
        2. 解析查询参数: 提取URL中的查询参数
        3. 获取请求体: 如果是POST请求，提取请求体
        4. 生成不同格式的请求数据: 包括cURL和fetch
        
        返回值:
        - 返回请求信息的字典
        """
        url = request.url
        method = request.method
        headers = request.headers
        
        # 解析URL获取查询参数
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 获取POST数据
        post_data = None
        if method == "POST" and hasattr(request, "post_data"):
            try:
                post_data = request.post_data
            except:
                post_data = None
        
        # 生成cURL命令
        curl_command = await self.generate_curl(request)
        
        # 生成fetch API调用
        fetch_browser = await self.generate_fetch(request, use_node=False)
        fetch_node = await self.generate_fetch(request, use_node=True)
        
        # 构建请求信息字典
        request_info = {
            "url": url,
            "method": method,
            "headers": dict(headers),
            "query_params": query_params,
            "post_data": post_data,
            "curl_command": curl_command,
            "fetch_browser": fetch_browser,
            "fetch_node": fetch_node,
            "timestamp": datetime.now().isoformat(),
            "page_url": None,  # 将在捕获响应时填充
            "version": self._detect_version(url)  # 检测版本
        }
        
        return request_info
    
    def _detect_version(self, url):
        """
        功能: 从URL中检测版本
        
        步骤:
        1. 检查URL中是否包含版本信息: 如 /4/... 或 /13/...
        2. 返回对应的版本代码或默认值
        
        返回值:
        - 版本代码 ("4", "13" 或 "common")
        """
        for version_code, version_info in self.version_config.items():
            base_url = version_info["base_url"]
            if base_url in url:
                return version_code
                
        return "common"  # 没有明确版本信息的API

    async def capture_response(self, response):
        """
        功能: 捕获响应数据
        
        步骤:
        1. 获取响应的请求对象: 从响应中提取请求信息
        2. 提取基本响应信息: 状态码、头信息
        3. 尝试获取响应体: 根据内容类型处理响应数据
        4. 将响应信息添加到请求数据中
        
        返回值:
        - 无直接返回值，但会更新内部的requests_data列表
        """
        request = response.request
        url = request.url
        
        # 检查是否是API请求
        if not self.is_api_request(url):
            return
        
        # 提取请求信息
        request_info = await self.extract_request_info(request)
        
        # 添加当前页面信息
        # 这需要通过一个全局变量来跟踪当前页面URL
        request_info["page_url"] = getattr(self, "current_page_url", None)
        
        # 添加响应信息
        try:
            status = response.status
            headers = response.headers
            
            # 尝试获取响应体
            content_type = headers.get("content-type", "")
            response_body = None
            
            if "json" in content_type or "javascript" in content_type:
                try:
                    response_body = await response.json()
                except:
                    try:
                        text = await response.text()
                        response_body = text
                    except:
                        response_body = "<无法解析的响应体>"
            elif "text" in content_type:
                response_body = await response.text()
            
            response_info = {
                "status": status,
                "headers": dict(headers),
                "body": response_body
            }
            
            request_info["response"] = response_info
            
            # 检查是否匹配API配置
            api_matched = False
            for api_key, api_info in self.api_config.items():
                if re.search(api_info["pattern"], url):
                    request_info["api_type"] = api_key
                    request_info["api_description"] = api_info["description"]
                    request_info["save_dir"] = api_info["save_dir"]
                    if url not in api_info["urls"]:
                        api_info["urls"].append(url)
                    api_matched = True
                    break
            
            # 如果没有匹配到任何API类型，归类为"other"
            if not api_matched:
                request_info["api_type"] = "other"
                request_info["api_description"] = "其他API数据"
                request_info["save_dir"] = "misc"
            
            # 添加到请求数据列表
            self.requests_data.append(request_info)
            
            # 按页面分类
            page_url = request_info["page_url"] or "unknown"
            if page_url not in self.page_requests:
                self.page_requests[page_url] = []
            self.page_requests[page_url].append(request_info)
            
            # 按版本分类
            version = request_info["version"]
            self.version_requests[version].append(request_info)
            
            # 实时打印API捕获信息
            self.logger.info(f"捕获API: {url} [{request.method}] - 状态: {status} - 类型: {request_info.get('api_description', '未知')} - 版本: {version}")
            
        except Exception as e:
            self.logger.error(f"处理响应时出错: {url} - {str(e)}")

    def is_api_request(self, url):
        """
        功能: 判断URL是否为API请求
        
        步骤:
        1. 检查URL是否包含API相关关键词: 如api、json、js等
        2. 检查URL是否匹配预定义的API模式
        
        返回值:
        - 如果是API请求返回True，否则返回False
        """
        # 检查是否包含API相关关键词
        api_keywords = ["api", "json", "data", ".js"]
        if any(keyword in url.lower() for keyword in api_keywords):
            return True
        
        # 检查是否匹配预定义的API模式
        for api_info in self.api_config.values():
            if re.search(api_info["pattern"], url):
                return True
        
        return False

    async def save_results(self):
        """
        功能: 保存捕获的结果
        
        步骤:
        1. 按版本保存: 将数据保存到对应的版本目录
        2. 按API类型保存: 将数据按API类型分类保存
        3. 只保存JSON格式: 简化数据保存结构
        
        返回值:
        - 无直接返回值，但会创建输出文件
        """
        self.logger.info("开始保存API数据...")
        
        # 保存总体数据（所有API请求）
        all_data_file = self.data_dir / f"all_api_requests_{self.timestamp}.json"
        FileManager.save_json(self.requests_data, all_data_file)
        self.logger.info(f"所有API请求数据已保存到: {all_data_file}")
        
        # 按版本保存数据
        for version, requests in self.version_requests.items():
            if not requests:
                continue
                
            version_name = next((info["name"] for code, info in self.version_config.items() 
                                if code == version), "通用")
            version_dir = self.version_dirs.get(version, self.api_base_dir / "common")
            
            # 按API类型分组
            api_type_requests = {}
            for req in requests:
                api_type = req.get("api_type", "other")
                if api_type not in api_type_requests:
                    api_type_requests[api_type] = []
                api_type_requests[api_type].append(req)
            
            # 保存每种API类型的数据
            for api_type, type_requests in api_type_requests.items():
                # 获取保存目录
                save_dir = self.api_config.get(api_type, {}).get("save_dir", "misc")
                
                # 构建完整保存路径
                save_path = version_dir / save_dir
                PathManager.ensure_dir(save_path)
                
                # 只保存JSON格式
                json_file = save_path / f"{api_type}_{self.timestamp}.json"
                FileManager.save_json(type_requests, json_file)
                
                self.logger.info(f"版本 {version_name} 的 {api_type} API数据已保存")
        
        # 保存按页面分类的数据
        for page_url, page_requests in self.page_requests.items():
            if not page_requests:
                continue
                
            # 提取页面名称
            page_name = page_url.split("/")[-1].replace("#", "").replace("/", "_")
            if not page_name:
                page_name = "index"
                
            # 保存页面API数据
            page_data_file = self.data_dir / "pages" / f"{page_name}_api_{self.timestamp}.json"
            PathManager.ensure_dir(page_data_file.parent)
            FileManager.save_json(page_requests, page_data_file)
            
            self.logger.info(f"页面 {page_name} 的API数据已保存")
        
        self.logger.info("所有结果保存完成!")

    async def run(self):
        """
        功能: 主运行函数
        
        步骤:
        1. 初始化Playwright: 创建浏览器实例和上下文
        2. 访问指定URL: 依次访问所有需监听的页面
        3. 设置网络请求监听器: 捕获所有网络请求和响应
        4. 等待页面加载: 确保页面完全加载并捕获所有请求
        5. 保存结果: 将捕获的API信息保存为不同格式
        
        返回值:
        - 无直接返回值，但会完成整个监听和捕获过程
        """
        self.logger.info("开始API捕获过程...")
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            
            # 创建页面
            page = await context.new_page()
            
            # 监听网络请求
            page.on("response", self.capture_response)
            
            # 访问每个URL
            for url in self.urls_to_visit:
                self.logger.info(f"访问页面: {url}")
                # 设置当前页面URL以便在捕获响应时使用
                self.current_page_url = url
                
                await page.goto(url, wait_until="networkidle")
                
                # 等待页面加载
                await page.wait_for_load_state("networkidle")
                
                # 等待一些额外的时间确保所有请求都被捕获
                await asyncio.sleep(2)
                
                # 尝试点击模式选择器(如果有)
                for version_key, version_info in self.version_config.items():
                    selector = version_info.get("selector")
                    if selector:
                        try:
                            self.logger.info(f"尝试切换到版本: {version_info['name']} (选择器: {selector})")
                            await page.click(selector)
                            await page.wait_for_load_state("networkidle")
                            await asyncio.sleep(2)
                            
                            # 设置当前版本
                            self.current_version = version_key
                            self.logger.info(f"成功切换到版本: {version_info['name']}")
                        except Exception as e:
                            self.logger.error(f"点击选择器 {selector} 失败: {str(e)}")
            
            # 保存结果
            await self.save_results()
            
            # 关闭浏览器
            await browser.close()
            
            self.logger.info("API捕获完成!")


async def main():
    """
    功能: 主函数
    
    步骤:
    1. 创建APICapture实例: 初始化API捕获器
    2. 运行捕获过程: 启动监听和数据提取
    
    注意事项:
    - 确保已安装所有依赖: playwright, aiofiles等
    - 首次运行需安装浏览器: playwright install chromium
    """
    api_capture = APICapture()
    await api_capture.run()


if __name__ == "__main__":
    asyncio.run(main()) 
