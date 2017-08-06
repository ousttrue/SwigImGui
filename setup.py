# monkey patch for _msvccompiler
import distutils._msvccompiler
import os
import subprocess
def _get_vc_env(plat_spec):
    if os.getenv("DISTUTILS_USE_SDK"):
        return {
            key.lower(): value
            for key, value in os.environ.items()
        }

    vcvarsall, vcruntime = distutils._msvccompiler._find_vcvarsall(plat_spec)
    if not vcvarsall:
        raise DistutilsPlatformError("Unable to find vcvarsall.bat")

    try:
        out = subprocess.check_output(
            'cmd /u /c "{}" {} && set'.format(vcvarsall, plat_spec),
            stderr=subprocess.STDOUT,
        ).decode('utf-16le', errors='replace')
        #######################################################################
        if out.startswith("Error in script usage"):
            out = subprocess.check_output(
                'cmd /u /c "{}" {} && set'.format("C:\\Program Files (x86)\\Microsoft Visual C++ Build Tools\\vcbuildtools.bat", plat_spec),
                stderr=subprocess.STDOUT,
            ).decode('utf-16le', errors='replace')
        #######################################################################
    except subprocess.CalledProcessError as exc:
        log.error(exc.output)
        raise DistutilsPlatformError("Error executing {}"
                .format(exc.cmd))

    env = {
        key.lower(): value
        for key, _, value in
        (line.partition('=') for line in out.splitlines())
        if key and value
    }

    if vcruntime:
        env['py_vcruntime_redist'] = vcruntime
    return env
distutils._msvccompiler._get_vc_env=_get_vc_env


from distutils.core import setup, Extension


imgui_module = Extension('_swig_imgui',
        sources=[
            #'imgui_wrap.cxx',
            'imgui.i',
            'imgui/imgui.cpp',
            'imgui/imgui_draw.cpp',
            'imgui/imgui_demo.cpp',
            ],
        swig_opts=[
            '-modern',
            '-c++',
            '-py3',
            ]
        )

setup (name = 'swig_imgui',
        version = '0.1',
        author      = "ousttrue",
        description = """imgui wrapper using swig""",
        ext_modules = [imgui_module],
        py_modules = ["swig_imgui"],
        )
