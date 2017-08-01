"""CSV Tables in Markdown: Pandoc Filter for CSV Tables

See:
https://github.com/ickc/pantable
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# Version comparison
from pkg_resources import parse_version
# To use a consistent encoding
from codecs import open
from os import path

# Set description in install_requires for the reason why we at least need this
# version of setuptools.
assert parse_version(setuptools.__version__) >= parse_version("20.6.8"), \
    "Setuptools version 20.6.8 or heigher i required.  Updated it using `pip install -U setuptools`."

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Import version number
version = {}
with open("pantable/version.py") as f:
    exec(f.read(), version)
version = version['__version__']

setup(
    name='pantable',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='CSV Tables in Markdown: Pandoc Filter for CSV Tables',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/ickc/pantable',

    # Author details
    author='Kolen Cheung',
    author_email='christian.kolen@gmail.com',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Filters',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

    # What does your project relate to?
    keywords='pandoc pandocfilters panflute markdown latex html',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'panflute>=1.8.2',
        # Need newer version of setuptools, to support environment markers as
        # per PEP 508. It seems to work from around 20.2.2, but some bug fixes
        # were added up till 20.6.8
        # (https://setuptools.readthedocs.io/en/latest/history.html#v20-6-8).  A
        # lot has been fixed around 36.2.0/1, so if we end up having issues we
        # might need to depend on this instead (Ref:
        # https://github.com/pypa/setuptools/pull/1089)
        'setuptools>=20.6.8',
        'backports.csv ; python_version<"3"'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['shutilwhich', 'pep8', 'pylint', 'pytest', 'pytest-cov', 'coverage', 'coveralls', 'future'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'pantable = pantable.pantable:main',
            'pantable2csv = pantable.pantable2csv:main'
        ],
    },
)
