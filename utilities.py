"""
功能: 项目工具函数
"""

from pathlib import Path
from datetime import datetime
import logging
import json
from typing import Union, Dict, Any, Optional, List, Callable
import csv
import os
import base64
from urllib.parse import urlparse, parse_qs

# 项目根目录 - 修改为当前脚本所在目录
ROOT_DIR = Path(__file__).parent

# 数据目录结构
DATA_DIR = ROOT_DIR / "data"
CRAWLER_DIR = DATA_DIR / "crawler"  # 爬虫数据目录
API_DIR = CRAWLER_DIR / "api"  # API数据目录
DEBUG_DIR = CRAWLER_DIR / "debug"  # 调试数据目录

# 日志目录
LOG_DIR = ROOT_DIR / "logs"


class PathManager:
    """路径管理器"""

    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """确保目录存在"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_debug_dirs(timestamp: Optional[str] = None) -> Dict[str, Path]:
        """获取调试目录"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d")

        debug_date_dir = DEBUG_DIR / timestamp
        return {
            "logs": debug_date_dir / "logs",
            "screenshots": debug_date_dir / "screenshots",
            "html": debug_date_dir / "html",
        }

    @staticmethod
    def get_api_dir(version_name: str) -> Path:
        """获取API数据目录"""
        return API_DIR / version_name


