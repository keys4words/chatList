# Setup Instructions for GitHub Release & Pages

## Files Created

All necessary files have been created for publishing your application on GitHub Release and GitHub Pages.

### Documentation Files

1. **GITHUB_RELEASE_GUIDE.md** - Comprehensive step-by-step guide
2. **QUICK_START_RELEASE.md** - Quick reference guide
3. **RELEASE_CHECKLIST.md** - Pre-release checklist
4. **RELEASE_NOTES_TEMPLATE.md** - Template for release notes
5. **SETUP_INSTRUCTIONS.md** - This file

### Scripts

1. **prepare_release.ps1** - Prepares release files automatically
2. **.github/workflows/release.yml** - GitHub Actions workflow for automated releases

### Web Files

1. **index.html** - Landing page (root version)
2. **docs/index.html** - Landing page (for GitHub Pages using /docs folder)

## Required Customizations

Before using these files, you need to customize them with your information:

### 1. Update Landing Pages

Edit both `index.html` and `docs/index.html`:

- Replace `YOUR_USERNAME` with your GitHub username (appears 8+ times)
- Replace `chatList` with your repository name if different
- Update version numbers (currently v1.0.0)
- Add screenshots if available (uncomment screenshot sections)
- Customize feature descriptions if needed

**Quick find/replace:**
- `YOUR_USERNAME` → `your-github-username`
- `chatList` → `your-repo-name` (if different)

### 2. Update Release Notes Template

Edit `RELEASE_NOTES_TEMPLATE.md`:

- Replace `YOUR_USERNAME` with your GitHub username
- Update feature descriptions
- Add actual bug fixes and changes
- Update links

### 3. Update GitHub Actions Workflow (Optional)

Edit `.github/workflows/release.yml`:

- No changes needed if repository structure matches
- Adjust paths if your build process differs

### 4. Update Release Scripts

The scripts should work as-is, but verify:
- `prepare_release.ps1` - Checks version from `version.py` automatically
- Build scripts should match your project structure

## Quick Setup Steps

1. **Customize landing pages:**
   ```powershell
   # Use find/replace in your editor
   # Replace YOUR_USERNAME with your GitHub username
   ```

2. **Test the landing page locally:**
   - Open `docs/index.html` in a browser
   - Verify all links work
   - Check that styling looks good

3. **Prepare your first release:**
   ```powershell
   .\prepare_release.ps1
   ```

4. **Follow QUICK_START_RELEASE.md** for your first release

## File Structure

```
chatList/
├── .github/
│   └── workflows/
│       └── release.yml          # Automated release workflow
├── docs/
│   └── index.html               # GitHub Pages landing page
├── index.html                   # Alternative landing page (root)
├── GITHUB_RELEASE_GUIDE.md     # Full guide
├── QUICK_START_RELEASE.md       # Quick guide
├── RELEASE_CHECKLIST.md         # Pre-release checklist
├── RELEASE_NOTES_TEMPLATE.md    # Release notes template
├── prepare_release.ps1          # Release preparation script
└── SETUP_INSTRUCTIONS.md        # This file
```

## GitHub Pages Setup

### Option 1: Using /docs folder (Recommended)

1. Keep `docs/index.html` as is
2. In GitHub Settings → Pages:
   - Source: `main` branch
   - Folder: `/docs`
3. Your page will be at: `https://YOUR_USERNAME.github.io/chatList/`

### Option 2: Using root folder

1. Move `index.html` to root (or use the existing one)
2. In GitHub Settings → Pages:
   - Source: `main` branch
   - Folder: `/ (root)`
3. Your page will be at: `https://YOUR_USERNAME.github.io/chatList/`

### Option 3: Using gh-pages branch

1. Create a `gh-pages` branch
2. Copy `docs/index.html` to root of gh-pages branch
3. In GitHub Settings → Pages:
   - Source: `gh-pages` branch
   - Folder: `/ (root)`

## Testing Checklist

Before publishing:

- [ ] Landing page opens correctly in browser
- [ ] All links work (GitHub, releases, issues)
- [ ] Version numbers are correct
- [ ] YOUR_USERNAME replaced everywhere
- [ ] Repository name is correct
- [ ] Download links point to correct release URLs
- [ ] Release notes template is customized
- [ ] Screenshots added (if available)

## Common Issues

### Landing page not showing

- Wait 5-10 minutes after enabling Pages
- Check GitHub Actions tab for build errors
- Verify file is in correct location (docs/ or root)
- Check Pages settings in repository Settings

### Release files not uploading

- Check file size (GitHub limit: 100MB per file)
- Verify files exist in `release` folder
- Try uploading one file at a time

### Links not working

- Verify YOUR_USERNAME is replaced
- Check repository name is correct
- Test links manually in browser

## Next Steps

1. Customize all files with your information
2. Test landing page locally
3. Follow QUICK_START_RELEASE.md for first release
4. Set up GitHub Pages
5. Create your first release!

## Support

For detailed instructions, see:
- **GITHUB_RELEASE_GUIDE.md** - Full comprehensive guide
- **QUICK_START_RELEASE.md** - Quick reference
- **RELEASE_CHECKLIST.md** - Pre-release checklist

