# PowerShell配置文件
# 将此文件复制到 $PROFILE 位置（可通过在PowerShell中输入 $PROFILE 查看）

# 设置终端编码为UTF-8，解决中文显示问题
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# 设置环境变量
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = (Get-Location).Path

# 设置工作目录为auto_launcher
$AutoLauncherPath = Join-Path (Get-Location).Path 'auto_launcher'
if (Test-Path $AutoLauncherPath) {
    Set-Location $AutoLauncherPath
    Write-Host "已切换到自动启动器目录: $AutoLauncherPath" -ForegroundColor Green
}

# 定义全局变量用于进程控制
$global:AutoLauncherProcesses = @()

# 定义便捷函数

# 快速运行自动启动器
function Start-AutoLauncher {
    param (
        [string]$ConfigFile = 'config.json',
        [int]$TestDuration = 15,
        [float]$MaxSampleTime = 1.0
    )
    
    Write-Host "启动自动管理器 (配置文件: $ConfigFile)" -ForegroundColor Cyan
    $process = Start-Process -FilePath python -ArgumentList "auto_manager.py --config $ConfigFile --test-duration $TestDuration --max-sample-time $MaxSampleTime" -PassThru -NoNewWindow
    $global:AutoLauncherProcesses += $process
    Write-Host "进程已启动 (PID: $($process.Id))，按ESC键可随时退出" -ForegroundColor Yellow
    return $process
}

# 快速测试模式
function Start-TestMode {
    Write-Host '启动测试模式' -ForegroundColor Yellow
    $process = Start-Process -FilePath python -ArgumentList 'auto_manager.py --test-duration 10 --max-sample-time 1.0' -PassThru -NoNewWindow
    $global:AutoLauncherProcesses += $process
    Write-Host "进程已启动 (PID: $($process.Id))，按ESC键可随时退出" -ForegroundColor Yellow
    return $process
}

# 清理日志
function Clear-Logs {
    $LogPath = Join-Path (Get-Location).Path 'logs'
    if (Test-Path $LogPath) {
        Remove-Item (Join-Path $LogPath '*.log') -Force
        Write-Host '日志已清理' -ForegroundColor Green
    }
    else {
        Write-Host '日志目录不存在' -ForegroundColor Red
    }
}

# 终止所有自动启动器进程
function Stop-AllAutoLaunchers {
    $count = 0
    foreach ($proc in $global:AutoLauncherProcesses) {
        if (($proc -ne $null) -and (-not $proc.HasExited)) {
            try {
                $proc.Kill()
                $count++
                Write-Host "已终止进程 PID: $($proc.Id)" -ForegroundColor Green
            }
            catch {
                Write-Host "终止进程 PID: $($proc.Id) 失败: $_" -ForegroundColor Red
            }
        }
    }
    
    # 尝试查找并终止其他python自动启动器进程
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -ne $null -and $_.CommandLine -ne $null -and $_.CommandLine -like '*auto_manager.py*'
    }
    
    foreach ($proc in $pythonProcesses) {
        try {
            $proc.Kill()
            $count++
            Write-Host "已终止其他自动启动器进程 PID: $($proc.Id)" -ForegroundColor Green
        }
        catch {
            Write-Host "终止进程 PID: $($proc.Id) 失败: $_" -ForegroundColor Red
        }
    }
    
    # 搜索wuyanzhengma.exe进程并终止
    $wuyanzhengmaProcesses = Get-Process -Name wuyanzhengma -ErrorAction SilentlyContinue
    foreach ($proc in $wuyanzhengmaProcesses) {
        try {
            $proc.Kill()
            $count++
            Write-Host "已终止wuyanzhengma进程 PID: $($proc.Id)" -ForegroundColor Green
        }
        catch {
            Write-Host "终止进程 PID: $($proc.Id) 失败: $_" -ForegroundColor Red
        }
    }
    
    $global:AutoLauncherProcesses = @()
    
    if ($count -gt 0) {
        Write-Host "成功终止了 $count 个进程" -ForegroundColor Green
    }
    else {
        Write-Host '没有找到需要终止的进程' -ForegroundColor Yellow
    }
}

