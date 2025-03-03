"""
功能: 数据版本管理器 - 管理API数据的版本和更新
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging
import shutil

logger = logging.getLogger(__name__)


class DataVersionManager:
    def __init__(self):
        self.base_dir = Path("data/crawler/api")
        self.version_file = self.base_dir / "version_info.json"
        self.config_template = Path("config_template.py")
        self.backup_dir = Path("data/backups/config")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def load_version_info(self) -> Dict:
        """加载版本信息"""
        if self.version_file.exists():
            with open(self.version_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"last_update": "", "versions": {}}

    def save_version_info(self, info: Dict):
        """保存版本信息"""
        with open(self.version_file, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

    def detect_version_changes(self, new_data: Dict) -> Dict:
        """检测版本变化"""
        current_info = self.load_version_info()
        changes = {"new_versions": [], "updated_versions": [], "removed_versions": []}

        # 检查新增和更新的版本
        for version_id, version_data in new_data.items():
            if version_id not in current_info["versions"]:
                changes["new_versions"].append(version_id)
            elif version_data != current_info["versions"][version_id]:
                changes["updated_versions"].append(version_id)

        # 检查移除的版本
        for version_id in current_info["versions"]:
            if version_id not in new_data:
                changes["removed_versions"].append(version_id)

        return changes

    def update_config(self, version_changes: Dict):
        """更新配置文件"""
        if not any(version_changes.values()):
            return

        try:
            # 读取配置模板
            with open(self.config_template, "r", encoding="utf-8") as f:
                config_template = f.read()

            # 生成新的版本配置
            versions_config = {}
            version_info = self.load_version_info()

            for version_id, version_data in version_info["versions"].items():
                if version_id not in version_changes["removed_versions"]:
                    versions_config[version_id] = {
                        "base_url": version_data["base_url"],
                        "version": version_data["version"],
                        "season": version_data["season"],
                        "set_id": version_data["set_id"],
                        "name": version_data["name"],
                    }

            # 更新配置文件
            config_content = config_template.replace(
                "VERSIONS = {}",
                f"VERSIONS = {json.dumps(versions_config, indent=4, ensure_ascii=False)}",
            )

            # 备份旧配置
            if os.path.exists("config.py"):
                backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"config.py.bak.{backup_time}"
                backup_path = self.backup_dir / backup_name

                # 如果备份文件已存在，添加序号
                counter = 1
                while backup_path.exists():
                    backup_name = f"config.py.bak.{backup_time}_{counter}"
                    backup_path = self.backup_dir / backup_name
                    counter += 1

                # 复制而不是移动，保留原始配置
                shutil.copy2("config.py", backup_path)

            # 写入新配置
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)

            logger.info(f"配置文件已更新，旧配置已备份为: {backup_path}")

        except Exception as e:
            logger.error(f"更新配置文件失败: {str(e)}")
            raise

    async def process_new_data(self, version_data: Dict):
        """处理新数据"""
        try:
            # 检测版本变化
            version_changes = self.detect_version_changes(version_data)

            if any(version_changes.values()):
                # 更新版本信息
                version_info = self.load_version_info()
                version_info["last_update"] = datetime.now().isoformat()

                # 只保存版本基本信息
                version_info["versions"] = {
                    version_id: {
                        k: v
                        for k, v in info.items()
                        if k not in ["apis", "data"]  # 排除API数据
                    }
                    for version_id, info in version_data.items()
                }

                self.save_version_info(version_info)

                # 更新配置文件
                self.update_config(version_changes)

                # 记录变化
                logger.info("版本变化:")
                if version_changes["new_versions"]:
                    logger.info(f"新增版本: {version_changes['new_versions']}")
                if version_changes["updated_versions"]:
                    logger.info(f"更新版本: {version_changes['updated_versions']}")
                if version_changes["removed_versions"]:
                    logger.info(f"移除版本: {version_changes['removed_versions']}")

            return version_changes

        except Exception as e:
            logger.error(f"处理新数据时出错: {str(e)}")
            raise
