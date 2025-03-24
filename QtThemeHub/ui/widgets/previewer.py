"""
主题预览器组件

提供主题预览功能，展示各种UI控件在不同主题下的外观
"""

from typing import Optional

from qtpy import QtCore, QtWidgets, QtGui

from ...core.manager import ThemeManager
from ...core.loader import ThemeLoader, ThemeMeta


class ThemePreviewer(QtWidgets.QDialog):
    """主题预览器对话框"""
    
    def __init__(
        self, 
        theme_manager: ThemeManager, 
        theme_name: str, 
        parent: Optional[QtWidgets.QWidget] = None
    ):
        """初始化主题预览器
        
        Args:
            theme_manager: 主题管理器实例
            theme_name: 要预览的主题名称
            parent: 父组件
        """
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.theme_name = theme_name
        self.theme = theme_manager.get_theme_by_name(theme_name)
        
        if not self.theme:
            raise ValueError(f"主题 {theme_name} 不存在")
        
        # 设置窗口属性
        self.setWindowTitle(f"预览主题: {self.theme.display_name}")
        self.resize(800, 600)
        
        # 初始化UI
        self._init_ui()
        
        # 应用主题
        self._apply_preview_theme()
        
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        layout = QtWidgets.QVBoxLayout(self)
        
        # 主题信息
        info_group = QtWidgets.QGroupBox("主题信息")
        info_layout = QtWidgets.QFormLayout(info_group)
        
        info_layout.addRow("名称:", QtWidgets.QLabel(self.theme.display_name))
        info_layout.addRow("类型:", QtWidgets.QLabel("内置主题" if self.theme.type == "builtin" else "自定义主题"))
        info_layout.addRow("描述:", QtWidgets.QLabel(self.theme.description))
        
        layout.addWidget(info_group)
        
        # 预览区域
        preview_tabs = QtWidgets.QTabWidget()
        
        # 基础控件选项卡
        basic_tab = self._create_basic_widgets_tab()
        preview_tabs.addTab(basic_tab, "基础控件")
        
        # 输入控件选项卡
        input_tab = self._create_input_widgets_tab()
        preview_tabs.addTab(input_tab, "输入控件")
        
        # 容器控件选项卡
        container_tab = self._create_container_widgets_tab()
        preview_tabs.addTab(container_tab, "容器控件")
        
        # 高级控件选项卡
        advanced_tab = self._create_advanced_widgets_tab()
        preview_tabs.addTab(advanced_tab, "高级控件")
        
        layout.addWidget(preview_tabs)
        
        # 按钮区域
        buttons_layout = QtWidgets.QHBoxLayout()
        
        apply_btn = QtWidgets.QPushButton("应用此主题")
        apply_btn.clicked.connect(self._apply_theme)
        
        close_btn = QtWidgets.QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
    def _create_basic_widgets_tab(self) -> QtWidgets.QWidget:
        """创建基础控件选项卡
        
        Returns:
            包含基础控件的组件
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 标签
        labels_group = QtWidgets.QGroupBox("标签")
        labels_layout = QtWidgets.QVBoxLayout(labels_group)
        
        labels_layout.addWidget(QtWidgets.QLabel("普通标签"))
        
        disabled_label = QtWidgets.QLabel("禁用标签")
        disabled_label.setEnabled(False)
        labels_layout.addWidget(disabled_label)
        
        link_label = QtWidgets.QLabel("<a href='#'>链接标签</a>")
        link_label.setOpenExternalLinks(True)
        labels_layout.addWidget(link_label)
        
        layout.addWidget(labels_group)
        
        # 按钮
        buttons_group = QtWidgets.QGroupBox("按钮")
        buttons_layout = QtWidgets.QVBoxLayout(buttons_group)
        
        buttons_layout.addWidget(QtWidgets.QPushButton("普通按钮"))
        
        default_btn = QtWidgets.QPushButton("默认按钮")
        default_btn.setDefault(True)
        buttons_layout.addWidget(default_btn)
        
        disabled_btn = QtWidgets.QPushButton("禁用按钮")
        disabled_btn.setEnabled(False)
        buttons_layout.addWidget(disabled_btn)
        
        flat_btn = QtWidgets.QPushButton("扁平按钮")
        flat_btn.setFlat(True)
        buttons_layout.addWidget(flat_btn)
        
        layout.addWidget(buttons_group)
        
        # 工具按钮
        tool_buttons_group = QtWidgets.QGroupBox("工具按钮")
        tool_buttons_layout = QtWidgets.QVBoxLayout(tool_buttons_group)
        
        tool_buttons_layout.addWidget(QtWidgets.QToolButton())
        
        menu_btn = QtWidgets.QToolButton()
        menu_btn.setText("菜单按钮")
        menu_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        menu = QtWidgets.QMenu()
        menu.addAction("选项1")
        menu.addAction("选项2")
        menu.addAction("选项3")
        menu_btn.setMenu(menu)
        tool_buttons_layout.addWidget(menu_btn)
        
        layout.addWidget(tool_buttons_group)
        
        return tab
    
    def _create_input_widgets_tab(self) -> QtWidgets.QWidget:
        """创建输入控件选项卡
        
        Returns:
            包含输入控件的组件
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 文本输入
        text_group = QtWidgets.QGroupBox("文本输入")
        text_layout = QtWidgets.QVBoxLayout(text_group)
        
        text_layout.addWidget(QtWidgets.QLineEdit("单行文本输入"))
        
        password_edit = QtWidgets.QLineEdit("密码输入")
        password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        text_layout.addWidget(password_edit)
        
        disabled_edit = QtWidgets.QLineEdit("禁用输入")
        disabled_edit.setEnabled(False)
        text_layout.addWidget(disabled_edit)
        
        text_edit = QtWidgets.QTextEdit()
        text_edit.setPlainText("多行文本输入\n第二行\n第三行")
        text_layout.addWidget(text_edit)
        
        layout.addWidget(text_group)
        
        # 选择控件
        selection_group = QtWidgets.QGroupBox("选择控件")
        selection_layout = QtWidgets.QVBoxLayout(selection_group)
        
        combo = QtWidgets.QComboBox()
        combo.addItems(["选项1", "选项2", "选项3"])
        selection_layout.addWidget(combo)
        
        editable_combo = QtWidgets.QComboBox()
        editable_combo.setEditable(True)
        editable_combo.addItems(["可编辑选项1", "可编辑选项2", "可编辑选项3"])
        selection_layout.addWidget(editable_combo)
        
        disabled_combo = QtWidgets.QComboBox()
        disabled_combo.addItems(["禁用选项1", "禁用选项2", "禁用选项3"])
        disabled_combo.setEnabled(False)
        selection_layout.addWidget(disabled_combo)
        
        layout.addWidget(selection_group)
        
        # 数值输入
        numeric_group = QtWidgets.QGroupBox("数值输入")
        numeric_layout = QtWidgets.QVBoxLayout(numeric_group)
        
        numeric_layout.addWidget(QtWidgets.QSpinBox())
        
        double_spin = QtWidgets.QDoubleSpinBox()
        double_spin.setDecimals(2)
        numeric_layout.addWidget(double_spin)
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        numeric_layout.addWidget(slider)
        
        layout.addWidget(numeric_group)
        
        return tab
    
    def _create_container_widgets_tab(self) -> QtWidgets.QWidget:
        """创建容器控件选项卡
        
        Returns:
            包含容器控件的组件
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 分组框
        group_box = QtWidgets.QGroupBox("分组框")
        group_layout = QtWidgets.QVBoxLayout(group_box)
        group_layout.addWidget(QtWidgets.QLabel("分组框内容"))
        group_layout.addWidget(QtWidgets.QPushButton("分组框按钮"))
        layout.addWidget(group_box)
        
        # 选项卡
        tab_widget = QtWidgets.QTabWidget()
        
        tab1 = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(tab1)
        tab1_layout.addWidget(QtWidgets.QLabel("选项卡1内容"))
        tab_widget.addTab(tab1, "选项卡1")
        
        tab2 = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(tab2)
        tab2_layout.addWidget(QtWidgets.QLabel("选项卡2内容"))
        tab_widget.addTab(tab2, "选项卡2")
        
        layout.addWidget(tab_widget)
        
        # 堆叠窗口
        stack = QtWidgets.QStackedWidget()
        
        page1 = QtWidgets.QWidget()
        page1_layout = QtWidgets.QVBoxLayout(page1)
        page1_layout.addWidget(QtWidgets.QLabel("页面1"))
        stack.addWidget(page1)
        
        page2 = QtWidgets.QWidget()
        page2_layout = QtWidgets.QVBoxLayout(page2)
        page2_layout.addWidget(QtWidgets.QLabel("页面2"))
        stack.addWidget(page2)
        
        # 切换按钮
        switch_layout = QtWidgets.QHBoxLayout()
        
        prev_btn = QtWidgets.QPushButton("上一页")
        prev_btn.clicked.connect(lambda: stack.setCurrentIndex(max(0, stack.currentIndex() - 1)))
        
        next_btn = QtWidgets.QPushButton("下一页")
        next_btn.clicked.connect(lambda: stack.setCurrentIndex(min(stack.count() - 1, stack.currentIndex() + 1)))
        
        switch_layout.addWidget(prev_btn)
        switch_layout.addWidget(next_btn)
        
        stack_group = QtWidgets.QGroupBox("堆叠窗口")
        stack_layout = QtWidgets.QVBoxLayout(stack_group)
        stack_layout.addWidget(stack)
        stack_layout.addLayout(switch_layout)
        
        layout.addWidget(stack_group)
        
        return tab
    
    def _create_advanced_widgets_tab(self) -> QtWidgets.QWidget:
        """创建高级控件选项卡
        
        Returns:
            包含高级控件的组件
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 列表和树
        views_group = QtWidgets.QGroupBox("列表和树")
        views_layout = QtWidgets.QHBoxLayout(views_group)
        
        # 列表
        list_widget = QtWidgets.QListWidget()
        list_widget.addItems([f"列表项 {i+1}" for i in range(10)])
        views_layout.addWidget(list_widget)
        
        # 树
        tree_widget = QtWidgets.QTreeWidget()
        tree_widget.setHeaderLabels(["树项"])
        
        for i in range(3):
            parent = QtWidgets.QTreeWidgetItem([f"父项 {i+1}"])
            tree_widget.addTopLevelItem(parent)
            
            for j in range(3):
                child = QtWidgets.QTreeWidgetItem([f"子项 {i+1}-{j+1}"])
                parent.addChild(child)
        
        tree_widget.expandAll()
        views_layout.addWidget(tree_widget)
        
        layout.addWidget(views_group)
        
        # 表格
        table_group = QtWidgets.QGroupBox("表格")
        table_layout = QtWidgets.QVBoxLayout(table_group)
        
        table = QtWidgets.QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["列1", "列2", "列3"])
        
        for i in range(5):
            for j in range(3):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(f"单元格 {i+1}-{j+1}"))
        
        table_layout.addWidget(table)
        layout.addWidget(table_group)
        
        # 进度条
        progress_group = QtWidgets.QGroupBox("进度条")
        progress_layout = QtWidgets.QVBoxLayout(progress_group)
        
        progress = QtWidgets.QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(75)
        progress_layout.addWidget(progress)
        
        indeterminate = QtWidgets.QProgressBar()
        indeterminate.setRange(0, 0)  # 不确定进度
        progress_layout.addWidget(indeterminate)
        
        layout.addWidget(progress_group)
        
        return tab
    
    def _apply_preview_theme(self):
        """应用预览主题"""
        # 加载主题样式表
        stylesheet = ThemeLoader.load_stylesheet(self.theme)
        
        # 应用样式表
        self.setStyleSheet(stylesheet)
    
    def _apply_theme(self):
        """应用当前预览的主题到整个应用"""
        try:
            self.theme_manager.set_theme(self.theme_name)
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "应用主题失败",
                f"应用主题 {self.theme_name} 时出错: {e}"
            ) 