# 紧急终止所有Python进程（用于紧急情况）
function Stop-AllPythonProcesses {
    $count = 0
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
    
    foreach ($proc in $pythonProcesses) {
        try {
            $proc.Kill()
            $count++
            Write-Host "已强制终止Python进程 PID: $($proc.Id)" -ForegroundColor Red
        }
        catch {
            Write-Host "终止Python进程 PID: $($proc.Id) 失败: $_" -ForegroundColor Red
        }
    }
    
    if ($count -gt 0) {
        Write-Host "紧急模式：强制终止了 $count 个Python进程" -ForegroundColor Red
    }
    else {
        Write-Host '没有找到Python进程' -ForegroundColor Yellow
    }
}

# 设置ESC键作为快速退出键
function Set-EscapeHandler {
    # 检查是否已经有PSReadLine模块
    if (Get-Module -ListAvailable -Name PSReadLine) {
        # 设置ESC键绑定
        Set-PSReadLineKeyHandler -Key Escape -ScriptBlock {
            # 清除当前输入行
            [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
            
            # 显示提示信息
            Write-Host "`n[ESC] 正在终止所有自动启动器进程..." -ForegroundColor Red
            
            # 执行终止命令
            Stop-AllAutoLaunchers
            
            # 恢复命令提示符
            [Microsoft.PowerShell.PSConsoleReadLine]::AcceptLine()
        }
        Write-Host 'ESC键已绑定为紧急退出功能，在任何时候按ESC可立即终止所有自动启动器进程' -ForegroundColor Cyan
    }
    else {
        Write-Host '未安装PSReadLine模块，无法设置ESC键绑定。请使用Stop-AllAutoLaunchers命令手动退出' -ForegroundColor Yellow
        Write-Host '可以尝试安装PSReadLine: Install-Module -Name PSReadLine -Force' -ForegroundColor Yellow
    }
}

# 设置Ctrl+C组合键为强制终止所有Python进程
function Set-CtrlCHandler {
    if (Get-Module -ListAvailable -Name PSReadLine) {
        # 设置Ctrl+C键绑定
        Set-PSReadLineKeyHandler -Chord Ctrl+c -ScriptBlock {
            # 清除当前输入行
            [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
            
            # 显示警告信息
            Write-Host "`n[Ctrl+C] 紧急模式：正在强制终止所有Python进程..." -ForegroundColor Red
            
            # 执行紧急终止命令
            Stop-AllPythonProcesses
            
            # 恢复命令提示符
            [Microsoft.PowerShell.PSConsoleReadLine]::AcceptLine()
        }
        Write-Host 'Ctrl+C组合键已绑定为紧急强制终止功能，用于紧急情况下强制关闭所有Python进程' -ForegroundColor Red
    }
}

# 安装键盘处理器
Set-EscapeHandler
Set-CtrlCHandler

# 显示帮助信息
Write-Host '=== 自动启动器快捷命令 ===' -ForegroundColor Cyan
Write-Host 'Start-AutoLauncher     - 启动自动管理器' -ForegroundColor White
Write-Host 'Start-TestMode         - 以测试模式启动' -ForegroundColor White
Write-Host 'Clear-Logs             - 清理日志文件' -ForegroundColor White
Write-Host 'Stop-AllAutoLaunchers  - 终止所有自动启动器进程' -ForegroundColor White
Write-Host 'Stop-AllPythonProcesses - 紧急强制终止所有Python进程' -ForegroundColor Red
Write-Host '[ESC]                  - 随时按ESC键快速终止所有进程' -ForegroundColor Yellow
Write-Host '[Ctrl+C]               - 紧急强制终止所有Python进程' -ForegroundColor Red
Write-Host '=========================' -ForegroundColor Cyan 
