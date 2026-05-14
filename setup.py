# -*- coding: utf-8 -*-


import os
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np


extensions = [
    Extension(
        "nextrngbook.dx_generator._dx_generator32", 
        sources=[
            os.path.join("src", "nextrngbook", "dx_generator", "_dx_generator32.pyx"), 
            os.path.join("src", "nextrngbook", "dx_generator", "src", "dx_k_s_32.c")
        ],
        include_dirs=[
            np.get_include(),
            os.path.join(os.path.dirname(__file__), "src", "nextrngbook", "dx_generator", "src")
        ],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    ),
]

setup(
    name="nextrngbook",
    packages=find_packages(where="src", 
                           exclude=["nextrngbook.dx_generator.data", 
                                    "nextrngbook.dx_generator.src"]),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={"nextrngbook.dx_generator": ["data/*"]},
    ext_modules=cythonize(extensions, language_level="3str")
)