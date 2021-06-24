from setuptools import setup,find_packages


with open('README.rst') as f:
    long_description = f.read()

VERSION = "0.1"

setup(
    name='xaal.sensfloor',
    version=VERSION,
    license='GPL License',
    author='Quentin Mahé',
    #url='',
    description=('xAAL SensFloor devices' ),
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['xaal', 'sensfloor'],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'xaal.lib',
        'gevent',
        'pycrypto',
    ]
)
