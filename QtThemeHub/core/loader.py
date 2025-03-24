"""
主题加载器模块

负责检测和加载不同来源的主题，包括内置主题库和自定义主题文件
"""

import os
import importlib
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Any, Union

from qtpy import QtCore


@dataclass
class ThemeMeta:
    """主题元数据类"""
    name: str  # 主题名称
    type: str  # 主题类型：builtin/custom
    display_name: str = ""  # 显示名称
    description: str = ""  # 主题描述
    path: Optional[Path] = None  # 主题文件路径
    loader: Optional[Callable] = None  # 主题加载函数
    config: Dict[str, Any] = field(default_factory=dict)  # 主题配置
    
    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()


class ThemeLoader:
    """主题加载器类"""
    
    @classmethod
    def detect_builtin_themes(cls) -> Dict[str, ThemeMeta]:
        """检测已安装的内置主题库"""
        themes = {}
        
        # 检测QDarkStyle主题
        if importlib.util.find_spec('qdarkstyle'):
            themes.update({
                'qdarkstyle_dark': ThemeMeta(
                    name='qdarkstyle_dark',
                    type='builtin',
                    display_name='QDarkStyle Dark',
                    description='QDarkStyle暗色主题',
                    loader=lambda: importlib.import_module('qdarkstyle').load_stylesheet()
                ),
                'qdarkstyle_light': ThemeMeta(
                    name='qdarkstyle_light',
                    type='builtin',
                    display_name='QDarkStyle Light',
                    description='QDarkStyle亮色主题',
                    loader=lambda: importlib.import_module('qdarkstyle').load_stylesheet(light=True)
                )
            })
            
        # 检测qt-material主题
        if importlib.util.find_spec('qt_material'):
            material = importlib.import_module('qt_material')
            try:
                for theme in material.list_themes():
                    theme_name = theme.replace('.xml', '')
                    themes[f'material_{theme_name}'] = ThemeMeta(
                        name=f'material_{theme_name}',
                        type='builtin',
                        display_name=f'Material {theme_name.replace("_", " ").title()}',
                        description=f'Material Design {theme_name}主题',
                        loader=lambda t=theme: material.get_theme(t)
                    )
            except (AttributeError, ImportError):
                # 如果qt_material没有list_themes方法，使用预定义的主题列表
                material_themes = [
                    'dark_amber', 'dark_blue', 'dark_cyan', 'dark_lightgreen',
                    'dark_pink', 'dark_purple', 'dark_red', 'dark_teal',
                    'dark_yellow', 'light_amber', 'light_blue', 'light_cyan',
                    'light_lightgreen', 'light_pink', 'light_purple', 'light_red',
                    'light_teal', 'light_yellow'
                ]
                for theme in material_themes:
                    themes[f'material_{theme}'] = ThemeMeta(
                        name=f'material_{theme}',
                        type='builtin',
                        display_name=f'Material {theme.replace("_", " ").title()}',
                        description=f'Material Design {theme}主题',
                        loader=lambda t=theme: cls._load_material_theme(t)
                    )
        
        # 检测PyQtDarkTheme主题
        if importlib.util.find_spec('qdarktheme'):
            themes.update({
                'qdarktheme_dark': ThemeMeta(
                    name='qdarktheme_dark',
                    type='builtin',
                    display_name='QDarkTheme Dark',
                    description='PyQtDarkTheme暗色主题',
                    loader=lambda: importlib.import_module('qdarktheme').load_stylesheet('dark')
                ),
                'qdarktheme_light': ThemeMeta(
                    name='qdarktheme_light',
                    type='builtin',
                    display_name='QDarkTheme Light',
                    description='PyQtDarkTheme亮色主题',
                    loader=lambda: importlib.import_module('qdarktheme').load_stylesheet('light')
                )
            })
                
        return themes

    @classmethod
    def scan_custom_themes(cls, theme_dir: Union[str, Path]) -> Dict[str, ThemeMeta]:
        """扫描自定义主题目录"""
        themes = {}
        
        if isinstance(theme_dir, str):
            theme_dir = Path(theme_dir)
            
        if not theme_dir.exists():
            return themes
            
        # 扫描QSS文件
        for qss_file in theme_dir.glob('**/*.qss'):
            theme_name = f"custom_{qss_file.stem}"
            themes[theme_name] = ThemeMeta(
                name=theme_name,
                type='custom',
                display_name=qss_file.stem.replace('_', ' ').title(),
                description=f'自定义主题: {qss_file.stem}',
                path=qss_file
            )
            
        return themes

    @staticmethod
    def load_stylesheet(theme: ThemeMeta) -> str:
        """加载主题样式表"""
        if theme.loader:
            try:
                return theme.loader()
            except Exception as e:
                print(f"加载主题 {theme.name} 时出错: {e}")
                return ""
        elif theme.path:
            try:
                return theme.path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"读取主题文件 {theme.path} 时出错: {e}")
                return ""
        return ""
        
    @staticmethod
    def _load_material_theme(theme_name: str) -> str:
        """加载Material主题"""
        try:
            material = importlib.import_module('qt_material')
            return material.get_theme(f"{theme_name}.xml")
        except (AttributeError, ImportError):
            # 如果没有get_theme方法，尝试使用apply_stylesheet
            try:
                return ""  # 实际使用时需要通过apply_stylesheet应用
            except Exception as e:
                print(f"加载Material主题 {theme_name} 时出错: {e}")
                return "" 
