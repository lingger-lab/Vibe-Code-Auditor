# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Collect Streamlit data files and metadata
streamlit_datas = collect_data_files('streamlit')
streamlit_metadata = copy_metadata('streamlit')
altair_metadata = copy_metadata('altair')
plotly_metadata = copy_metadata('plotly')

# Collect all submodules
all_hidden_imports = [
    'streamlit', 'plotly', 'anthropic', 'rich', 'click', 'yaml', 'pylint',
    'streamlit.web', 'streamlit.web.cli', 'streamlit.runtime',
    'streamlit.runtime.scriptrunner', 'streamlit.runtime.state',
    'altair', 'tornado', 'watchdog', 'validators',
    'plotly.graph_objs', 'pandas', 'numpy', 'pyarrow'
]

a = Analysis(
    ['vibe_auditor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # Include source code
        ('docs', 'docs'),  # Include documentation
    ] + streamlit_datas + streamlit_metadata + altair_metadata + plotly_metadata,
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
