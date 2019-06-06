from distutils.core import setup
from Cython.Build import cythonize

setup(name='Simluator', ext_modules=cythonize('evaluate_order.pyx'))
