# MuMu模拟器管理工具

一个用于管理MuMu模拟器的Python GUI工具。

## 功能特点

- 模拟器管理
  - 创建、克隆、备份模拟器
  - 查看模拟器信息
  - 管理模拟器配置

- 模拟器控制
  - 基本控制（启动、停止、重启）
  - 窗口管理
  - 应用管理

- 设置管理
  - 显示设置
  - 性能设置
  - 网络设置
  - 设备设置

- ADB工具
  - 命令执行
  - Shell交互

- 硬件管理
  - 驱动管理
  - 硬件模拟配置

## 安装要求

- Python 3.8+
- Windows 10/11
- MuMu模拟器

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/mumu-manager.git
cd mumu-manager
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置模拟器路径：
编辑 `config/settings.json` 文件，设置MuMu模拟器安装路径。

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 使用界面：
- 在"模拟器管理"标签页中管理模拟器
- 在"模拟器控制"标签页中控制模拟器
- 在"设置"标签页中配置模拟器
- 在"ADB工具"标签页中使用ADB命令
- 在"硬件管理"标签页中管理驱动和硬件配置

## 测试

运行测试：
```bash
python -m pytest tests/
```

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT License
