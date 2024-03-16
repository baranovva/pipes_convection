# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['webbrowser.open_new', 'tkinter.ttk', 'tkinter.scrolledtext', 'tkinter.BooleanVar', 'tkinter.Checkbutton',
                   'math.log', 'math.pi', 'numpy.arange', 'numpy.array', 'numpy.where',
                   'pandas.read_csv',
                   'sklearn.linear_model.LinearRegression',
                   'sklearn.preprocessing.PolynomialFeatures',
                   'sklearn.model_selection.GridSearchCV',
                   'sklearn.pipeline.make_pipeline',
                   'functools.wraps'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Convection',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    bundle_files=1,
    zip_files=None,
    zip_include_packages=None,
    zip_exclude_packages=None,
    stashing=False,
    upx_exclude=[],
    upx_dir=None,
    runtime_tmpdir=None,
    console_exe=None,
    strip_target_libs=True,
    onefile=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Convection',
    clean=True
)
