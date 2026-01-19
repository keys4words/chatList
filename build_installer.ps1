Write-Host "Building executable..." -ForegroundColor Green
& .\build.ps1

Write-Host ""
Write-Host "Generating setup.iss..." -ForegroundColor Cyan
python generate_setup.py

Write-Host ""
Write-Host "Building installer with Inno Setup..." -ForegroundColor Green

$innoSetupPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$isccPath = $null
foreach ($path in $innoSetupPaths) {
    if (Test-Path $path) {
        $isccPath = $path
        break
    }
}

if ($isccPath) {
    & $isccPath setup.iss
    Write-Host ""
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer build complete! Check the 'installer' folder." -ForegroundColor Green
    } else {
        Write-Host "Error building installer. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} else {
    Write-Host "Inno Setup not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Inno Setup:" -ForegroundColor Yellow
    Write-Host "1. Run: .\install_inno_setup.ps1" -ForegroundColor Cyan
    Write-Host "   OR" -ForegroundColor Cyan
    Write-Host "2. Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "   Install it, then run this script again." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Alternatively, you can manually run ISCC.exe with setup.iss" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}

Read-Host "Press Enter to continue"

