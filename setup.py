"""
To test locally, run python setup.py install
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="computerSitTimer",
    version="0.1.3",
    author="tjango",
    description="A simple timer in tray to prevent sitting too long.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tjangoW/computerSitTimer",
    install_requires=[
        "pySimpleGUIQt"
    ],
    project_urls={
    },
    packages=setuptools.find_packages(exclude=["tmp*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Desktop Environment",
    ],
    entry_points={
        "gui_scripts": [
            "computerSitTimer = computerSitTimer.__main__:main"
        ]
    },
    python_requires='~=3.5',  # typing since 3.5, enum since 3.4,
    package_data={
        # https://pythonhosted.org/setuptools/setuptools.html#including-data-files
        # If any package contains *.png files, include them:
        '': ['media/*.png'],
    },
)
