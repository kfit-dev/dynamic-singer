import setuptools


__packagename__ = 'dynamic-singer'

setuptools.setup(
    name = __packagename__,
    packages = setuptools.find_packages(),
    version = '0.0.1',
    python_requires = '>=3.7.*',
    description = 'Python API, Dynamic source, N targets, Prometheus exporter for Singer ETL',
    author = 'huseinzol05',
    author_email = 'husein.zol05@gmail.com',
    url = 'https://github.com/huseinzol05/dynamic-singer',
    install_requires = ['genson', 'singer-python', 'jsonschema'],
    license = 'MIT',
    classifiers = [
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
