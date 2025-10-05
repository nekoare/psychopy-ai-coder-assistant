# Release Checklist for PyPI

Use this checklist each time you prepare a release.

## 1. Confirm Metadata
- [ ] `pyproject.toml` has correct `version`, `name`, `description`, `license`, `readme`
- [ ] `src/psychopy_ai_coder_assistant/__init__.py` `__version__` matches pyproject
- [ ] Classifiers include supported Python versions
- [ ] URLs (Homepage/Repository/Issues) are valid

## 2. Update Version
```bash
# Choose new version, e.g. 0.1.1
sed -i 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml
sed -i 's/__version__ = "0.1.0"/__version__ = "0.1.1"/' src/psychopy_ai_coder_assistant/__init__.py
```

## 3. Clean & Build
```bash
rm -rf dist build *.egg-info
python -m build
```

## 4. Inspect Artifacts
```bash
ls -1 dist/
unzip -l dist/*.whl | head
```

## 5. Run Tests Against Built Wheel
```bash
python -m venv /tmp/ai_release_test
source /tmp/ai_release_test/bin/activate
pip install --upgrade pip
pip install dist/*.whl
python - <<'PY'
import psychopy_ai_coder_assistant as m, importlib.metadata as md
print('Version:', m.__version__)
print('Entry points:', [e.name for e in md.entry_points(group='psychopy.plugins')])
PY
```

## 6. Upload to TestPyPI (first time or dry run)
```bash
pip install --upgrade twine
python -m twine upload --repository testpypi dist/*
# Verify on https://test.pypi.org/project/psychopy-ai-coder-assistant/
```

## 7. Install from TestPyPI (Optional)
```bash
python -m venv /tmp/testpypi_env
source /tmp/testpypi_env/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple psychopy-ai-coder-assistant
python -c "import psychopy_ai_coder_assistant, sys; print('OK', psychopy_ai_coder_assistant.__version__)"
```

## 8. Upload to PyPI
```bash
python -m twine upload dist/*
```

## 9. Git Tag & Push
```bash
git tag v0.1.1
git push origin v0.1.1
```

## 10. Post Release
- [ ] Update CHANGELOG / RELEASE_NOTES
- [ ] Announce (Forum / README badge optional)
- [ ] Increment dev version (e.g. 0.1.2-dev) in `main` if desired

## 11. Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| 400 Invalid Metadata | README rendering error | `twine check dist/*` before upload |
| Missing entry point | Version mismatch or build stale | Rebuild after bump, verify wheel contents |
| Install fails on wxPython | Platform wheel absent | Document system libs, advise pip retry |

## 12. Automation (Future)
- GitHub Actions workflow to run tests & build on tag
- Automated publish on pushing semver tag matching `v*`
