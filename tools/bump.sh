#!/usr/bin/env bash
# Bump the version in pyproject.toml, commit and tag it, and push: the tag
# triggers .github/workflows/release.yml, which publishes to PyPI.
#
#     pixi run bump [major|minor|patch]   # default: patch
set -euo pipefail

# --frozen: rewrite pyproject.toml without locking (this repo has pixi.lock, no
# uv.lock). The read below must not pass it: with no uv.lock, a read with
# --frozen fails, while a plain read neither locks nor syncs.
uv version --bump "${1:-patch}" --frozen
version="$(uv version --short)"
git commit -m "Bump version: ${version}" pyproject.toml
git tag -a "v${version}" -m "v${version}"
git push --follow-tags
