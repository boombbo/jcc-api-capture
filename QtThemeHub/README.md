# QtThemeHub

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

跨Qt绑定的主题管理解决方案，一键切换多种视觉风格。

## 功能特性

- 🎨 **多主题支持**：内置QDarkStyle、Material Design等流行主题
- 🔄 **动态切换**：运行时无缝切换主题
- 🛠️ **扩展性强**：支持自定义QSS主题
- 📱 **高DPI适配**：自动处理不同屏幕缩放比例
- 🚦 **安全可靠**：主题验证和错误处理机制
- 🌓 **自动适配**：自动检测系统暗色/亮色模式

## 安装

```bash
# 从GitHub克隆
git clone https://github.com/yourusername/QtThemeHub.git
cd QtThemeHub

# 安装依赖
pip install qtpy

# 可选依赖（用于更多主题）
pip install qdarkstyle pyqtdarktheme qt-material
```

## 快速开始

```python
from qtpy import QtWidgets
from QtThemeHub import ThemeManager

# 创建应用
app = QtWidgets.QApplication([])

# 初始化主题管理器
theme_mgr = ThemeManager(app)

# 应用自动检测的主题
theme_mgr.apply_auto_theme()

# 或者指定主题
# theme_mgr.set_theme('qdarkstyle_dark')

# 创建窗口
window = QtWidgets.QMainWindow()
window.setWindowTitle("QtThemeHub示例")
window.resize(400, 300)
window.show()

# 运行应用
app.exec()
```

## 主题选择器

QtThemeHub提供了一个现成的主题选择器组件，可以轻松集成到你的应用中：

```python
from qtpy import QtWidgets
from QtThemeHub import ThemeManager
from QtThemeHub.ui import ThemeSelector

# 创建应用
app = QtWidgets.QApplication([])

# 初始化主题管理器
theme_mgr = ThemeManager(app)

# 创建窗口
window = QtWidgets.QMainWindow()
window.setWindowTitle("主题选择器示例")
window.resize(600, 400)

# 创建主题选择器
selector = ThemeSelector(theme_mgr)

# 设置为中央部件
window.setCentralWidget(selector)
window.show()

# 运行应用
app.exec()
```

## 支持的主题

QtThemeHub自动检测并支持以下主题库：

1. **QDarkStyle**
   - `qdarkstyle_dark` - QDarkStyle暗色主题
   - `qdarkstyle_light` - QDarkStyle亮色主题

2. **PyQtDarkTheme**
   - `qdarktheme_dark` - PyQtDarkTheme暗色主题
   - `qdarktheme_light` - PyQtDarkTheme亮色主题

3. **Qt-Material**
   - 多种Material Design主题，如`material_dark_blue`、`material_light_blue`等

4. **自定义主题**
   - 放置在`themes/custom`目录下的`.qss`文件会自动加载

## 自定义主题

你可以通过以下方式添加自定义主题：

1. **添加QSS文件**

   将QSS文件放置在`themes/custom`目录下，QtThemeHub会自动加载。

2. **编程方式添加**

   ```python
   # 加载自定义主题
   theme_path = "path/to/your/theme.qss"
   theme = theme_mgr.load_custom_theme("my_theme", theme_path)
   
   # 应用自定义主题
   theme_mgr.set_theme(theme.name)
   ```

3. **添加自定义主题目录**

   ```python
   # 添加自定义主题目录
   theme_mgr.add_custom_theme_dir("path/to/your/themes")
   ```

## 高级用法

### 主题变更事件

你可以监听主题变更事件，以便在主题变更时执行自定义操作：

```python
def on_theme_changed(theme):
    print(f"主题已变更为: {theme.display_name}")

# 连接信号
theme_mgr.themeChanged.connect(on_theme_changed)
```

### 主题验证

QtThemeHub提供了主题验证功能，可以检查主题文件的有效性：

```python
from QtThemeHub.utils import validate_theme

# 验证主题
is_valid, errors = validate_theme("path/to/your/theme.qss")
if not is_valid:
    print("主题验证失败:")
    for error in errors:
        print(f"- {error}")
```

## 示例应用

QtThemeHub提供了一个完整的示例应用，展示了如何使用QtThemeHub的各种功能：

```bash
# 运行示例应用
python -m QtThemeHub.examples.basic_app
```

## 兼容性

QtThemeHub支持以下Qt绑定：

- PyQt5 (5.9.0+)
- PySide2 (5.12.0+)
- PyQt6 (6.2.0+)
- PySide6 (6.2.0+)

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。
