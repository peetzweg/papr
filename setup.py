try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import sys

# disables creation of .DS_Store files inside tarballs on Mac OS X
os.environ['COPY_EXTENDED_ATTRIBUTES_DISABLE'] = 'true'
os.environ['COPYFILE_DISABLE'] = 'true'

from pip.req import parse_requirements

import papr

def extract_package_name(requirement):
    return str(requirement.req).replace('-', '_').split('==')[0]

def find_requirements(req_file='requirements.txt'):
    return [extract_package_name(r) for r in parse_requirements(req_file)]

DESCRIPTION = 'papr creates a PDF calendar you can print out, fold and use.'

setup(
    author=papr.__author__,
    author_email=papr.__author_email__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Afrikaans',
        'Natural Language :: Arabic',
        'Natural Language :: Bengali',
        'Natural Language :: Bosnian',
        'Natural Language :: Bulgarian',
        'Natural Language :: Catalan',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: Croatian',
        'Natural Language :: Czech',
        'Natural Language :: Danish',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Natural Language :: Esperanto',
        'Natural Language :: Finnish',
        'Natural Language :: French',
        'Natural Language :: Galician',
        'Natural Language :: German',
        'Natural Language :: Greek',
        'Natural Language :: Hebrew',
        'Natural Language :: Hindi',
        'Natural Language :: Hungarian',
        'Natural Language :: Icelandic',
        'Natural Language :: Indonesian',
        'Natural Language :: Italian',
        'Natural Language :: Japanese',
        'Natural Language :: Javanese',
        'Natural Language :: Korean',
        'Natural Language :: Latin',
        'Natural Language :: Latvian',
        'Natural Language :: Macedonian',
        'Natural Language :: Malay',
        'Natural Language :: Marathi',
        'Natural Language :: Norwegian',
        'Natural Language :: Panjabi',
        'Natural Language :: Persian',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Romanian',
        'Natural Language :: Russian',
        'Natural Language :: Serbian',
        'Natural Language :: Slovak',
        'Natural Language :: Slovenian',
        'Natural Language :: Spanish',
        'Natural Language :: Swedish',
        'Natural Language :: Tamil',
        'Natural Language :: Telugu',
        'Natural Language :: Thai',
        'Natural Language :: Turkish',
        'Natural Language :: Ukranian',
        'Natural Language :: Urdu',
        'Natural Language :: Vietnamese',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
    ],
    data_files=[],
    description=DESCRIPTION,
    ext_modules=[],
    install_requires=find_requirements('requirements.txt'),
    license=papr.__license__,
    long_description=DESCRIPTION,
    name='papr',
    packages=find_packages(),
    package_data={},
    setup_requires=find_requirements('requirements.txt'),
    url=papr.__url__,
    use_2to3=(sys.version_info >= (3,)),
    version=papr.__version__,
    entry_points={'console_scripts' : [
        'papr = papr.app:main']},
)

