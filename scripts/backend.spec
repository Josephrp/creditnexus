# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec for building the CreditNexus backend executable.
Usage: pyinstaller --noconfirm --clean scripts/backend.spec
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

try:
    SPEC_PATH = Path(__file__).resolve()
except NameError:
    SPEC_PATH = Path.cwd() / "scripts" / "backend.spec"

PROJECT_ROOT = SPEC_PATH.parent.parent
BLOCK_CIPHER = None

hiddenimports = collect_submodules("app")
extra_datas = collect_data_files("app")

STATIC_DIRS = ["alembic", "data"]
for relative in STATIC_DIRS:
    source = PROJECT_ROOT / relative
    if source.exists():
        extra_datas.append((str(source), relative))

STATIC_FILES = ["alembic.ini", "README.md", "README_DATABASE_SETUP.md"]
for filename in STATIC_FILES:
    file_path = PROJECT_ROOT / filename
    if file_path.exists():
        extra_datas.append((str(file_path), filename))

a = Analysis(
    [str(PROJECT_ROOT / "run_backend.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=extra_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=BLOCK_CIPHER,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=BLOCK_CIPHER)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="creditnexus-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="creditnexus-backend",
)
