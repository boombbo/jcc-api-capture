# 自动启动器终端故障排除指南

本文档提供了在使用自动启动器过程中可能遇到的终端相关问题的解决方案。

## 常见问题

### 1. 终端启动失败

#### 问题表现

- 终端尝试启动但立即关闭
- 出现错误代码（如 1, 259, 3221225786 等）
- 提示"本机异常"或其他错误信息

#### 解决方案

1. **使用诊断模式**

   使用VSCode调试面板中的"终端诊断模式"配置。这会在外部终端窗口中启动程序，通常能够显示更详细的错误信息。

2. **检查Python环境**

   确保已正确安装Python和所需的库：

   ```
   python --version
   pip list
   ```

3. **检查防病毒软件**

   某些防病毒软件可能会阻止终端进程启动。尝试暂时禁用防病毒软件，或将VSCode及Python添加到排除列表中。

4. **检查Windows兼容模式**

   右击VSCode可执行文件，选择"属性"，确保未启用"以兼容模式运行此程序"。

### 2. 资源测试缓慢

#### 问题表现

- 资源测试阶段进度缓慢
- 采样间隔不正常，如从1秒跳到6秒

#### 解决方案

1. **调整采样参数**

   使用命令行参数减少测试持续时间和采样超时：

   ```
   python auto_manager.py --test-duration 10 --max-sample-time 1.0
   ```

2. **使用任务运行**

   通过VSCode任务运行器执行"快速测试模式"任务。

3. **检查系统负载**

   如果系统资源已接近上限，可能会导致采样过程变慢。关闭不必要的应用程序后再试。

### 3. 中文字符显示问题

#### 问题表现

- 终端中的中文字符显示为方块或乱码
- 日志中的中文无法正确显示

#### 解决方案

1. **设置正确的编码**

   在`.vscode/settings.json`中设置终端编码：

   ```json
   "terminal.integrated.env.windows": {
       "PYTHONIOENCODING": "utf-8"
   }
   ```

2. **使用兼容字体**

   在终端设置中使用支持中文的字体：

   ```json
   "terminal.integrated.fontFamily": "Consolas, 'Microsoft YaHei', monospace"
   ```

3. **检查PowerShell编码**

   如果使用PowerShell，可能需要在配置文件中设置UTF-8编码：

   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```

## 特定错误代码解决方案

### 退出代码 1

通常表示一般性错误。检查Python解释器路径和参数是否正确。对于WSL，确保已设置有效的默认分发版：

```
wslconfig.exe /l
wslconfig.exe /setdefault Ubuntu
```

### 退出代码 259 (STILL_ACTIVE)

检查是否有旧的进程未正确关闭。重启VSCode或计算机可能有助于解决问题。

### 退出代码 3221225786

检查是否启用了旧版控制台模式。打开cmd.exe，右键点击标题栏，选择"属性"，在"选项"选项卡下取消勾选"使用旧版控制台"。

## 启用终端日志

若问题持续存在，可以启用VSCode的终端跟踪日志：

1. 打开VSCode设置 (Ctrl+,)
2. 搜索 `terminal.integrated.trace`
3. 将值设置为 `true` 或 `verbose`
4. 重启VSCode，重现问题
5. 从菜单中选择 "帮助" > "切换开发人员工具"
6. 在开发者工具的控制台中，可以看到终端相关的日志

## 提高终端性能

对于资源密集型操作，可以尝试以下设置：

```json
"terminal.integrated.gpuAcceleration": "auto",
"terminal.integrated.rendererType": "dom",
"terminal.integrated.experimentalLinkProvider": false
```

## 联系支持

如果以上解决方案都无法解决您的问题，请提供以下信息联系支持：

1. VSCode版本 (`Help > About`)
2. 操作系统版本
3. 终端日志
4. 错误代码和详细描述
5. 尝试过的解决方案
