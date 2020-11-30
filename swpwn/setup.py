from setuptools import setup, find_packages

setup(
    name='swpwn',
    version='0.3.1.2',
    description='swpwn docker image manipulation script, to simplify docker pwn environment management',
    author='swing',
    packages=['swpwn',],
    package_dir={'swpwn': 'src'},
    entry_points={
        'console_scripts': ['swpwn=swpwn.swpwn:main']
    },
    install_requires=[
        'docker',
    ]
)
