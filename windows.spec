# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\main.py'],
             pathex=['C:\\switcher'],
             binaries=[],
             datas=[
                 ('res', 'res'),
                 ('manifest.yaml', '.'),
                 ('LICENSE', '.'),
             ],
             hiddenimports=["qasync"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='switcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
