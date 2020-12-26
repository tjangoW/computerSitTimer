import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="computerSitTimer",
    version="0.1.0",
    author="tjango",
    description="A simple timer in tray to prevent sitting too long.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tjangoW/computerSitTimer",
    install_requires=[
        "pySimpleGUIQt",
        "simpleaudio"
    ],
    project_urls={
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        "gui_scripts": [
            "computerSitTimer = computerSitTimer.__main__:main"
        ]
    },
    python_requires='>=3.8',
)
