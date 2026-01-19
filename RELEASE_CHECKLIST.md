# Release Checklist

Use this checklist before creating a new release on GitHub.

## Pre-Release

- [ ] **Version Updated**
  - [ ] Version number updated in `version.py`
  - [ ] Version matches planned release tag (e.g., v1.0.0)

- [ ] **Code Quality**
  - [ ] All tests pass
  - [ ] Code reviewed and approved
  - [ ] No known critical bugs
  - [ ] All changes committed to repository

- [ ] **Documentation**
  - [ ] README.md is up to date
  - [ ] Release notes prepared (RELEASE_NOTES_TEMPLATE.md)
  - [ ] User guide updated if needed
  - [ ] Changelog updated

## Build

- [ ] **Application Build**
  - [ ] Executable builds successfully (`.\build.ps1`)
  - [ ] Application runs without errors
  - [ ] Tested on clean Windows system

- [ ] **Installer Build**
  - [ ] Installer builds successfully (`.\build_installer.ps1`)
  - [ ] Installer tested on clean Windows system
  - [ ] Uninstaller works correctly
  - [ ] Shortcuts created properly

## Release Preparation

- [ ] **Files Prepared**
  - [ ] Release files prepared (`.\prepare_release.ps1`)
  - [ ] All files present in `release` folder
  - [ ] File sizes are reasonable (< 100MB each)
  - [ ] Files are virus-scanned (if applicable)

- [ ] **Release Notes**
  - [ ] Release notes updated with correct version
  - [ ] Features listed accurately
  - [ ] Bug fixes documented
  - [ ] Breaking changes highlighted (if any)
  - [ ] Links updated (GitHub URLs, etc.)

## GitHub Release

- [ ] **Tag Created**
  - [ ] Git tag created: `git tag v1.0.0`
  - [ ] Tag pushed: `git push origin v1.0.0`
  - [ ] Tag message is descriptive

- [ ] **Release Created**
  - [ ] Release created on GitHub
  - [ ] Tag selected correctly
  - [ ] Title is clear and descriptive
  - [ ] Release notes pasted correctly
  - [ ] Files uploaded (installer, standalone exe)
  - [ ] "Set as latest release" checked (if applicable)
  - [ ] Release published (not draft)

## Post-Release

- [ ] **Verification**
  - [ ] Release visible on GitHub Releases page
  - [ ] Download links work
  - [ ] Installer downloads and installs correctly
  - [ ] Application launches after installation

- [ ] **Announcement** (Optional)
  - [ ] Release announced on social media
  - [ ] Documentation updated
  - [ ] GitHub Pages landing page updated (if applicable)

- [ ] **Follow-up**
  - [ ] Monitor for issues
  - [ ] Respond to user feedback
  - [ ] Plan next release

## Notes

- Always test on a clean system before release
- Keep release notes concise but informative
- Include screenshots if possible
- Update version number immediately after release for next development cycle

