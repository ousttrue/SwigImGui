from distutils.core import setup, Extension


imgui_module = Extension('_swig_imgui',
        sources=[
            'imgui_wrap.cxx',
            'imgui/imgui.cpp',
            'imgui/imgui_draw.cpp',
            'imgui/imgui_demo.cpp',
            ],
        )

setup (name = 'swig_imgeui',
        version = '0.1',
        author      = "ousttrue",
        description = """imgui wrapper using swig""",
        ext_modules = [imgui_module],
        py_modules = ["imgui"],
        )

