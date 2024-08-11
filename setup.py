from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("lang/interpret.py", compiler_directives={"language_level": "3"})
)
