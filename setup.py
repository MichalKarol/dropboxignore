import setuptools
import os.path as p


with open('README.md', 'r') as fh:
    long_description = fh.read()

the_lib_directory = p.dirname(p.realpath(__file__))
requirement_path = p.join(the_lib_directory, 'requirements.txt')
install_requires = []
if p.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()


setuptools.setup(
    name='dropboxignore',
    version='0.2.0',
    scripts=['dropboxignore.py'],
    author='Michał Karol',
    author_email='michal.p.karol@gmail.com',
    description='Tool allowing for watching sync directory and setting Dropbox to ignore paths using .dropboxignore',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MichalKarol/dropboxignore',
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'dropboxignore = dropboxignore:main',
        ],
    }
)
