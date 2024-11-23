from os.path import join, abspath, dirname
from setuptools import setup, find_packages


# Current working directory
cwd = abspath(dirname(__file__))


def readme():
    with open(join(cwd, "README.md"), encoding="utf-8") as f:
        try:
            return f.read()
        except:
            return None


setup(
    name="pinsy",
    version="0.2.3",
    description="A Python package to help speed up the workflow of creating beautiful CLI apps.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Anas-Shakeel/pinsy",
    author="Anas Shakeel",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["colorama", "cursor", "ansy", "readchar"],
    keywords=[
        "python",
        "cli",
        "command-line",
        "terminal",
        "text formatting",
        "color output",
        "CLI app development",
        "CLI tools",
        "terminal UI",
        "beautiful CLI apps",
        "text styling",
    ],
    entry_points={"console_scripts": ["pinsy=pinsy.cli:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.9",
)
