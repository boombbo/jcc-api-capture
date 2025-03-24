# 自动化开发环境准备脚本

# 确保在auto_launcher目录下运行
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 检查虚拟环境是否存在
if (-not (Test-Path '.\venv')) {
    Write-Host '创建虚拟环境...' -ForegroundColor Cyan
    python -m venv venv
    if (-not $?) {
        Write-Host '创建虚拟环境失败，请确保已安装Python 3.6+' -ForegroundColor Red
        exit 1
    }
}

# 激活虚拟环境
Write-Host '激活虚拟环境...' -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host '安装依赖...' -ForegroundColor Cyan
pip install -r requirements.txt

# 检查keyboard库是否需要管理员权限
$keyboardInstalled = $false
try {
    $modules = pip list
    if ($modules -like '*keyboard*') {
        $keyboardInstalled = $true
    }
}
catch {
    Write-Host '检查keyboard库安装状态时出错' -ForegroundColor Yellow
}

if (-not $keyboardInstalled) {
    Write-Host '警告: keyboard库可能需要管理员权限才能安装和使用' -ForegroundColor Yellow
    Write-Host '如需使用ESC键退出功能，请以管理员身份运行PowerShell，然后执行:' -ForegroundColor Yellow
    Write-Host '   pip install keyboard' -ForegroundColor Yellow
}

# 确保日志目录存在
if (-not (Test-Path '.\logs')) {
    Write-Host '创建日志目录...' -ForegroundColor Cyan
    New-Item -ItemType Directory -Path '.\logs' | Out-Null
}

# 提示启动命令
Write-Host "`n环境准备完成！" -ForegroundColor Green
Write-Host '可以使用以下命令启动程序:' -ForegroundColor Cyan
Write-Host '   python auto_manager.py' -ForegroundColor White
Write-Host "或在VSCode中使用'运行自动管理器'任务" -ForegroundColor Cyan
Write-Host "按ESC键可随时退出程序`n" -ForegroundColor Yellow 
