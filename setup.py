import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mptools",
    version="1.0.10",
    author="Manuele Pesenti",
    author_email="manuele@inventati.org",
    description="A very custom collection of development shared libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manuelep/mptools",
    project_urls={
        "Bug Tracker": "https://github.com/manuelep/mptools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"": ['*.sql', '*.md']},
    python_requires=">=3.6",
    install_requires=[
        "py4web",
        "pandas",
        "matplotlib",
        "numpy",
        "diskcache",
        "pytopojson",
    ],
    entry_points={
    'console_scripts': [
        'dbgenie = mptools.command_line:dbgenie'
    ],
}, 
)

