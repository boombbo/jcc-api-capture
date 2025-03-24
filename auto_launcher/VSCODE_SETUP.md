# VSCode 开发环境配置指南

本文档提供了使用 VSCode 开发和调试自动启动器的完整指南。

## 1. 开发环境配置

我们已经为您准备了完整的 VSCode 配置，包括：

- 终端设置：支持中文显示，设置合适的工作目录
- 调试配置：多种启动模式，满足不同需求
- 任务配置：常用操作的快捷运行方式
- 类型检查设置：更严格的代码质量控制

## 2. 调试功能使用

### 使用调试配置

在 VSCode 左侧的"运行和调试"面板中，您可以选择以下预配置的调试选项：

1. **启动自动管理器** - 使用默认设置启动
2. **启动管理器(自定义配置)** - 使用 config.yaml 和自定义参数
3. **启动管理器(测试模式)** - 快速测试模式，缩短测试时间
4. **调试配置管理器** - 单独调试配置管理器模块
5. **终端诊断模式** - 在外部终端窗口运行，查看完整输出

使用方法：选择配置 -> 按 F5 运行 -> 在需要的地方设置断点

### 使用任务运行

1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Tasks: Run Task"
3. 选择以下任务之一：
   - **运行自动管理器** - 标准运行模式
   - **快速测试模式** - 使用缩短的测试参数
   - **测试配置加载** - 仅测试配置文件加载
   - **创建日志目录** - 确保日志目录存在
   - **清理日志** - 删除所有日志文件

## 3. PowerShell 增强配置

我们提供了 PowerShell 配置文件 `PowerShell_profile.ps1`，用于改善终端体验：

### 安装方法

1. 在 PowerShell 中运行 `notepad $PROFILE` 打开配置文件
2. 将 `auto_launcher/PowerShell_profile.ps1` 的内容复制到打开的文件中
3. 保存并关闭
4. 重启 PowerShell 终端

### 可用命令

安装后，在 PowerShell 终端中可以使用以下命令：

- `Start-AutoLauncher` - 启动自动管理器
- `Start-TestMode` - 以测试模式启动
- `Clear-Logs` - 清理日志文件

## 4. 类型检查与问题修复

我们配置了 Pylance 类型检查，以提高代码质量。常见类型错误及其修复方法：

### "X is not a known attribute of None"

这类错误表示您在可能为 `None` 的对象上调用方法。修复方法：

```python
# 修复前
result = obj.method()

# 修复后
if obj is not None:
    result = obj.method()
else:
    result = default_value
```

### "Expression of type None cannot be assigned to parameter of type X"

当函数参数注解与实际传入值类型不匹配时出现。修复方法：

```python
# 修复前
def func(param: str = None):
    pass

# 修复后
from typing import Optional
def func(param: Optional[str] = None):
    pass
```

### 配置错误级别

如果某些类型错误过于严格，可以在 `.vscode/settings.json` 中调整其严重性：

```json
"python.analysis.diagnosticSeverityOverrides": {
    "reportOptionalMemberAccess": "information",
    "reportUnknownMemberType": "none"
}
```

## 5. 终端问题排查

如果遇到终端相关问题，请参考 `TERMINAL_TROUBLESHOOTING.md` 文档，其中提供了详细的故障排除步骤。
