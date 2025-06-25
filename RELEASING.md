# Releasing mcp-gigapi

This document describes how to release a new version of mcp-gigapi to PyPI.

## Prerequisites

1. **PyPI Account**: You need a PyPI account with access to the `mcp-gigapi` package
2. **GitHub Repository Access**: You need push access to the repository
3. **PyPI API Token**: Create an API token in your PyPI account settings

## Setting up PyPI API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create a new API token with scope "Entire account (all projects)"
3. Copy the token (it starts with `pypi-`)
4. Add it to your GitHub repository secrets:
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add a new repository secret named `PYPI_API_TOKEN`
   - Paste your PyPI API token as the value

## Release Process

### 1. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
version = "0.1.1"  # or whatever the new version is
```

### 2. Update Changelog

Add release notes to the README or create a CHANGELOG.md file documenting the changes.

### 3. Create a Release

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Release v0.1.1"
   git push origin main
   ```

2. Create a new release on GitHub:
   - Go to the repository on GitHub
   - Click "Releases" in the right sidebar
   - Click "Create a new release"
   - Choose a tag (e.g., `v0.1.1`)
   - Add a release title (e.g., "Release v0.1.1")
   - Add release notes describing the changes
   - Click "Publish release"

### 4. Automatic Publishing

Once you publish the release, the GitHub Actions workflow will automatically:

1. Run all tests on multiple Python versions
2. Build the package
3. Publish to PyPI

You can monitor the progress in the "Actions" tab of your repository.

### 5. Verify the Release

After the workflow completes successfully:

1. Check PyPI: https://pypi.org/project/mcp-gigapi/
2. Verify the new version is available
3. Test installation:
   ```bash
   uv run --with mcp-gigapi --python 3.11 mcp-gigapi --help
   ```

## Manual Publishing (if needed)

If you need to publish manually:

```bash
# Install build tools
uv sync --all-extras --dev

# Build the package
uv build

# Publish to PyPI
uv run python -m twine upload dist/*
```

## Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check that your `PYPI_API_TOKEN` secret is correctly set
2. **Version Already Exists**: PyPI doesn't allow overwriting versions. Increment the version number
3. **Build Failures**: Check the GitHub Actions logs for specific error messages

### Rollback

If you need to rollback a release:

1. **PyPI**: PyPI doesn't support deleting packages, but you can yank a release:
   ```bash
   uv run python -m twine delete mcp-gigapi 0.1.1
   ```

2. **GitHub**: Delete the release tag and release on GitHub

## Security

- Never commit API tokens to the repository
- Use repository secrets for sensitive data
- Regularly rotate your PyPI API tokens
- Review the release before publishing 