"""
主题选择器组件

提供主题选择和预览功能
"""

from typing import List, Optional, Dict, Callable

from qtpy import QtCore, QtWidgets, QtGui

from ...core.manager import ThemeManager
from ...core.loader import ThemeMeta


class ThemeSelector(QtWidgets.QWidget):
    """主题选择器组件"""
    
    # 主题选择信号，传递主题名称
    themeSelected = QtCore.Signal(str)
    
    def __init__(self, theme_manager: ThemeManager, parent: Optional[QtWidgets.QWidget] = None):
        """初始化主题选择器
        
        Args:
            theme_manager: 主题管理器实例
            parent: 父组件
        """
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.current_theme = theme_manager.current_theme
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 加载主题列表
        self._load_themes()
        
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 主题类型选择
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItem("所有主题", "all")
        self.type_combo.addItem("内置主题", "builtin")
        self.type_combo.addItem("自定义主题", "custom")
        layout.addWidget(self.type_combo)
        
        # 主题列表
        self.theme_list = QtWidgets.QListWidget()
        self.theme_list.setIconSize(QtCore.QSize(32, 32))
        layout.addWidget(self.theme_list)
        
        # 主题详情
        details_group = QtWidgets.QGroupBox("主题详情")
        details_layout = QtWidgets.QFormLayout(details_group)
        
        self.name_label = QtWidgets.QLabel()
        self.type_label = QtWidgets.QLabel()
        self.desc_label = QtWidgets.QLabel()
        self.desc_label.setWordWrap(True)
        
        details_layout.addRow("名称:", self.name_label)
        details_layout.addRow("类型:", self.type_label)
        details_layout.addRow("描述:", self.desc_label)
        
        layout.addWidget(details_group)
        
        # 操作按钮
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.apply_btn = QtWidgets.QPushButton("应用主题")
        self.preview_btn = QtWidgets.QPushButton("预览主题")
        
        buttons_layout.addWidget(self.preview_btn)
        buttons_layout.addWidget(self.apply_btn)
        
        layout.addLayout(buttons_layout)
        
    def _connect_signals(self):
        """连接信号"""
        # 主题类型选择变化
        self.type_combo.currentIndexChanged.connect(self._filter_themes)
        
        # 主题列表选择变化
        self.theme_list.currentItemChanged.connect(self._on_theme_selected)
        
        # 应用按钮点击
        self.apply_btn.clicked.connect(self._apply_theme)
        
        # 预览按钮点击
        self.preview_btn.clicked.connect(self._preview_theme)
        
        # 主题管理器主题变更
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        
    def _load_themes(self):
        """加载主题列表"""
        # 清空列表
        self.theme_list.clear()
        
        # 获取所有主题
        themes = self.theme_manager.get_available_themes()
        
        # 添加到列表
        for theme in themes:
            item = QtWidgets.QListWidgetItem(theme.display_name)
            item.setData(QtCore.Qt.UserRole, theme.name)
            
            # 设置图标
            if theme.type == 'builtin':
                item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
            else:
                item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileLinkIcon))
            
            self.theme_list.addItem(item)
        
        # 选择当前主题
        if self.current_theme:
            for i in range(self.theme_list.count()):
                item = self.theme_list.item(i)
                if item.data(QtCore.Qt.UserRole) == self.current_theme.name:
                    self.theme_list.setCurrentItem(item)
                    break
        
    def _filter_themes(self):
        """根据类型筛选主题"""
        theme_type = self.type_combo.currentData()
        
        # 显示所有主题
        for i in range(self.theme_list.count()):
            item = self.theme_list.item(i)
            theme_name = item.data(QtCore.Qt.UserRole)
            theme = self.theme_manager.get_theme_by_name(theme_name)
            
            if theme_type == "all" or theme.type == theme_type:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def _on_theme_selected(self, current: QtWidgets.QListWidgetItem, previous: QtWidgets.QListWidgetItem):
        """主题选择变化处理
        
        Args:
            current: 当前选中项
            previous: 之前选中项
        """
        if not current:
            return
        
        # 获取主题名称
        theme_name = current.data(QtCore.Qt.UserRole)
        
        # 获取主题元数据
        theme = self.theme_manager.get_theme_by_name(theme_name)
        if not theme:
            return
        
        # 更新详情
        self.name_label.setText(theme.display_name)
        self.type_label.setText("内置主题" if theme.type == "builtin" else "自定义主题")
        self.desc_label.setText(theme.description)
        
        # 发送主题选择信号
        self.themeSelected.emit(theme_name)
    
    def _apply_theme(self):
        """应用当前选中的主题"""
        current_item = self.theme_list.currentItem()
        if not current_item:
            return
        
        # 获取主题名称
        theme_name = current_item.data(QtCore.Qt.UserRole)
        
        # 应用主题
        try:
            self.theme_manager.set_theme(theme_name)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "应用主题失败",
                f"应用主题 {theme_name} 时出错: {e}"
            )
    
    def _preview_theme(self):
        """预览当前选中的主题"""
        current_item = self.theme_list.currentItem()
        if not current_item:
            return
        
        # 获取主题名称
        theme_name = current_item.data(QtCore.Qt.UserRole)
        
        # 获取主题元数据
        theme = self.theme_manager.get_theme_by_name(theme_name)
        if not theme:
            return
        
        # 创建预览窗口
        from .previewer import ThemePreviewer
        previewer = ThemePreviewer(self.theme_manager, theme_name, self)
        previewer.show()
    
    def _on_theme_changed(self, theme: ThemeMeta):
        """主题变更处理
        
        Args:
            theme: 新主题元数据
        """
        self.current_theme = theme
        
        # 更新选中项
        for i in range(self.theme_list.count()):
            item = self.theme_list.item(i)
            if item.data(QtCore.Qt.UserRole) == theme.name:
                self.theme_list.setCurrentItem(item)
                break 
