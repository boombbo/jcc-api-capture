"""
主题管理器模块

负责管理和应用主题，提供统一的主题切换接口
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable

from qtpy import QtCore, QtWidgets, QtGui

from .loader import ThemeLoader, ThemeMeta
from ..utils.compat import is_dark_mode
from ..utils.styler import optimize_stylesheet


class ThemeManager(QtCore.QObject):
    """主题管理器类"""
    
    # 主题变更信号，传递ThemeMeta对象
    themeChanged = QtCore.Signal(object)
    
    def __init__(self, app: Optional[QtWidgets.QApplication] = None):
        """初始化主题管理器
        
        Args:
            app: Qt应用程序实例，如果为None则使用QApplication.instance()
        """
        super().__init__()
        
        # 获取应用程序实例
        self.app = app or QtWidgets.QApplication.instance()
        if not self.app:
            raise RuntimeError("必须先创建QApplication实例")
            
        # 初始化属性
        self.current_theme = None
        self._themes = {}
        self._custom_theme_dirs = []
        
        # 添加默认自定义主题目录
        default_custom_dir = Path(__file__).parent.parent / 'themes' / 'custom'
        self.add_custom_theme_dir(default_custom_dir)
        
        # 初始化主题
        self._init_themes()
        
    def _init_themes(self):
        """初始化主题列表"""
        # 检测内置主题
        self._themes.update(ThemeLoader.detect_builtin_themes())
        
        # 加载自定义主题
        for theme_dir in self._custom_theme_dirs:
            custom_themes = ThemeLoader.scan_custom_themes(theme_dir)
            self._themes.update(custom_themes)
            
        # 添加系统默认主题
        self._themes['system_default'] = ThemeMeta(
            name='system_default',
            type='builtin',
            display_name='系统默认',
            description='使用系统默认样式',
            loader=lambda: ''
        )
        
    def add_custom_theme_dir(self, theme_dir: Union[str, Path]):
        """添加自定义主题目录
        
        Args:
            theme_dir: 主题目录路径
        """
        if isinstance(theme_dir, str):
            theme_dir = Path(theme_dir)
            
        if theme_dir not in self._custom_theme_dirs:
            self._custom_theme_dirs.append(theme_dir)
            
            # 扫描新添加的目录
            custom_themes = ThemeLoader.scan_custom_themes(theme_dir)
            self._themes.update(custom_themes)
            
    def set_theme(self, theme_name: str):
        """设置当前主题
        
        Args:
            theme_name: 主题名称
            
        Raises:
            ValueError: 如果主题不存在
        """
        # 检查主题是否存在
        theme = self._themes.get(theme_name)
        if not theme:
            raise ValueError(f"主题 {theme_name} 不存在")
        
        try:
            # 特殊处理qt-material主题
            if theme.name.startswith('material_'):
                self._apply_material_theme(theme)
            else:
                # 加载样式表
                stylesheet = ThemeLoader.load_stylesheet(theme)
                
                # 优化样式表
                stylesheet = optimize_stylesheet(stylesheet)
                
                # 应用样式表
                self.app.setStyleSheet(stylesheet)
            
            # 更新当前主题
            self.current_theme = theme
            
            # 触发主题变更信号
            self.themeChanged.emit(theme)
            
        except Exception as e:
            print(f"应用主题 {theme_name} 时出错: {e}")
            
    def _apply_material_theme(self, theme: ThemeMeta):
        """应用Material主题
        
        Args:
            theme: 主题元数据
        """
        try:
            # 导入qt_material
            import qt_material
            
            # 提取主题名称
            theme_name = theme.name.replace('material_', '')
            
            # 应用主题
            qt_material.apply_stylesheet(
                self.app, 
                theme=f"{theme_name}.xml",
                invert_secondary=theme.config.get('invert_secondary', True),
                extra=theme.config.get('extra', {})
            )
            
        except ImportError:
            print("未安装qt_material库，无法应用Material主题")
        except Exception as e:
            print(f"应用Material主题时出错: {e}")
            
    def get_available_themes(self) -> List[ThemeMeta]:
        """获取可用主题列表
        
        Returns:
            主题元数据列表
        """
        return list(self._themes.values())
    
    def get_theme_by_name(self, theme_name: str) -> Optional[ThemeMeta]:
        """根据名称获取主题
        
        Args:
            theme_name: 主题名称
            
        Returns:
            主题元数据，如果不存在则返回None
        """
        return self._themes.get(theme_name)
    
    def load_custom_theme(self, name: str, qss_path: Union[str, Path]) -> ThemeMeta:
        """加载自定义主题
        
        Args:
            name: 主题名称
            qss_path: QSS文件路径
            
        Returns:
            主题元数据
            
        Raises:
            FileNotFoundError: 如果QSS文件不存在
        """
        if isinstance(qss_path, str):
            qss_path = Path(qss_path)
            
        if not qss_path.exists():
            raise FileNotFoundError(f"QSS文件 {qss_path} 不存在")
            
        # 创建主题元数据
        theme_name = f"custom_{name}"
        theme = ThemeMeta(
            name=theme_name,
            type='custom',
            display_name=name.replace('_', ' ').title(),
            description=f'自定义主题: {name}',
            path=qss_path
        )
        
        # 添加到主题列表
        self._themes[theme_name] = theme
        
        return theme
    
    def auto_detect_theme(self) -> str:
        """自动检测系统主题
        
        Returns:
            适合当前系统主题的主题名称
        """
        # 检测系统是否为暗色模式
        if is_dark_mode():
            # 优先使用QDarkTheme
            if 'qdarktheme_dark' in self._themes:
                return 'qdarktheme_dark'
            # 其次使用QDarkStyle
            elif 'qdarkstyle_dark' in self._themes:
                return 'qdarkstyle_dark'
            # 再次使用Material Dark Blue
            elif 'material_dark_blue' in self._themes:
                return 'material_dark_blue'
        else:
            # 优先使用QDarkTheme
            if 'qdarktheme_light' in self._themes:
                return 'qdarktheme_light'
            # 其次使用QDarkStyle
            elif 'qdarkstyle_light' in self._themes:
                return 'qdarkstyle_light'
            # 再次使用Material Light Blue
            elif 'material_light_blue' in self._themes:
                return 'material_light_blue'
                
        # 如果没有合适的主题，使用系统默认
        return 'system_default'
        
    def apply_auto_theme(self):
        """应用自动检测的主题"""
        theme_name = self.auto_detect_theme()
        self.set_theme(theme_name) 
