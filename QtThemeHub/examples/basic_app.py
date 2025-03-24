"""
基本示例应用

展示如何使用QtThemeHub进行主题管理
"""

import sys
from pathlib import Path

from qtpy import QtWidgets, QtCore, QtGui

# 导入QtThemeHub
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from QtThemeHub import ThemeManager
from QtThemeHub.ui import ThemeSelector


class MainWindow(QtWidgets.QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("QtThemeHub示例应用")
        self.resize(800, 600)
        
        # 创建主题管理器
        self.theme_manager = ThemeManager()
        
        # 初始化UI
        self._init_ui()
        
        # 应用自动检测的主题
        self.theme_manager.apply_auto_theme()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # 创建左侧面板
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)
        
        # 创建右侧面板
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel)
        
        # 设置分割比例
        main_layout.setStretch(0, 1)  # 左侧面板
        main_layout.setStretch(1, 2)  # 右侧面板
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建状态栏
        self._create_status_bar()
        
    def _create_left_panel(self):
        """创建左侧面板
        
        Returns:
            左侧面板组件
        """
        # 创建主题选择器
        theme_selector = ThemeSelector(self.theme_manager)
        
        # 创建分组框
        group_box = QtWidgets.QGroupBox("主题选择")
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.addWidget(theme_selector)
        
        return group_box
    
    def _create_right_panel(self):
        """创建右侧面板
        
        Returns:
            右侧面板组件
        """
        # 创建选项卡部件
        tab_widget = QtWidgets.QTabWidget()
        
        # 创建控件展示选项卡
        widgets_tab = self._create_widgets_tab()
        tab_widget.addTab(widgets_tab, "控件展示")
        
        # 创建表单示例选项卡
        form_tab = self._create_form_tab()
        tab_widget.addTab(form_tab, "表单示例")
        
        # 创建数据展示选项卡
        data_tab = self._create_data_tab()
        tab_widget.addTab(data_tab, "数据展示")
        
        return tab_widget
    
    def _create_widgets_tab(self):
        """创建控件展示选项卡
        
        Returns:
            控件展示选项卡
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 创建滚动区域
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # 创建滚动内容
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        
        # 添加各种控件
        
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
        
        scroll_layout.addWidget(buttons_group)
        
        # 输入控件
        input_group = QtWidgets.QGroupBox("输入控件")
        input_layout = QtWidgets.QFormLayout(input_group)
        
        input_layout.addRow("单行文本:", QtWidgets.QLineEdit())
        
        password_edit = QtWidgets.QLineEdit()
        password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        input_layout.addRow("密码:", password_edit)
        
        combo = QtWidgets.QComboBox()
        combo.addItems(["选项1", "选项2", "选项3"])
        input_layout.addRow("下拉框:", combo)
        
        spin = QtWidgets.QSpinBox()
        spin.setRange(0, 100)
        input_layout.addRow("数值:", spin)
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        input_layout.addRow("滑块:", slider)
        
        scroll_layout.addWidget(input_group)
        
        # 容器控件
        container_group = QtWidgets.QGroupBox("容器控件")
        container_layout = QtWidgets.QVBoxLayout(container_group)
        
        tab_widget = QtWidgets.QTabWidget()
        tab1 = QtWidgets.QWidget()
        tab1_layout = QtWidgets.QVBoxLayout(tab1)
        tab1_layout.addWidget(QtWidgets.QLabel("选项卡1内容"))
        tab_widget.addTab(tab1, "选项卡1")
        
        tab2 = QtWidgets.QWidget()
        tab2_layout = QtWidgets.QVBoxLayout(tab2)
        tab2_layout.addWidget(QtWidgets.QLabel("选项卡2内容"))
        tab_widget.addTab(tab2, "选项卡2")
        
        container_layout.addWidget(tab_widget)
        
        scroll_layout.addWidget(container_group)
        
        # 设置滚动内容
        scroll_area.setWidget(scroll_content)
        
        return tab
    
    def _create_form_tab(self):
        """创建表单示例选项卡
        
        Returns:
            表单示例选项卡
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 创建表单
        form_group = QtWidgets.QGroupBox("用户信息表单")
        form_layout = QtWidgets.QFormLayout(form_group)
        
        form_layout.addRow("用户名:", QtWidgets.QLineEdit())
        
        password_edit = QtWidgets.QLineEdit()
        password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow("密码:", password_edit)
        
        gender_layout = QtWidgets.QHBoxLayout()
        male_radio = QtWidgets.QRadioButton("男")
        female_radio = QtWidgets.QRadioButton("女")
        male_radio.setChecked(True)
        gender_layout.addWidget(male_radio)
        gender_layout.addWidget(female_radio)
        form_layout.addRow("性别:", gender_layout)
        
        age_spin = QtWidgets.QSpinBox()
        age_spin.setRange(1, 120)
        age_spin.setValue(18)
        form_layout.addRow("年龄:", age_spin)
        
        country_combo = QtWidgets.QComboBox()
        country_combo.addItems(["中国", "美国", "英国", "法国", "德国", "日本"])
        form_layout.addRow("国家:", country_combo)
        
        hobby_layout = QtWidgets.QVBoxLayout()
        hobby_layout.addWidget(QtWidgets.QCheckBox("阅读"))
        hobby_layout.addWidget(QtWidgets.QCheckBox("音乐"))
        hobby_layout.addWidget(QtWidgets.QCheckBox("运动"))
        hobby_layout.addWidget(QtWidgets.QCheckBox("旅游"))
        form_layout.addRow("爱好:", hobby_layout)
        
        intro_edit = QtWidgets.QTextEdit()
        form_layout.addRow("简介:", intro_edit)
        
        layout.addWidget(form_group)
        
        # 创建按钮
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(QtWidgets.QPushButton("提交"))
        buttons_layout.addWidget(QtWidgets.QPushButton("重置"))
        layout.addLayout(buttons_layout)
        
        return tab
    
    def _create_data_tab(self):
        """创建数据展示选项卡
        
        Returns:
            数据展示选项卡
        """
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # 创建表格
        table = QtWidgets.QTableWidget(10, 5)
        table.setHorizontalHeaderLabels(["ID", "姓名", "年龄", "性别", "职业"])
        
        # 添加示例数据
        data = [
            (1, "张三", 25, "男", "工程师"),
            (2, "李四", 30, "男", "教师"),
            (3, "王五", 28, "男", "医生"),
            (4, "赵六", 35, "男", "律师"),
            (5, "钱七", 22, "女", "学生"),
            (6, "孙八", 40, "男", "经理"),
            (7, "周九", 27, "女", "设计师"),
            (8, "吴十", 33, "男", "会计"),
            (9, "郑十一", 29, "女", "销售"),
            (10, "王十二", 31, "男", "程序员")
        ]
        
        for row, (id_, name, age, gender, job) in enumerate(data):
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(id_)))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(age)))
            table.setItem(row, 3, QtWidgets.QTableWidgetItem(gender))
            table.setItem(row, 4, QtWidgets.QTableWidgetItem(job))
        
        layout.addWidget(table)
        
        # 创建图表（使用简单的进度条代替）
        chart_group = QtWidgets.QGroupBox("年龄分布")
        chart_layout = QtWidgets.QVBoxLayout(chart_group)
        
        age_ranges = ["18-25", "26-30", "31-35", "36-40", "41+"]
        values = [2, 3, 3, 1, 1]  # 对应上面数据的年龄分布
        
        for age_range, value in zip(age_ranges, values):
            progress = QtWidgets.QProgressBar()
            progress.setRange(0, 10)
            progress.setValue(value)
            chart_layout.addWidget(QtWidgets.QLabel(f"{age_range}: {value}人"))
            chart_layout.addWidget(progress)
        
        layout.addWidget(chart_group)
        
        return tab
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        file_menu.addAction("新建")
        file_menu.addAction("打开")
        file_menu.addAction("保存")
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        edit_menu.addAction("撤销")
        edit_menu.addAction("重做")
        edit_menu.addSeparator()
        edit_menu.addAction("剪切")
        edit_menu.addAction("复制")
        edit_menu.addAction("粘贴")
        
        # 视图菜单
        view_menu = menu_bar.addMenu("视图")
        view_menu.addAction("放大")
        view_menu.addAction("缩小")
        view_menu.addAction("重置缩放")
        
        # 主题菜单
        theme_menu = menu_bar.addMenu("主题")
        
        # 添加自动检测主题选项
        auto_action = theme_menu.addAction("自动检测")
        auto_action.triggered.connect(self.theme_manager.apply_auto_theme)
        
        theme_menu.addSeparator()
        
        # 添加所有主题
        for theme in self.theme_manager.get_available_themes():
            action = theme_menu.addAction(theme.display_name)
            action.triggered.connect(lambda checked, name=theme.name: self.theme_manager.set_theme(name))
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        help_menu.addAction("关于", self._show_about_dialog)
        
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = self.statusBar()
        status_bar.showMessage("就绪")
        
    def _show_about_dialog(self):
        """显示关于对话框"""
        QtWidgets.QMessageBox.about(
            self,
            "关于QtThemeHub示例应用",
            "QtThemeHub示例应用\n\n"
            "这是一个展示QtThemeHub功能的示例应用。\n"
            "QtThemeHub是一个跨Qt绑定的主题管理解决方案，\n"
            "支持PyQt5/PySide2/PyQt6/PySide6。"
        )


def main():
    """主函数"""
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
