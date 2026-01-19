# Script to prepare files for GitHub release
# Usage: .\prepare_release.ps1

Write-Host "Preparing release files..." -ForegroundColor Green

# Get version from version.py
$versionFile = Get-Content "version.py"
$versionMatch = $versionFile | Select-String '__version__ = "(.*)"'
if ($versionMatch) {
    $version = $versionMatch.Matches.Groups[1].Value
    Write-Host "Detected version: $version" -ForegroundColor Cyan
} else {
    Write-Host "Error: Could not find version in version.py" -ForegroundColor Red
    exit 1
}

# Create release directory
$releaseDir = "release"
if (Test-Path $releaseDir) {
    Write-Host "Cleaning existing release directory..." -ForegroundColor Yellow
    Remove-Item $releaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

Write-Host "`nCopying files..." -ForegroundColor Cyan

# Copy installer
$installerPath = "installer\ChatList-Setup-v$version.exe"
if (Test-Path $installerPath) {
    Copy-Item $installerPath -Destination $releaseDir\
    Write-Host "  ✓ Copied installer" -ForegroundColor Green
} else {
    Write-Host "  ✗ Installer not found: $installerPath" -ForegroundColor Yellow
    Write-Host "    Run .\build_installer.ps1 first" -ForegroundColor Yellow
}

# Copy standalone executable
$exePath = "dist\ChatList-v$version.exe"
if (Test-Path $exePath) {
    Copy-Item $exePath -Destination $releaseDir\
    Write-Host "  ✓ Copied standalone executable" -ForegroundColor Green
} else {
    Write-Host "  ✗ Executable not found: $exePath" -ForegroundColor Yellow
    Write-Host "    Run .\build.ps1 first" -ForegroundColor Yellow
}

# Copy documentation
if (Test-Path "README.md") {
    Copy-Item "README.md" -Destination $releaseDir\
    Write-Host "  ✓ Copied README.md" -ForegroundColor Green
}

if (Test-Path "LICENSE") {
    Copy-Item "LICENSE" -Destination $releaseDir\
    Write-Host "  ✓ Copied LICENSE" -ForegroundColor Green
}

# Create release notes if template exists
if (Test-Path "RELEASE_NOTES_TEMPLATE.md") {
    $releaseNotes = Get-Content "RELEASE_NOTES_TEMPLATE.md" -Raw
    $releaseNotes = $releaseNotes -replace "v1\.0\.0", "v$version"
    $releaseNotes | Out-File "$releaseDir\RELEASE_NOTES.md" -Encoding UTF8
    Write-Host "  ✓ Created RELEASE_NOTES.md" -ForegroundColor Green
}

Write-Host "`nRelease files prepared in '$releaseDir' directory" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Review files in '$releaseDir' folder" -ForegroundColor White
Write-Host "2. Update RELEASE_NOTES.md if needed" -ForegroundColor White
Write-Host "3. Create GitHub release:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/YOUR_USERNAME/chatList/releases/new" -ForegroundColor White
Write-Host "   - Tag: v$version" -ForegroundColor White
Write-Host "   - Upload files from '$releaseDir' folder" -ForegroundColor White
Write-Host "   - Copy content from RELEASE_NOTES.md" -ForegroundColor White

