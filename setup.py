# -*- coding: utf-8 -*-


import sys

main_dependencies = [
    "setuptools"
]

for dep in main_dependencies:
    try:
        __import__(dep)
    except ImportError:
        print(
            "Error: You do not have %s installed, please\n"
            "       install it. For example doing\n"
            "\n"
            "       pip install %s\n" % (dep, dep)
        )
        sys.exit(1)


from setuptools import setup
import adg


setup(
    name='ADG - Automated Diagram Generator',
    maintainer='Pierre Arthuis',
    maintainer_email='pierre.arthuis@pm.me',
    url='https://github.com/alejandrogallo/papis',
    install_requires=[
        "networkx>=2.0",
        "numpy",
    ],
    python_requires='=2.7',
    classifiers=[
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
    ],
    description='A powerful diagram generator and evaluator for many-body '
                'formalisms in physics and chemistry',
    long_description='',
    keywords=[
        'physics',
        'chemistry',
        'theory',
        'many-body',
        'diagram',
        'cli',
        'batch'
    ],
    packages=[
        "adg",
    ],
    entry_points=dict(
        console_scripts=[
            'adg=adg.main:main'
        ]
    ),
    platforms=['linux', 'osx'],
)
