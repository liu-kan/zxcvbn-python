from setuptools import setup, find_packages
from setuptools.command.build import build as _build
from babel.messages.frontend import compile_catalog

class build(_build):
    def run(self):
        self.run_command('compile_catalog')
        super().run()

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='zxcvbn',
    version='4.5.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'zxcvbn': ['locale/*/LC_MESSAGES/*.mo'],
    },
    url='https://github.com/dwolfhub/zxcvbn-python',
    download_url='https://github.com/dwolfhub/zxcvbn-python/tarball/v4.5.0',
    license='MIT',
    author='Daniel Wolf',
    author_email='danielrwolf5@gmail.com',
    long_description=long_description,
    keywords=['zxcvbn', 'password', 'security'],
    entry_points={
        'console_scripts': [
            'zxcvbn = zxcvbn.__main__:cli'
         ]
    },
    project_urls = {
      'Changelog': 'https://github.com/dwolfhub/zxcvbn-python/blob/master/CHANGELOG.md'
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={
        'build': build,
        'compile_catalog': compile_catalog,
    },
)
