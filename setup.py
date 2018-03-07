from setuptools import setup

version = "0.0.1"

requirements = [
    'pyshark',
    'PyQt5',
    'PyQtChart'
]

setup(
    name="snifc",
    version=version,
    description="Sniffer de pacotes",
    author="yurihs",
    packages=["snifc"],
    packagedir={"snifc": "snifc"},
    include_package_data=True,
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': [
            'snifc=snifc.gui:run'
        ]
    }
)
