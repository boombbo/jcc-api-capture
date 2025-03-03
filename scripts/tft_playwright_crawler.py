"""
功能: 捕获游戏API请求并保存所有复制格式
"""

import asyncio
from playwright.async_api import async_playwright
import json
import logging
from datetime import datetime
import os
from pathlib import Path
import re
from typing import Dict, List, Optional
from scripts.data_version_manager import DataVersionManager
from update_logger import UpdateLogger

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class APICapture:
    def __init__(self):
        self.target_url = "https://jcc.qq.com"
        self.requests_data = []

        # 设置数据目录
        self.base_dir = Path("data/crawler")
        self.api_dir = {
            "4": self.base_dir / "api" / "天选福星",
            "13": self.base_dir / "api" / "双城传说II",
        }
        self.create_directories()

        # API配置
        self.api_config = {
            "chess": {
                "pattern": r"chess\.js",
                "description": "英雄数据",
                "required": True,
                "urls": [],
            },
            "race": {
                "pattern": r"race\.js",
                "description": "种族数据",
                "required": True,
                "urls": [],
            },
            "job": {
                "pattern": r"job\.js",
                "description": "职业数据",
                "required": True,
                "urls": [],
            },
            "trait": {
                "pattern": r"trait\.js",
                "description": "羁绊数据",
                "required": True,
                "urls": [],
            },
            "hex": {
                "pattern": r"hex\.js",
                "description": "海克斯数据",
                "required": True,
                "urls": [],
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
                "transform": """
                    function transformEquipData(data) {
                        if (typeof data === 'string') {
                            try {
                                // 移除变量声明
                                data = data.replace(/^var\s+\w+\s*=\s*/, ''); # type: ignore # type: ignore
                                // 移除结尾分号
                                data = data.replace(/;?\s*$/, '');
                                // 处理单引号
                                data = data.replace(/'/g, '"');
                                // 处理属性名的引号
                                data = data.replace(/([{,]\s*)(\w+):/g, '$1"$2":');

                                return JSON.parse(data);
                            } catch(e) {
                                console.error('转换装备数据失败:', e);

                                // 尝试提取JSON对象
                                const match = data.match(/\{[\s\S]*\}/);
                                if (match) {
                                    try {
                                        return JSON.parse(match[0]);
                                    } catch(e2) {
                                        console.error('提取JSON失败:', e2);
                                    }
                                }
                                return null;
                            }
                        }
                        return data;
                    }
                """,
            },
            "lineup": {
                "pattern": r"lineup_detail_total\.json",
                "description": "阵容数据",
                "required": True,
                "urls": [],
                "versions": {"4": "天选福星", "13": "双城传说II"},
            },
            "version": {
                "pattern": r"version.*\.js",
                "description": "版本数据",
                "required": False,
                "urls": [],
            },
            "rank": {
                "pattern": r"rank\.js",
                "description": "段位数据",
                "required": True,
                "urls": [],
                "transform": """
                    function transformRankData(data) {
                        if (typeof data === 'string') {
                            try {
                                data = data.replace(/^var\s+\w+\s*=\s*/, '');
                                data = data.replace(/;?\s*$/, '');
                                data = data.replace(/'/g, '"');
                                data = data.replace(/([{,]\s*)(\w+):/g, '$1"$2":');
                                return JSON.parse(data);
                            } catch(e) {
                                console.error('转换段位数据失败:', e);
                                const match = data.match(/\{[\s\S]*\}/);
                                if (match) {
                                    try {
                                        return JSON.parse(match[0]);
                                    } catch(e2) {
                                        console.error('提取JSON失败:', e2);
                                    }
                                }
                                return null;
                            }
                        }
                        return data;
                    }
                """,
            },
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

        # 修改页面访问配置
        self.pages_to_visit = [
            {
                "path": "/#/lineup",
                "expected_apis": {
                    "version",
                    "chess",
                    "race",
                    "job",
                    "trait",
                    "equip",
                    "hex",
                    "lineup",
                },
                "wait_for": [".lineup-detail", ".lineup-list", "#lineup-container"],
                "timeout": 10000,
                "actions": [
                    # 第一步：等待页面加载
                    {
                        "type": "wait_for_selector",
                        "selector": "#gWrap > div > div > div.lineup-content > div > div > div > div.list-container > div.head-option > div.tab-bar",
                        "timeout": 5000,
                    },
                    {"type": "wait", "time": 2000},
                    # 第二步：切换到双城传说II
                    {
                        "type": "click",
                        "selector": "#gWrap > div > div > div.lineup-content > div > div > div > div.list-container > div.head-option > div.tab-bar > a:nth-child(2)",
                        "description": "切换到双城传说II标签",
                    },
                    {"type": "wait", "time": 3000},
                    # 第三步：等待双城传说II数据加载
                    {
                        "type": "wait_for_selector",
                        "selector": "div.lineup-box",
                        "timeout": 5000,
                    },
                    {"type": "wait", "time": 2000},
                    # 第四步：切换到天选福星
                    {
                        "type": "click",
                        "selector": "#gWrap > div > div > div.lineup-content > div > div > div > div.list-container > div.head-option > div.tab-bar > a:nth-child(1)",
                        "description": "切换到天选福星标签",
                    },
                    {"type": "wait", "time": 3000},
                    # 第五步：等待天选福星数据加载
                    {
                        "type": "wait_for_selector",
                        "selector": "div.lineup-box",
                        "timeout": 5000,
                    },
                    {"type": "wait", "time": 2000},
                ],
            },
            {
                "path": "/#/index",
                "expected_apis": {
                    "version",
                    "chess",
                    "race",
                    "job",
                    "trait",
                    "equip",
                    "hex",
                },
                "wait_for": [".home-container", ".version-info", "#index-container"],
                "timeout": 8000,
                "actions": [
                    {
                        "type": "wait_for_selector",
                        "selector": ".home-container",
                        "timeout": 5000,
                    },
                    {"type": "scroll", "y": 800},
                    {"type": "wait", "time": 2000},
                ],
            },
            {
                "path": "/#/rank/list",
                "expected_apis": {
                    "version",
                    "rank",
                },
                "wait_for": [".rank-list-container", "#rank-list"],
                "timeout": 8000,
                "actions": [
                    {
                        "type": "wait_for_selector",
                        "selector": ".rank-list-container",
                        "timeout": 5000,
                    },
                    {"type": "scroll", "y": 500},
                    {"type": "wait", "time": 2000},
                ],
            },
            {
                "path": "/#/rank/tier",
                "expected_apis": {
                    "version",
                    "rank",
                },
                "wait_for": [".rank-tier-container", "#rank-tier"],
                "timeout": 8000,
                "actions": [
                    {
                        "type": "wait_for_selector",
                        "selector": ".rank-tier-container",
                        "timeout": 5000,
                    },
                    {"type": "scroll", "y": 500},
                    {"type": "wait", "time": 2000},
                ],
            },
            {
                "path": "/#/champion",
                "expected_apis": {
                    "version",
                    "chess",
                    "race",
                    "job",
                    "trait",
                },
                "wait_for": [".champion-container", "#champion-list"],
                "timeout": 10000,
                "actions": [
                    {
                        "type": "wait_for_selector",
                        "selector": ".champion-container",
                        "timeout": 5000,
                    },
                    {"type": "scroll", "y": 800},
                    {"type": "wait", "time": 2000},
                ],
            },
        ]

        # 添加计数器和等待时间
        self.required_apis_count = len(
            [api for api in self.api_config.values() if api["required"]]
        )
        self.captured_required_apis = set()
        self.max_wait_time = 30  # 最大等待时间(秒)

        # 增加数据验证配置
        self.data_validators = {
            "chess": lambda data: isinstance(data, dict) and "data" in data,
            "race": lambda data: isinstance(data, dict) and "data" in data,
            "job": lambda data: isinstance(data, dict) and "data" in data,
            "trait": lambda data: isinstance(data, dict) and "data" in data,
            "hex": lambda data: isinstance(data, dict) and "data" in data,
            "equip": lambda data: isinstance(data, dict) and "data" in data,
            "rank": lambda data: isinstance(data, dict) and "data" in data,
        }

        # 改进重试配置
        self.retry_config = {
            "max_retries": 2,
            "retry_delay": 2000,
            "network_timeout": 30000,
            "page_load_timeout": 60000,
        }

        # 修改错误恢复配置
        self.recovery_config = {
            "max_browser_restarts": 3,  # 增加重启次数
            "restart_delay": 10000,  # 增加重启等待时间
            "clear_cache": True,
            "force_https": True,
        }

        # 修改数据处理器
        self.data_processors = {
            "lineup": self._process_lineup_data,
            "chess": self._process_chess_data,
            "equip": self._process_equip_data,
            "rank": self._process_rank_data,
            # ... 其他处理器
        }

        self.version_manager = DataVersionManager()
        self.update_logger = UpdateLogger()

        # 添加版本信息缓存
        self.version_cache = {}

    def create_directories(self):
        """创建数据目录"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for version_dir in self.api_dir.values():
            version_dir.mkdir(parents=True, exist_ok=True)

    def is_api_request(self, url: str) -> Optional[str]:
        """判断是否为API请求并返回API名称"""
        for api_name, config in self.api_config.items():
            if re.search(config["pattern"], url):
                config["urls"].append(url)  # 记录URL
                return api_name
        return None

    async def capture_network(self, page):
        """捕获网络请求"""

        async def handle_request(route, request):
            try:
                api_name = self.is_api_request(request.url)
                if request.resource_type in ["fetch", "xhr", "script"] and api_name:
                    logger.info(f"捕获API请求: {api_name} - {request.url}")
                    if self.api_config[api_name]["required"]:
                        self.captured_required_apis.add(api_name)
                    self.requests_data.append(
                        {
                            "api_name": api_name,
                            "request": request,
                            "formats": self._generate_copy_formats(request),
                            "response_data": None,
                        }
                    )
                await route.continue_()
            except Exception as e:
                logger.error(f"处理请求出错: {str(e)}")
                await route.continue_()

        async def handle_response(response):
            try:
                api_name = self.is_api_request(response.url)
                if (
                    response.request.resource_type in ["fetch", "xhr", "script"]
                    and api_name
                ):
                    response_data = await self._parse_response(response)

                    # 更新请求数据
                    for req_data in self.requests_data:
                        if req_data["request"].url == response.url:
                            req_data["response_data"] = response_data
                            req_data["formats"].update(
                                self._generate_copy_formats(
                                    response.request, response_data
                                )
                            )
                            logger.info(f"已获取响应: {api_name}")
                            break
            except Exception as e:
                logger.error(f"处理响应出错: {str(e)}")

        await page.route("**/*", handle_request)
        page.on("response", handle_response)

    async def _parse_response(self, response):
        """解析响应数据"""
        try:
            text = await response.text()
            try:
                # 尝试解析为JSON
                json_data = json.loads(text)
            except:
                # 处理JavaScript文件
                if "window.__DATA__" in text:
                    json_str = text.split("window.__DATA__=")[1].split(";")[0]
                    json_data = json.loads(json_str)
                else:
                    # 提取JS中的JSON数据
                    start = text.find("{")
                    end = text.rfind("}")
                    if start >= 0 and end > start:
                        json_data = json.loads(text[start : end + 1])
                    else:
                        json_data = text

            return {
                "status": response.status,
                "headers": dict(response.headers),
                "data": json_data,
            }
        except Exception as e:
            logger.error(f"解析响应出错: {str(e)}")
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "data": text,
            }

    def _generate_copy_formats(self, request, response_data=None):
        """生成所有复制格式"""
        url = request.url
        method = request.method
        headers = request.headers
        post_data = request.post_data if method == "POST" else None

        formats = {
            "url": url,
            "curl_cmd": self._generate_curl_cmd(method, url, headers, post_data),
            "curl_bash": self._generate_curl_bash(method, url, headers, post_data),
            "powershell": self._generate_powershell(method, url, headers, post_data),
            "fetch": self._generate_fetch(method, url, headers, post_data),
        }

        if response_data:
            formats.update(
                {
                    "response": response_data,
                    "har": self._generate_har(request, response_data),
                }
            )

        return formats

    def _generate_curl_cmd(self, method, url, headers, data=None):
        """生成 cURL (cmd) 格式"""
        headers_str = " ".join([f'-H "{k}: {v}"' for k, v in headers.items()])
        data_str = f' --data "{data}"' if data else ""
        return f'curl -X {method} {headers_str}{data_str} "{url}"'

    def _generate_curl_bash(self, method, url, headers, data=None):
        """生成 cURL (bash) 格式"""
        return (
            f"curl -X {method} \\\n"
            + "\n".join([f'  -H "{k}: {v}" \\' for k, v in headers.items()])
            + (f'\n  --data "{data}" \\' if data else "")
            + f'\n  "{url}"'
        )

    def _generate_powershell(self, method, url, headers, data=None):
        """生成 PowerShell 格式"""
        headers_str = ", ".join([f'"{k}"="{v}"' for k, v in headers.items()])
        return f'Invoke-WebRequest -Uri "{url}" -Method {method} -Headers @{{{headers_str}}}'

    def _generate_fetch(self, method, url, headers, data=None):
        """生成 Fetch (Node.js) 格式"""
        options = {"method": method, "headers": headers}
        if data:
            options["body"] = data
        return f'fetch("{url}", {json.dumps(options, indent=2)})'

    def _generate_har(self, request, response_data):
        """生成 HAR 格式"""
        return {
            "startedDateTime": datetime.now().isoformat(),
            "request": {
                "method": request.method,
                "url": request.url,
                "headers": [
                    {"name": k, "value": v} for k, v in request.headers.items()
                ],
                "postData": {"text": request.post_data} if request.post_data else None,
            },
            "response": {
                "status": response_data.get("status"),
                "headers": response_data.get("headers", {}),
                "content": response_data.get("data"),
            },
        }

    async def save_results(self):
        """保存结果并更新版本信息"""
        try:
            # 按版本分组保存数据
            version_data = {}

            for req_data in self.requests_data:
                if not req_data.get("response_data"):
                    continue

                # 从URL提取版本信息
                url = req_data["request"].url
                version_info = self._extract_version_info(url)
                if not version_info:
                    continue

                version_id = version_info["set_id"]
                if version_id not in version_data:
                    version_data[version_id] = {
                        "base_url": f"https://game.gtimg.cn/images/lol/act/jkzlk/js//{version_id}/{version_info['version']}",
                        "version": version_info["version"],
                        "season": version_info["season"],
                        "set_id": version_id,
                        "name": self.version_config[version_id]["name"],
                        "apis": {},  # 使用字典存储API数据
                    }

                # 保存API数据
                api_name = req_data["api_name"]
                version_data[version_id]["apis"][api_name] = {
                    "url": url,
                    "data": req_data["response_data"],
                }

            # 处理版本更新
            version_changes = await self.version_manager.process_new_data(version_data)

            # 分析数据变化
            data_changes = self._analyze_data_changes(version_data)

            # 记录更新日志
            self.update_logger.log_update(version_changes, data_changes)

            # 保存API数据
            for version_id, version_info in version_data.items():
                save_dir = self.api_dir[version_id]
                save_dir.mkdir(parents=True, exist_ok=True)

                for api_name, api_data in version_info["apis"].items():
                    filename = f"api_{api_name}.json"
                    filepath = save_dir / filename

                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(api_data["data"], f, ensure_ascii=False, indent=2)

                    logger.info(
                        f"已保存 {api_name}数据 ({version_info['name']}): {filepath}"
                    )

        except Exception as e:
            logger.error(f"保存结果出错: {str(e)}")
            raise

    def _extract_version_info(self, url: str) -> Optional[Dict]:
        """从URL提取版本信息"""
        try:
            # 示例URL: https://game.gtimg.cn/images/lol/act/jkzlk/js//4/14.13.6-S14/chess.js
            parts = url.split("/")
            if len(parts) < 7:
                return None

            version_str = parts[-2]  # 14.13.6-S14
            set_id = parts[-3]  # 4 or 13

            if not version_str or not set_id:
                return None

            version_parts = version_str.split("-")
            if len(version_parts) != 2:
                return None

            return {
                "version": version_parts[0],
                "season": version_parts[1],
                "set_id": set_id,
            }

        except Exception:
            return None

    async def _validate_response_data(self, api_name: str, response_data: dict) -> bool:
        """验证响应数据的有效性"""
        try:
            if api_name not in self.data_validators:
                return True

            data = response_data.get("data", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    return False

            return self.data_validators[api_name]({"data": data})
        except Exception as e:
            logger.error(f"数据验证出错 ({api_name}): {str(e)}")
            return False

    async def visit_page(self, page, page_config):
        """访问页面并等待API加载"""
        url = f"{self.target_url}{page_config['path']}"
        logger.info(f"\n访问页面: {url}")

        try:
            # 访问页面
            await page.goto(
                url,
                wait_until="networkidle",
                timeout=self.retry_config["page_load_timeout"],
            )

            # 等待选择器出现
            selector_found = False
            for selector in page_config["wait_for"]:
                try:
                    await page.wait_for_selector(
                        selector, timeout=page_config["timeout"], state="visible"
                    )
                    logger.info(f"找到页面元素: {selector}")
                    selector_found = True
                    break
                except Exception:
                    continue

            # 执行页面动作
            if "actions" in page_config:
                for action in page_config["actions"]:
                    if action["type"] == "wait":
                        await page.wait_for_timeout(action["time"])
                    elif action["type"] == "scroll":
                        await page.evaluate(f"window.scrollTo(0, {action['y']})")
                    elif action["type"] == "wait_for_selector":
                        await page.wait_for_selector(action["selector"])
                    elif action["type"] == "click":
                        await page.click(action["selector"])
                        # 等待新的API请求完成
                        await page.wait_for_load_state("networkidle")

            # 等待网络请求完成
            await page.wait_for_load_state(
                "networkidle", timeout=self.retry_config["network_timeout"]
            )

            # 检查API捕获状态
            expected_apis = page_config["expected_apis"]
            captured_apis = {
                req_data["api_name"]
                for req_data in self.requests_data
                if req_data["api_name"] in expected_apis
            }

            if expected_apis.issubset(captured_apis):
                logger.info(f"已成功捕获所有预期API")
                return True

            missing_apis = expected_apis - captured_apis
            logger.warning(f"未捕获的API: {', '.join(missing_apis)}")
            return False

        except Exception as e:
            logger.error(f"访问页面出错: {str(e)}")
            return False

    async def _process_chess_data(self, data, version=None):
        """处理英雄数据"""
        try:
            if isinstance(data, str):
                data = json.loads(data)

            # 直接返回原始数据，不做处理
            return data

        except Exception as e:
            logger.error(f"处理英雄数据出错: {str(e)}")
            return None

    async def _process_race_data(self, data):
        """处理种族数据"""
        # Implementation needed
        pass

    async def _process_job_data(self, data):
        """处理职业数据"""
        # Implementation needed
        pass

    async def _process_trait_data(self, data):
        """处理羁绊数据"""
        # Implementation needed
        pass

    async def _process_hex_data(self, data):
        """处理海克斯数据"""
        # Implementation needed
        pass

    async def _process_equip_data(self, data):
        """处理装备数据"""
        try:
            if isinstance(data, str):
                # 如果是字符串，尝试解析
                try:
                    # 移除JS变量声明
                    data = re.sub(r"^var\s+\w+\s*=\s*", "", data)
                    # 移除结尾分号
                    data = re.sub(r";?\s*$", "", data)
                    # 处理单引号
                    data = data.replace("'", '"')
                    # 处理未加引号的属性名
                    data = re.sub(r"([{,]\s*)(\w+):", r'\1"\2":', data)

                    data = json.loads(data)
                except:
                    # 尝试提取JSON对象
                    match = re.search(r"\{[\s\S]*\}", data)
                    if match:
                        try:
                            data = json.loads(match.group(0))
                        except:
                            logger.error("提取装备数据JSON失败")
                            return None

            if not isinstance(data, dict):
                return None

            # 验证数据结构
            if "data" not in data:
                data = {"data": data}

            # 验证装备数据
            equips = data["data"]
            if not isinstance(equips, (list, dict)):
                return None

            # 标准化数据格式
            if isinstance(equips, dict):
                equips = list(equips.values())

            # 处理每个装备
            processed_equips = []
            for equip in equips:
                if not isinstance(equip, dict):
                    continue

                # 验证必需字段
                required_fields = ["name", "id", "description"]
                if not all(field in equip for field in required_fields):
                    continue

                processed_equips.append(equip)

            return {"data": processed_equips}

        except Exception as e:
            logger.error(f"处理装备数据出错: {str(e)}")
            return None

    async def _process_lineup_data(self, data, version):
        """处理阵容数据"""
        try:
            if not isinstance(data, dict) or "lineup_list" not in data:
                return None

            processed_data = {
                "version": self.version_config[version]["name"],
                "mode": self.version_config[version]["mode"],
                "lineup_list": [],
            }

            for lineup in data["lineup_list"]:
                # 处理阵容详情
                detail = json.loads(lineup["detail"])
                processed_lineup = {
                    "id": lineup["id"],
                    "name": detail.get("line_name", ""),
                    "quality": lineup["quality"],
                    "author": lineup.get("lineupauthor_data", {}).get("name", ""),
                    "heroes": [],
                    "traits": [],
                }

                # 处理英雄位置
                if "hero_location" in detail:
                    for hero in detail["hero_location"]:
                        processed_lineup["heroes"].append(
                            {
                                "id": hero["hero_id"],
                                "equipment": (
                                    hero["equipment_id"].split(",")
                                    if hero["equipment_id"]
                                    else []
                                ),
                                "position": [
                                    hero["location"],
                                    hero.get("location_2", ""),
                                ],
                            }
                        )

                processed_data["lineup_list"].append(processed_lineup)

            return processed_data

        except Exception as e:
            logger.error(f"处理阵容数据出错: {str(e)}")
            return None

    async def _process_rank_data(self, data):
        """处理段位数据"""
        try:
            if isinstance(data, str):
                data = json.loads(data)

            # 验证数据结构
            if not isinstance(data, dict):
                return None

            # 处理段位数据
            processed_data = {
                "total_players": data.get("total_players", 0),
                "rank_list": [],
            }

            for rank in data.get("rank_list", []):
                processed_rank = {
                    "tier": rank.get("tier", ""),
                    "division": rank.get("division", ""),
                    "players": rank.get("players", 0),
                    "percentage": rank.get("percentage", 0),
                }
                processed_data["rank_list"].append(processed_rank)

            return processed_data

        except Exception as e:
            logger.error(f"处理段位数据出错: {str(e)}")
            return None

    async def _create_browser(self):
        """创建浏览器实例"""
        try:
            browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-web-security",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                ],
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
            )

            # 设置请求超时
            context.set_default_timeout(self.retry_config["network_timeout"])

            # 启用请求拦截
            await context.route("**/*", self._handle_route)

            return browser, context

        except Exception as e:
            logger.error(f"创建浏览器实例失败: {str(e)}")
            raise

    async def _handle_route(self, route):
        """处理请求路由"""
        try:
            request = route.request
            if self.recovery_config["force_https"]:
                url = request.url.replace("http://", "https://")
            else:
                url = request.url

            # 处理特定类型的请求
            if request.resource_type in ["fetch", "xhr", "script"]:
                api_name = self.is_api_request(url)
                if api_name:
                    await route.continue_()
                    return

            # 阻止不必要的请求
            if request.resource_type in ["image", "media", "font"]:
                await route.abort()
                return

            await route.continue_()

        except Exception as e:
            logger.error(f"处理请求路由出错: {str(e)}")
            await route.continue_()

    async def run(self):
        """运行捕获"""
        try:
            self.playwright = await async_playwright().start()
            restart_count = 0

            while restart_count <= self.recovery_config["max_browser_restarts"]:
                browser = None
                try:
                    browser = await self.playwright.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-web-security",
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-accelerated-2d-canvas",
                            "--disable-gpu",
                            "--window-size=1920,1080",
                        ],
                    )
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        ignore_https_errors=True,
                        java_script_enabled=True,
                        bypass_csp=True,
                    )

                    # 设置请求超时
                    context.set_default_timeout(self.retry_config["network_timeout"])
                    page = await context.new_page()

                    # 启用请求拦截
                    await self.capture_network(page)

                    print(
                        f"\n开始捕获API请求... (尝试 {restart_count + 1}/{self.recovery_config['max_browser_restarts'] + 1})"
                    )

                    # 访问所有页面并捕获API
                    success = await self._capture_all_apis(page)
                    if success:
                        # 保存结果
                        await self.save_results()
                        break

                    # 如果失败且还有重试次数，则重启浏览器
                    if restart_count < self.recovery_config["max_browser_restarts"]:
                        logger.warning("重启浏览器并重试...")
                        if browser:
                            await browser.close()
                        await asyncio.sleep(
                            self.recovery_config["restart_delay"] / 1000
                        )
                        restart_count += 1
                        continue

                    raise Exception("达到最大重试次数，仍未成功捕获所有API")

                except Exception as e:
                    logger.error(f"运行出错: {str(e)}")
                    if restart_count < self.recovery_config["max_browser_restarts"]:
                        restart_count += 1
                        continue
                    raise

                finally:
                    if browser:
                        try:
                            await browser.close()
                        except:
                            pass

        except Exception as e:
            logger.error(f"程序运行出错: {str(e)}")
            raise

        finally:
            try:
                await self.playwright.stop()
            except:
                pass

    async def _capture_all_apis(self, page):
        """捕获所有API"""
        try:
            start_time = datetime.now()

            # 访问所有配置的页面
            for page_config in self.pages_to_visit:
                success = await self.visit_page(page, page_config)

                # 检查是否已捕获所有必需的API
                if len(self.captured_required_apis) >= self.required_apis_count:
                    logger.info("已成功捕获所有预期API")
                    # 直接保存结果
                    await self.save_results()
                    return True

                # 检查是否超时
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > self.max_wait_time:
                    logger.warning(f"已达到最大等待时间 {self.max_wait_time} 秒")
                    return False

            return len(self.captured_required_apis) >= self.required_apis_count

        except Exception as e:
            logger.error(f"捕获API出错: {str(e)}")
            return False

    def _analyze_data_changes(self, version_data: Dict) -> Dict:
        """分析数据变化"""
        changes = {}
        for version_id, version_info in version_data.items():
            changes[version_id] = {"new": [], "modified": [], "removed": []}

            # 分析每个API的数据变化
            for api_name, api_data in version_info["apis"].items():
                old_file = self.api_dir[version_id] / f"api_{api_name}.json"

                if not old_file.exists():
                    changes[version_id]["new"].append(api_name)
                else:
                    # 比较数据是否有变化
                    with open(old_file, "r", encoding="utf-8") as f:
                        old_data = json.load(f)
                    if old_data != api_data["data"]:
                        changes[version_id]["modified"].append(api_name)

        return changes


async def main():
    capture = APICapture()
    await capture.run()


if __name__ == "__main__":
    asyncio.run(main())
