import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dropboxignore',
    version='0.1',
    scripts=['dropboxignore'],
    author="Michał Karol",
    author_email="michal.p.karol@gmail.com",
    description="Tool allowing for watching sync directory and setting Dropbox to ignore paths using .dropboxignore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichalKarol/dropboxignore",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
