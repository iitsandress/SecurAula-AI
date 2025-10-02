param(
  [string]$PyInstaller = "pyinstaller"
)

Push-Location "$PSScriptRoot\..\agent"

if (-not (Test-Path ".\config.json")) {
  Write-Host "Sugerencia: copie config.example.json a config.json para empaquetarlo con el ejecutable (opcional)." -ForegroundColor Yellow
}

# Instalar PyInstaller si no está
python -m pip show pyinstaller *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Instalando PyInstaller..."
  python -m pip install pyinstaller
}

# Construir ejecutable de una sola carpeta (one-dir) para permitir editar config.json a posteriori
$icon = "$PSScriptRoot\..\server\static\edumon.ico"
$iconArg = (Test-Path $icon) ? "--icon `"$icon`"" : ""

& $PyInstaller --noconsole --name EduMonAgent --clean $iconArg main.py

Pop-Location

Write-Host "Hecho. Binarios en edumon/agent/dist/EduMonAgent/" -ForegroundColor Green
