from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as test_command

import io
import os
import sys
import oshi

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst')


class PyTest(test_command):
    def __init__(self):
        self.test_args = []
        self.test_suite = True

    def finalize_options(self):
        test_command.finalize_options(self)

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='sandman',
    version=oshi.__version__,
    url='https://github.com/ferrarimarco/OSHI-monitoring',
    license='TBD',
    author='Marco Ferrari',
    tests_require=['pytest'],
    install_requires=['rrdtool>=0.1.2'],
    cmdclass={'test': PyTest},
    author_email='ferrari.marco@gmail.com',
    description='TBD',
    long_description=long_description,
    packages=['oshi.monitoring'],
    include_package_data=True,
    platforms='any',
    test_suite='oshi.monitoring.test.test_oshi_monitoring',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'],
    extras_require={
        'testing': ['pytest'],
    }
)
