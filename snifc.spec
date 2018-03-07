# -*- mode: python -*-

block_cipher = None


def Entrypoint(dist, group, name,
               scripts=None, pathex=None, hiddenimports=None,
               datas=None, excludes=None, runtime_hooks=None):
    import pkg_resources

    # get toplevel packages of distribution from metadata
    def get_toplevel(dist):
        distribution = pkg_resources.get_distribution(dist)
        if distribution.has_metadata('top_level.txt'):
            return list(distribution.get_metadata('top_level.txt').split())
        else:
            return []

    hiddenimports = hiddenimports or []

    scripts = scripts or []
    pathex = pathex or []
    # get the entry point
    ep = pkg_resources.get_entry_info(dist, group, name)
    # insert path of the egg at the verify front of the search path
    pathex = [ep.dist.location] + pathex
    # script name must not be a valid module name to avoid name clashes on import
    script_path = os.path.join(workpath, name + '-script.py')
    print ("creating script for entry point", dist, group, name)
    with open(script_path, 'w') as fh:
        print("import", ep.module_name, file=fh)
        print("%s.%s()" % (ep.module_name, '.'.join(ep.attrs)), file=fh)
        for package in hiddenimports:
            print ("import", package, file=fh)

    return Analysis([script_path] + scripts, pathex=pathex, hiddenimports=hiddenimports, datas=datas, excludes=excludes, runtime_hooks=runtime_hooks)

added_files = [
    ('snifc/gui/dialogo_capturar.ui', 'gui'),
    ('snifc/gui/main.ui', 'gui'),
    ('snifc/pyshark/config.ini', 'pyshark')
]

a = Entrypoint(
    'snifc', 'console_scripts', 'snifc',
    hiddenimports=['py._vendored_packages.iniconfig'],
    datas=added_files
)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# DIR
# ===
# exe = EXE(pyz,
#           a.scripts,
#           exclude_binaries=True,
#           name='snifc',
#           debug=False,
#           strip=False,
#           upx=True,
#           console=True )
# coll = COLLECT(exe,
#                a.binaries,
#                a.zipfiles,
#                a.datas,
#                strip=False,
#                upx=True,
#                name='snifc')

# ONEFILE
# =======
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='snifc',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
