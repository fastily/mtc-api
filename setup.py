import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mtc-api",
    version="0.0.1",
    author="Fastily",
    author_email="fastily@users.noreply.github.com",
    description="API for generating descriptions pages when transferring files to Commons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastily/mtc-api",
    project_urls={
        "Bug Tracker": "https://github.com/fastily/mtc-api/issues",
    },
    include_package_data=True,
    packages=setuptools.find_packages(include=["mtc_api"]),
    install_requires=['fastilybot', 'fastapi[all]', 'gunicorn'],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
