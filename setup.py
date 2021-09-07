import setuptools
setuptools.setup(
    name="autom8",
    version="0.1",
    author="Daniel Konopka",
    author_email="daniel@konopka.me",
    description="Package to autom8 mundane work",
    license='MIT',
    download_url="https://github.com/ipseityperse/autom8",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities"
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",

    ],
    install_requires = [
        'Pillow==8.3.1',
        'PyInquirer==1.0.3',
        'PyMuPDF==1.18.16',
        'regex==2021.8.3',
        'requests==2.26.0',
    ]
)