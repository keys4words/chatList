# GitHub Release & GitHub Pages Publishing Guide

This guide will help you publish ChatList application on GitHub Releases and create a landing page on GitHub Pages.

## Prerequisites

- GitHub account and repository
- Git installed and configured
- GitHub CLI (optional, but recommended) or access to GitHub web interface

## Part 1: Preparing for Release

### Step 1: Update Version

Before creating a release, update the version in `version.py`:

```python
__version__ = "1.0.0"  # Update to new version, e.g., "1.0.1"
```

### Step 2: Build the Application

1. **Build the executable:**
   ```powershell
   .\build.ps1
   ```
   This creates `dist\ChatList-v1.0.0.exe`

2. **Build the installer:**
   ```powershell
   .\build_installer.ps1
   ```
   This creates `installer\ChatList-Setup-v1.0.0.exe`

### Step 3: Prepare Release Files

Create a `release` folder and copy necessary files:

```powershell
# Create release directory
New-Item -ItemType Directory -Path "release" -Force

# Copy installer
Copy-Item "installer\ChatList-Setup-v*.exe" -Destination "release\"

# Copy standalone executable (optional)
Copy-Item "dist\ChatList-v*.exe" -Destination "release\"

# Copy README and LICENSE
Copy-Item "README.md" -Destination "release\"
Copy-Item "LICENSE" -Destination "release\"
```

Or use the provided script:
```powershell
.\prepare_release.ps1
```

## Part 2: Creating GitHub Release

### Method 1: Using GitHub Web Interface (Recommended for First Time)

1. **Go to your repository on GitHub**

2. **Click "Releases" → "Create a new release"**

3. **Fill in the release information:**
   - **Tag version:** `v1.0.0` (must start with 'v')
   - **Release title:** `ChatList v1.0.0` or `Release v1.0.0`
   - **Description:** Copy content from `RELEASE_NOTES_TEMPLATE.md` or write your own

4. **Upload files:**
   - Click "Attach binaries"
   - Upload `ChatList-Setup-v1.0.0.exe` (installer)
   - Optionally upload `ChatList-v1.0.0.exe` (standalone)

5. **Check "Set as the latest release"** (if this is your latest version)

6. **Click "Publish release"**

### Method 2: Using GitHub CLI

1. **Install GitHub CLI:**
   ```powershell
   winget install GitHub.cli
   ```

2. **Authenticate:**
   ```powershell
   gh auth login
   ```

3. **Create release:**
   ```powershell
   gh release create v1.0.0 `
     installer\ChatList-Setup-v1.0.0.exe `
     --title "ChatList v1.0.0" `
     --notes-file RELEASE_NOTES_TEMPLATE.md
   ```

### Method 3: Using Git Tags (Manual)

1. **Create and push a tag:**
   ```powershell
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Then create release on GitHub web interface** using the tag you just created

## Part 3: Setting Up GitHub Pages

### Step 1: Enable GitHub Pages

1. Go to your repository → **Settings** → **Pages**

2. Under **Source**, select:
   - **Branch:** `gh-pages` (or `main` if you want to use main branch)
   - **Folder:** `/ (root)` or `/docs` if you use docs folder

3. Click **Save**

### Step 2: Prepare HTML Landing Page

1. **Create `docs` folder** (or use root if you selected root in Pages settings)

2. **Copy the landing page:**
   ```powershell
   Copy-Item "index.html" -Destination "docs\index.html"
   ```

3. **Update the landing page** with your repository URL and information

4. **Commit and push:**
   ```powershell
   git add docs\index.html
   git commit -m "Add GitHub Pages landing page"
   git push origin main
   ```

### Step 3: Access Your Landing Page

Your page will be available at:
```
https://YOUR_USERNAME.github.io/YOUR_REPOSITORY_NAME/
```

Example:
```
https://maxim.github.io/chatList/
```

## Part 4: Automated Release Workflow (Optional)

If you want to automate releases, use the GitHub Actions workflow provided in `.github/workflows/release.yml`.

### Setup:

1. **Create `.github/workflows` directory:**
   ```powershell
   New-Item -ItemType Directory -Path ".github\workflows" -Force
   ```

2. **Copy the workflow file:**
   ```powershell
   Copy-Item "release.yml" -Destination ".github\workflows\"
   ```

3. **Push to repository:**
   ```powershell
   git add .github\workflows\release.yml
   git commit -m "Add automated release workflow"
   git push origin main
   ```

### Using Automated Workflow:

1. **Update version** in `version.py`
2. **Create a tag:**
   ```powershell
   git tag v1.0.1
   git push origin v1.0.1
   ```
3. **The workflow will automatically:**
   - Build the application
   - Create installer
   - Create GitHub release
   - Upload files

## Part 5: Release Checklist

Before publishing, make sure:

- [ ] Version updated in `version.py`
- [ ] Application builds successfully
- [ ] Installer builds successfully
- [ ] Application tested on clean Windows system
- [ ] Release notes prepared
- [ ] Files ready in `release` folder
- [ ] Git repository is clean and up to date
- [ ] All changes committed
- [ ] Tag created (if using tags)

## Part 6: Updating Landing Page

To update the landing page:

1. Edit `docs/index.html` (or `index.html` if using root)
2. Update version numbers, features, screenshots
3. Commit and push:
   ```powershell
   git add docs\index.html
   git commit -m "Update landing page"
   git push origin main
   ```

## Troubleshooting

### Release not appearing
- Check that tag starts with 'v' (e.g., `v1.0.0`)
- Verify files uploaded successfully
- Check release is published (not draft)

### GitHub Pages not working
- Check Pages settings in repository Settings
- Verify `index.html` exists in selected folder
- Wait a few minutes for GitHub to build the page
- Check Actions tab for build errors

### Files too large
- GitHub has 100MB file size limit for releases
- Use installer instead of standalone executable if needed
- Consider using Git LFS for large files

## Next Steps

- Set up automated releases with GitHub Actions
- Add screenshots to release notes
- Create changelog file (CHANGELOG.md)
- Add badges to README.md
- Set up issue templates

