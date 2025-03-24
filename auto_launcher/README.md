# 自动启动器 (Auto Launcher)

这是一个基于系统资源自动管理多个进程实例的工具。它能够根据CPU和内存使用情况，动态调整运行的实例数量，确保系统资源得到最优利用。

## 功能特点

- **资源监控**：实时监控系统CPU和内存使用情况
- **自动扩缩容**：根据系统资源动态调整实例数量
- **资源测试**：自动测试单个实例的资源消耗
- **配置灵活**：支持JSON和YAML格式的配置文件
- **命令行参数**：支持通过命令行参数覆盖配置
- **健康检查**：检测并处理僵尸进程和无响应进程
- **平滑扩缩容**：避免一次性启动或停止过多实例
- **详细日志**：记录系统状态和操作过程
- **失败保护**：连续失败后进入冷却期，避免反复尝试
- **资源波动保护**：系统资源波动大时暂停调整
- **分级日志**：控制台显示重要信息，文件记录详细日志

## 安装依赖

```bash
pip install psutil
# 如果需要YAML配置支持
pip install pyyaml
```

## 使用方法

1. 将目标程序（如`wuyanzhengma.exe`）复制到`auto_launcher`目录
2. 根据需要修改配置文件（`config.json`或`config.yaml`）
3. 运行自动启动器：

```bash
python auto_manager.py
```

## 配置文件

支持JSON和YAML两种格式的配置文件，默认使用`config.json`。

### 配置文件路径

程序按以下优先级查找配置文件：

1. 命令行参数指定的路径（`--config`）
2. 环境变量`AUTO_LAUNCHER_CONFIG_DIR`指定的目录
3. 当前工作目录（如果存在配置文件）
4. 程序所在目录

您可以通过以下方式指定配置文件：

```bash
# 使用命令行参数指定配置文件（绝对或相对路径）
python auto_manager.py --config /path/to/my_config.json
python auto_manager.py --config ../configs/config.yaml

# 使用环境变量指定配置目录
# Windows
set AUTO_LAUNCHER_CONFIG_DIR=D:\configs
# Linux/macOS
export AUTO_LAUNCHER_CONFIG_DIR=/path/to/configs
```

### JSON格式示例

```json
{
    "exe_name": "wuyanzhengma.exe",
    "max_cpu_percent": 80.0,
    "max_memory_percent": 80.0,
    "check_interval": 10,
    "max_instances": 50,
    "launch_params": "clientNumber: 50 headless: 1 target: shop delta: shop wait: 0",
    "safe_threshold": 0.2,
    "test_duration": 15,
    "sample_interval": 1,
    "max_retries": 3,
    "max_sample_time": 2.0,
    "logging": {
        "level": "INFO",
        "max_size_mb": 10,
        "backup_count": 5,
        "format": "%(asctime)s [%(levelname)s] %(message)s",
        "console_level": "INFO",
        "file_level": "DEBUG"
    }
}
```

### YAML格式示例

```yaml
# 基本设置
exe_name: wuyanzhengma.exe
max_cpu_percent: 80.0
max_memory_percent: 80.0
check_interval: 10
max_instances: 50
launch_params: "clientNumber: 50 headless: 1 target: shop delta: shop wait: 0"
safe_threshold: 0.2

# 测试设置
test_duration: 15
sample_interval: 1
max_retries: 3
max_sample_time: 2.0

# 日志设置
logging:
  level: INFO
  max_size_mb: 10
  backup_count: 5
  format: "%(asctime)s [%(levelname)s] %(message)s"
  console_level: INFO
  file_level: DEBUG
```

