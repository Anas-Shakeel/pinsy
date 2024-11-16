import codecs
from os.path import join, abspath, dirname
from setuptools import setup, find_packages


def readme():
    with codecs.open(join(abspath(dirname(__file__)), "README.md"), encoding="utf-8") as f:
        return f.read()


setup(
    name='pinsy',
    version='0.1.2',
    description='A Python package to help speed up the workflow of creating beautiful CLI apps.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/Anas-Shakeel/pinsy',
    author='Anas Shakeel',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "colorama",
        "cursor",
        "ansy"
    ],
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
    entry_points={
        "console_scripts": [
            'pinsy=pinsy.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
