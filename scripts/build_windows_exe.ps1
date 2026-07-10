$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $ProjectDir ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$AppName = "Lazy Integration"

if (-not (Test-Path $VenvDir)) {
    py -3 -m venv $VenvDir
}

& $PythonExe -m pip install -r (Join-Path $ProjectDir "requirements.txt")

$DistDir = Join-Path $ProjectDir "dist"
$BuildDir = Join-Path $ProjectDir "build"
$SpecFile = Join-Path $ProjectDir "$AppName.spec"

if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}

if (Test-Path $BuildDir) {
    Remove-Item $BuildDir -Recurse -Force
}

if (Test-Path $SpecFile) {
    Remove-Item $SpecFile -Force
}

& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name $AppName `
    --icon (Join-Path $ProjectDir "app.ico") `
    --add-data "$ProjectDir\templates;templates" `
    --add-data "$ProjectDir\logs;logs" `
    "$ProjectDir\main.py"

Write-Host ""
Write-Host "Build complete."
Write-Host "Output: $ProjectDir\dist\$AppName.exe"
