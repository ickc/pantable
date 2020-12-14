#!/usr/bin/env python

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(
    name='pantable',
    version='0.13.0',
    license='BSD-3-Clause',
    description='A Python library for writing pandoc filters for tables with batteries included.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Kolen Cheung',
    author_email='christian.kolen@gmail.com',
    url='https://github.com/ickc/pantable',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Filters',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://pantable.readthedocs.io/',
        'Changelog': 'https://pantable.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/ickc/pantable/issues',
    },
    keywords=[
        'pandoc',
        'pandocfilters',
        'panflute',
        'markdown',
        'latex',
        'html',
        'csv',
        'table',
    ],
    python_requires='>=3.7',
    install_requires=[
        'panflute>=2',
        'pyyaml',
        'numpy',
        'backports.cached_property; python_version < "3.8"',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': [
            'shutilwhich',
            'pep8',
            'pytest',
            'pytest-cov',
            'pytest-parallel',
            'coverage',
            'coveralls',
            'future',
            'tabulate',
            'sphinx',
            'sphinx_bootstrap_theme',
            'pygments-style-solarized',
            'data-science-types',
            'yamlloader',
            'coloredlogs',
        ],
    },
    entry_points={
        'console_scripts': [
            'pantable = pantable.cli.pantable:main',
            'pantable2csv = pantable.cli.pantable2csv:main',
            'pantable2csvx = pantable.cli.pantable2csvx:main',
        ]
    },
)
