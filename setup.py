import setuptools
setuptools.setup(
    name="autom8",
    version="0.0.1",
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
        'certifi==2021.5.30',
        'charset-normalizer==2.0.4',
        'ci-info==0.2.0',
        'click==8.0.1',
        'colorama==0.4.4',
        'configobj==5.0.6',
        'configparser==5.0.2',
        'etelemetry==0.2.2',
        'filelock==3.0.12',
        'fitz==0.0.1.dev2',
        'future==0.18.2',
        'httplib2==0.19.1',
        'idna==3.2',
        'isodate==0.6.0',
        'lxml==4.6.3',
        'networkx==2.6.2',
        'nibabel==3.2.1',
        'nipype==1.6.1',
        'numpy==1.21.2',
        'packaging==21.0',
        'pandas==1.3.2',
        'pathlib==1.0.1',
        'Pillow==8.3.1',
        'prompt-toolkit==1.0.14',
        'prov==2.0.0',
        'pydot==1.4.2',
        'Pygments==2.10.0',
        'PyInquirer==1.0.3',
        'PyMuPDF==1.18.16',
        'pyparsing==2.4.7',
        'python-dateutil==2.8.2',
        'pytz==2021.1',
        'pyxnat==1.4',
        'rdflib==6.0.0',
        'regex==2021.8.3',
        'requests==2.26.0',
        'scipy==1.7.1',
        'simplejson==3.17.4',
        'six==1.16.0',
        'traits==6.2.0',
        'urllib3==1.26.6',
        'wcwidth==0.2.5'
    ]
)