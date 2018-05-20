from setuptools import setup, find_packages

setup(
    name='dscan',
    version='0.1',
    packages=[''],
    url='https://github.com/nico-duitsmann/dscan',
    license='GNU GPL v3',
    author='Nico Duitsmann',
    author_email='nico.duitsmann.privat@gmail.com',
    description='Command line utility to search data for matching patterns',
    entry_points={
        'console_scripts': [
            'dscan = dscan'
        ]
    },
    install_requires=['docopt', 'termcolor'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU GPL v3',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)