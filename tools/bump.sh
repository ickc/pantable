#!/usr/bin/env bash
# Bump the version in pyproject.toml, commit and tag it, and push: the tag
# triggers .github/workflows/release.yml, which publishes to PyPI.
#
#     pixi run bump [major|minor|patch]   # default: patch
set -euo pipefail

uv version --bump "${1:-patch}" --frozen
version="$(uv version --short --frozen)"
git commit -m "Bump version: ${version}" pyproject.toml
git tag -a "v${version}" -m "v${version}"
git push --follow-tags
