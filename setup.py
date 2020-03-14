from pathlib import Path
from setuptools import setup, find_packages

SRC_DIR = Path('src/gitstery')
DATA_DIR = SRC_DIR / 'data'
DATA_FILES = [
    p.relative_to(SRC_DIR).as_posix()
    for p in DATA_DIR.glob('**/*')
    if p.is_file()]

CONSOLE_SCRIPTS = {
    'gitstery': 'gitstery.cli:cli',
}

setup(
    name='gitstery-generator',
    version='1.0.1',
    description='A Git murder mystery',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Niv Ben-David',
    author_email='nivbend@gmail.com',
    url='https://github.com/nivbend/gitstery-generator',
    license='GPLv3',
    packages=find_packages('src'),
    package_dir={ '': 'src', },
    include_package_data=True,
    package_data={
        'gitstery': DATA_FILES,
    },
    install_requires=Path('requirements.txt').read_text().splitlines(),
    entry_points={
        'console_scripts': [f'{name}={path}' for (name, path) in CONSOLE_SCRIPTS.items()],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Terminals',
    ],
    keywords=' '.join([
        'git', 'mystery', 'learn', 'learning',
    ]))
