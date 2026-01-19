# Quick Start: Publishing to GitHub Release & Pages

This is a condensed guide for quickly publishing your application.

## Prerequisites

- GitHub repository created
- Git configured and repository cloned locally
- Application built and tested

## Step 1: Update Version

Edit `version.py`:
```python
__version__ = "1.0.0"  # Update to your release version
```

## Step 2: Build Application

```powershell
# Build executable
.\build.ps1

# Build installer
.\build_installer.ps1
```

## Step 3: Prepare Release Files

```powershell
.\prepare_release.ps1
```

This creates a `release` folder with all necessary files.

## Step 4: Create Git Tag

```powershell
git add .
git commit -m "Release v1.0.0"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

## Step 5: Create GitHub Release

1. Go to: `https://github.com/YOUR_USERNAME/chatList/releases/new`
2. Select tag: `v1.0.0`
3. Title: `ChatList v1.0.0`
4. Description: Copy from `RELEASE_NOTES_TEMPLATE.md` (update version numbers)
5. Upload files from `release` folder:
   - `ChatList-Setup-v1.0.0.exe`
   - `ChatList-v1.0.0.exe` (optional)
6. Click "Publish release"

## Step 6: Set Up GitHub Pages

1. Go to: `https://github.com/YOUR_USERNAME/chatList/settings/pages`
2. Source: `gh-pages` branch or `main` branch `/docs` folder
3. Click "Save"

## Step 7: Update Landing Page

1. Edit `docs/index.html` (or `index.html` if using root)
2. Replace `YOUR_USERNAME` with your GitHub username
3. Update version numbers
4. Commit and push:

```powershell
git add docs/index.html
git commit -m "Update landing page"
git push origin main
```

## Step 8: Verify

- **Release:** Check `https://github.com/YOUR_USERNAME/chatList/releases`
- **Pages:** Check `https://YOUR_USERNAME.github.io/chatList/` (may take a few minutes)

## That's It! 🎉

Your application is now published on GitHub Release and GitHub Pages.

## Next Time

For subsequent releases:
1. Update version in `version.py`
2. Run `.\prepare_release.ps1`
3. Create new tag and push
4. Create new release on GitHub
5. Update landing page if needed

## Need More Details?

See `GITHUB_RELEASE_GUIDE.md` for comprehensive instructions.

