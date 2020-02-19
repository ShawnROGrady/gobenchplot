from setuptools import setup

setup(
    name='gobenchplot',
    version='0.1.0',
    packages=['gobenchplot'],
    entry_points={
            'console_scripts': [
                'gobenchplot = gobenchplot.__main__:main',
            ],
    })
