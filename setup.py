import setuptools


version_namespace = {}
with open("xyztank/version.py") as f:
    exec(f.read(), version_namespace)


setuptools.setup(
    name="xyztank",
    version=version_namespace["__version__"],
    author="us4us Ltd.",
    author_email="support@us4us.eu",
    description="XYZ tank",
    long_description="XYZ tank",
    long_description_content_type="text/markdown",
    url="https://us4us.eu",
    packages=setuptools.find_packages(exclude=[]),
    classifiers=[
        "Development Status :: 1 - Planning",

        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",

        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    install_requires=[
        "numpy>=1.20.3"
    ],
    python_requires='>=3.8'
)