## 配置参数说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| exe_name | 字符串 | 可执行文件名称 | wuyanzhengma.exe |
| max_cpu_percent | 浮点数 | CPU使用率上限（百分比） | 80.0 |
| max_memory_percent | 浮点数 | 内存使用率上限（百分比） | 80.0 |
| check_interval | 整数 | 检查间隔（秒） | 10 |
| max_instances | 整数 | 最大实例数 | 50 |
| launch_params | 字符串 | 启动参数 | clientNumber: 50 headless: 1 target: shop delta: shop wait: 0 |
| safe_threshold | 浮点数 | 系统资源安全阈值（百分比） | 0.2 |
| test_duration | 整数 | 资源测试持续时间（秒） | 15 |
| sample_interval | 整数 | 采样间隔（秒） | 1 |
| max_retries | 整数 | 资源测试最大重试次数 | 3 |
| max_sample_time | 浮点数 | 单次资源采样最大允许时间(秒) | 2.0 |
| logging.level | 字符串 | 日志级别 | INFO |
| logging.max_size_mb | 整数 | 日志文件最大大小（MB） | 10 |
| logging.backup_count | 整数 | 日志文件备份数量 | 5 |
| logging.format | 字符串 | 日志格式 | %(asctime)s [%(levelname)s] %(message)s |
| logging.console_level | 字符串 | 控制台日志级别 | INFO |
| logging.file_level | 字符串 | 文件日志级别 | DEBUG |

## 命令行参数

可以通过命令行参数覆盖配置文件中的设置：

```bash
python auto_manager.py --config config.yaml --config-dir /path/to/configs --exe myapp.exe --max-cpu 70 --max-mem 75 --max-instances 30 --params "param1 param2" --max-retries 5 --max-sample-time 1.5
```

| 参数 | 说明 |
|------|------|
| --config | 配置文件路径（支持绝对路径和相对路径） |
| --config-dir | 配置文件目录，如果指定，将在此目录中查找配置文件 |
| --exe | 可执行文件名称 |
| --max-cpu | CPU使用率上限 |
| --max-mem | 内存使用率上限 |
| --max-instances | 最大实例数 |
| --params | 启动参数 |
| --max-retries | 资源测试最大重试次数 |
| --max-sample-time | 单次资源采样最大允许时间(秒) |

## 日志

日志文件保存在`logs`目录下，文件名格式为`auto_launcher_YYYYMMDD_HHMMSS.log`。日志记录了系统状态、资源使用情况和操作过程。

## 优化特性

### 1. 资源波动保护

系统会监控CPU和内存使用率的波动情况，当波动幅度超过10%时，暂停实例数调整，避免因资源波动导致频繁启停实例。

### 2. 失败保护机制

如果连续3次启动实例失败，系统会进入10分钟的冷却期，期间不再尝试启动新实例，避免反复失败。

### 3. 平滑扩缩容

- 每次最多启动3个实例，避免瞬时负载过高
- 每次最多停止2个实例，避免服务能力突然下降
- 实例启动间隔会根据当前实例数动态调整

### 4. 分级日志

- 控制台只显示重要信息（INFO级别及以上）
- 日志文件记录详细信息（DEBUG级别及以上）
- 可通过配置文件调整日志级别

### 5. 资源测试重试机制

- 当资源测试过程中测试实例意外终止时，会自动重试
- 最多重试次数可通过`max_retries`参数配置（默认为3次）
- 每次重试都会记录详细日志，便于排查问题
- 如果所有重试都失败，将使用保守的资源估计值
- 单次采样时间限制为`max_sample_time`秒（默认2秒），防止采样过程阻塞

## 注意事项

1. 确保目标程序（如`wuyanzhengma.exe`）位于`auto_launcher`目录下
2. 首次运行时会自动创建默认配置文件
3. 资源测试阶段需要约30秒时间，请耐心等待
4. 可以通过Ctrl+C安全停止程序，它会自动清理所有启动的进程
5. 如果系统资源波动较大，程序会自动暂停调整实例数，直到资源稳定
6. 配置文件可以放在不同位置，程序会按优先级查找
7. 如果资源测试过程中出现问题，程序会自动重试，无需手动干预
