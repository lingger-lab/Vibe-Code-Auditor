# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect Streamlit data files
streamlit_datas = collect_data_files('streamlit')

# Collect all submodules
all_hidden_imports = [
    'streamlit', 'plotly', 'anthropic', 'rich', 'click', 'yaml', 'pylint',
    'streamlit.web', 'streamlit.web.cli', 'altair', 'tornado',
    'plotly.graph_objs', 'pandas', 'numpy', 'pyarrow'
]

a = Analysis(
    ['vibe_auditor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # Include source code
        ('docs', 'docs'),  # Include documentation
    ] + streamlit_datas,
    hiddenimports=all_hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow', 'tensorflow-gpu', 'tf_keras',
        'torch', 'torchvision', 'torchaudio',
        'sklearn', 'scikit-learn',
        'scipy.linalg', 'scipy.stats', 'scipy.spatial',
        'sympy', 'numba', 'llvmlite'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VibeAuditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
