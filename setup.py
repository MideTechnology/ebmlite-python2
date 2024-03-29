import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='ebmlite',
        version='1.1.0',
        author='Mide Technology',
        author_email='help@mide.com',
        description='A lightweight, "pure Python" library for parsing EBML (Extensible Binary Markup Language) data.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/MideTechnology/ebmlite',
        license='MIT',
        classifiers=['Development Status :: 5 - Production/Stable',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Programming Language :: Python :: 2.7'],
        keywords='ebml binary matroska webm',
        python_requires='~=2.7',
        packages=setuptools.find_packages(),
        package_dir={'': '.'},
        package_data={
            '': ['schemata/*', 'tests/*.ide', 'tests/*.mkv']
        },
        test_suite='tests',
)
