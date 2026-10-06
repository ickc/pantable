"""Run the filters as pandoc runs them.

The tests that go through here know nothing of the AST library pantable is
built on: they give pandoc a document and a filter, and read what comes out.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
GOLDEN = Path(__file__).parent / "golden"
FILTERS = ("pantable", "pantable2csv", "pantable2csvx")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        help="write the filters' output to tests/golden/*/expected/ instead of comparing with it",
    )


def filter_path(name: str) -> str:
    """The console script installed beside this Python, else the one on PATH."""
    path = os.pathsep.join((str(Path(sys.executable).parent), os.environ.get("PATH", "")))
    exe = shutil.which(name, path=path)
    if exe is None:
        raise FileNotFoundError(f"{name} is not installed")
    return exe


def pandoc(
    *args: str,
    text: str | None = None,
    filters: tuple[str, ...] = (),
    cwd: Path = ROOT,
) -> subprocess.CompletedProcess[str]:
    """Run pandoc, by default from the repository root, as the include paths in tests/golden are relative to it.

    Its output is decoded as is, without translating newlines: pantable writes CSV with CRLF.
    """
    cmd = ["pandoc", *(f"--filter={filter_path(f)}" for f in filters), *args]
    res = subprocess.run(cmd, input=None if text is None else text.encode(), capture_output=True, check=True, cwd=cwd)
    return subprocess.CompletedProcess(res.args, res.returncode, res.stdout.decode(), res.stderr.decode())
