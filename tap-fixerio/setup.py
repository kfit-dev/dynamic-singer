from setuptools import setup, find_packages

setup(
    name = 'tap-fixerio',
    version = '0.1.1',
    description = 'Singer.io tap for extracting currency exchange rate data from the fixer.io API',
    author = 'Stitch',
    url = 'http://singer.io',
    classifiers = ['Programming Language :: Python :: 3 :: Only'],
    py_modules = ['tap_fixerio'],
    install_requires = [
        'singer-python>=0.1.0',
        'backoff>=1.3.2',
        'requests>=2.13.0',
    ],
    entry_points = """
          [console_scripts]
          tap-fixerio=tap_fixerio:main
      """,
)