class FileManager:
    """文件管理器"""

    @staticmethod
    def save_json(
        data: Any, filepath: Union[str, Path], ensure_ascii: bool = False
    ) -> None:
        """保存JSON数据"""
        filepath = Path(filepath)
        PathManager.ensure_dir(filepath.parent)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=2)

    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Any:
        """加载JSON数据"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


class LogManager:
    """日志管理器"""

    @staticmethod
    def setup_logging(debug_dirs: Dict[str, Path]) -> logging.Logger:
        """设置日志"""
        # 确保日志目录存在
        for dir_path in debug_dirs.values():
            PathManager.ensure_dir(dir_path)

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                # 主日志文件
                logging.FileHandler(
                    debug_dirs["logs"] / "crawler.log", encoding="utf-8"
                ),
                # 调试日志文件
                logging.FileHandler(
                    debug_dirs["logs"]
                    / f"debug_{datetime.now().strftime('%H%M%S')}.log",
                    encoding="utf-8",
                ),
                # 控制台输出
                logging.StreamHandler(),
            ],
        )

        return logging.getLogger(__name__)


class PlaywrightRequestManager:
    """Playwright 请求管理器"""

    @staticmethod
    async def extract_request_data(request) -> Dict:
        """
        功能: 从 Playwright 请求对象中提取数据

        输入:
        - request: Playwright 请求对象

        返回值:
        - 请求相关的所有数据
        """
        try:
            # 获取请求头
            headers = request.headers

            # 获取请求体
            post_data = None
            if request.post_data:
                try:
                    post_data = json.loads(request.post_data)
                except:
                    post_data = request.post_data

            # 解析URL参数
            parsed_url = urlparse(request.url)
            query_params = parse_qs(parsed_url.query)

            # 获取响应数据
            response = await request.response()
            response_data = None
            if response:
                try:
                    response_data = await response.json()
                except:
                    try:
                        response_data = await response.text()
                    except:
                        response_data = "无法解析的响应数据"

            # 构建cURL命令
            curl_command = f"curl -X {request.method} '{request.url}'"
            for header_name, header_value in headers.items():
                curl_command += f" -H '{header_name}: {header_value}'"
            if post_data:
                if isinstance(post_data, dict):
                    curl_command += f" -d '{json.dumps(post_data)}'"
                else:
                    curl_command += f" -d '{post_data}'"

            # 构建fetch命令
            fetch_command = f"fetch('{request.url}', {{\n"
            fetch_command += f"  method: '{request.method}',\n"
            fetch_command += f"  headers: {json.dumps(headers, indent=2)},\n"
            if post_data:
                fetch_command += f"  body: {json.dumps(post_data, indent=2)},\n"
            fetch_command += "});"

            return {
                "url": request.url,
                "method": request.method,
                "headers": headers,
                "query_params": query_params,
                "body_data": post_data,
                "response": response_data,
                "curl_command": curl_command,
                "fetch_command": fetch_command,
                "resource_type": request.resource_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": response.status if response else None,
                "status_text": response.status_text if response else None,
            }

        except Exception as e:
            return {
                "url": request.url,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    @staticmethod
    def create_request_filter(
        url_patterns: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None,
    ) -> Callable:
        """
        功能: 创建请求过滤器

        输入:
        - url_patterns: URL匹配模式列表
        - resource_types: 资源类型列表

        返回值:
        - 过滤函数
        """

        def filter_request(request) -> bool:
            # 检查资源类型
            if resource_types and request.resource_type not in resource_types:
                return False

            # 检查URL模式
            if url_patterns:
                return any(pattern in request.url for pattern in url_patterns)

            return True

        return filter_request

    @staticmethod
    async def save_har_data(
        context, filepath: Union[str, Path], include_sensitive: bool = False
    ) -> None:
        """
        功能: 保存HAR数据

        输入:
        - context: Playwright 上下文对象
        - filepath: 保存路径
        - include_sensitive: 是否包含敏感数据
        """
        har_path = Path(filepath)
        PathManager.ensure_dir(har_path.parent)

        await context.har.save(path=str(har_path), include_sensitive=include_sensitive)


class APIDataManager:
    """API数据管理器"""

    @staticmethod
    def save_api_data(
        page_url: str,
        api_data: List[Dict],
        format_type: str = "json",
        timestamp: Optional[str] = None,
    ) -> Path:
        """
        功能: 保存API请求数据

        输入:
        - page_url: 页面URL
        - api_data: API数据列表
        - format_type: 输出格式 (仅支持json)
        - timestamp: 时间戳

        返回值:
        - 保存文件的路径
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 从URL中提取页面名称
        page_name = page_url.split("/")[-1].replace("#", "").replace("/", "_")
        if not page_name:
            page_name = "index"

        # 确保输出目录存在
        output_dir = DATA_DIR / "pages"
        PathManager.ensure_dir(output_dir)

        # 只保存JSON格式
        output_file = output_dir / f"{page_name}_api_{timestamp}.json"
        FileManager.save_json(api_data, output_file)

        return output_file

    @staticmethod
    def format_request_data(request_data: Dict) -> Dict:
        """
        功能: 格式化请求数据

        输入:
        - request_data: 原始请求数据

        返回值:
        - 格式化后的请求数据
        """
        return {
            "url": request_data.get("url", ""),
            "method": request_data.get("method", ""),
            "headers": request_data.get("headers", {}),
            "query_params": request_data.get("query_params", {}),
            "body_data": request_data.get("body_data", {}),
            "response": request_data.get("response", {}),
            "curl_command": request_data.get("curl_command", ""),
            "fetch_command": request_data.get("fetch_command", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def filter_api_data(
        api_data: List[Dict],
        url_pattern: Optional[str] = None,
        method: Optional[str] = None,
    ) -> List[Dict]:
        """
        功能: 过滤API数据

        输入:
        - api_data: API数据列表
        - url_pattern: URL匹配模式
        - method: 请求方法

        返回值:
        - 过滤后的API数据列表
        """
        filtered_data = api_data

        if url_pattern:
            filtered_data = [
                data for data in filtered_data if url_pattern in data.get("url", "")
            ]

        if method:
            filtered_data = [
                data
                for data in filtered_data
                if data.get("method", "").upper() == method.upper()
            ]

        return filtered_data


# 创建基础目录
for path in [DATA_DIR, CRAWLER_DIR, API_DIR, DEBUG_DIR, LOG_DIR]:
    PathManager.ensure_dir(path)
