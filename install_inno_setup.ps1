# Script to download and install Inno Setup
# Then build the ChatList installer

Write-Host "Checking for Inno Setup installation..." -ForegroundColor Cyan

# Check common installation paths
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
        Write-Host "Found Inno Setup at: $path" -ForegroundColor Green
        break
    }
}

if (-not $isccPath) {
    Write-Host "Inno Setup not found. Downloading and installing..." -ForegroundColor Yellow
    
    # Download URL for Inno Setup 6
    $downloadUrl = "https://jrsoftware.org/download.php/is.exe"
    $installerPath = "$env:TEMP\innosetup-installer.exe"
    
    Write-Host "Downloading Inno Setup 6 from $downloadUrl..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "Download complete." -ForegroundColor Green
        
        Write-Host "Installing Inno Setup..." -ForegroundColor Cyan
        Write-Host "Please follow the installation wizard. After installation, run this script again." -ForegroundColor Yellow
        
        # Run the installer
        Start-Process -FilePath $installerPath -Wait
        
        Write-Host "Installation complete. Checking again..." -ForegroundColor Green
        
        # Check again after installation
        foreach ($path in $innoSetupPaths) {
            if (Test-Path $path) {
                $isccPath = $path
                Write-Host "Found Inno Setup at: $path" -ForegroundColor Green
                break
            }
        }
        
        # Clean up installer
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
    catch {
        Write-Host "Error downloading or installing Inno Setup: $_" -ForegroundColor Red
        Write-Host "Please download and install Inno Setup manually from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
        exit 1
    }
}

if ($isccPath) {
    Write-Host "`nBuilding installer..." -ForegroundColor Green
    Write-Host "Using: $isccPath" -ForegroundColor Cyan
    
    # Change to script directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir
    
    # Build the installer
    & $isccPath setup.iss
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nInstaller built successfully! Check the 'installer' folder." -ForegroundColor Green
    }
    else {
        Write-Host "`nError building installer. Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Inno Setup still not found after installation attempt." -ForegroundColor Red
    Write-Host "Please install Inno Setup manually from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "Or add ISCC.exe to your PATH environment variable." -ForegroundColor Yellow
    exit 1
}

