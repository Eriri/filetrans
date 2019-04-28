# -*- mode: python -*-

block_cipher = None


a = Analysis(['servergui.py'],
             pathex=['C:\\Z\\filetrans'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += (('favicon.ico','C:\\Z\\filetrans\\favicon.ico','DATA'),)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('favicon.ico','C:\\Z\\filetrans\\favicon.ico','DATA')],
          name='servergui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, icon='favicon.ico')
