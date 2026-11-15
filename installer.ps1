# Chekushka Adventure installer
$ErrorActionPreference = "Stop"
$Owner = "YOUR_GITHUB_USERNAME"
$Repo = "YOUR_REPO"
$Branch = "main"
$InstallDir = Join-Path $env:LOCALAPPDATA "ChekushkaAdventure"
$PythonVersion = "3.13.7"
$PythonInstaller = Join-Path $env:TEMP "python-$PythonVersion-amd64.exe"

Write-Host "=== Установка Chekushka Adventure ===" -ForegroundColor Cyan
Write-Host "Папка установки: $InstallDir"

function Find-Python {
    $commands = @("py", "python")
    foreach ($cmd in $commands) {
        try {
            $v = & $cmd --version 2>$null
            if ($LASTEXITCODE -eq 0 -and $v -match "Python 3\.(1[1-9]|[2-9][0-9])") { return $cmd }
        } catch {}
    }
    return $null
}

$PythonCmd = Find-Python
if (-not $PythonCmd) {
    Write-Host "Python не найден. Пробую установить Python 3.13..." -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        try {
            winget install --id Python.Python.3.13 -e --scope user --silent --accept-package-agreements --accept-source-agreements
        } catch {}
    }
    $PythonCmd = Find-Python
    if (-not $PythonCmd) {
        Write-Host "Скачиваю официальный установщик Python..." -ForegroundColor Yellow
        $url = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
        Invoke-WebRequest -Uri $url -OutFile $PythonInstaller
        Start-Process -FilePath $PythonInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_tcltk=1 Include_test=0" -Wait
        Remove-Item $PythonInstaller -Force -ErrorAction SilentlyContinue
        $PythonCmd = Find-Python
    }
}
if (-not $PythonCmd) {
    throw "Не удалось установить Python. Установи Python 3.13 с python.org и включи Tcl/Tk."
}

Write-Host "Проверяю Tkinter..."
$tkOk = $false
try {
    & $PythonCmd -c "import tkinter" 2>$null
    $tkOk = ($LASTEXITCODE -eq 0)
} catch {}
if (-not $tkOk) {
    throw "В Python отсутствует Tkinter. Переустанови Python 3.13 с компонентом Tcl/Tk and IDLE."
}

Write-Host "Скачиваю игру с GitHub..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$zip = Join-Path $env:TEMP "chekushka-repo.zip"
$url = "https://codeload.github.com/$Owner/$Repo/zip/refs/heads/$Branch"
Invoke-WebRequest -Uri $url -OutFile $zip
$temp = Join-Path $env:TEMP "chekushka-repo"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $temp -Force
$source = Get-ChildItem $temp -Directory | Select-Object -First 1
if (-not $source) { throw "GitHub вернул пустой архив." }
Copy-Item (Join-Path $source.FullName "game\*") $InstallDir -Recurse -Force
Copy-Item (Join-Path $source.FullName "version.json") $InstallDir -Force
Remove-Item $zip -Force -ErrorAction SilentlyContinue
Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue

$launcher = Join-Path $InstallDir "Запустить игру.bat"
if (-not (Test-Path $launcher)) {
    @"
@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 chekushka_adventure.py
) else (
  python chekushka_adventure.py
)
if errorlevel 1 pause
"@ | Set-Content -Path $launcher -Encoding ASCII
}
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Chekushka Adventure.lnk"
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $InstallDir
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,44"
$shortcut.Save()

Write-Host "Готово! Игра установлена." -ForegroundColor Green
Start-Process $launcher
