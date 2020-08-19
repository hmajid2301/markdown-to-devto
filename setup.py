from setuptools import find_packages
from setuptools import setup

setup(
    name="markdown-to-devto",
    version="0.2.2-beta.1",
    description="A CLI tool for publish markdown articles to dev.to",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Haseeb Majid",
    author_email="me@haseebmajid.dev",
    keywords="cli, tool",
    license="Apache License",
    url="https://gitlab.com/hmajid2301/markdown-to-devto",
    python_requires="~=3.6",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=False,
    include_package_data=True,
    install_requires=["click>=7.0", "requests>=2.23.0", "python-frontmatter>=0.5.0"],
    entry_points={"console_scripts": ["markdown_to_devto = markdown_to_devto.cli:cli"]},
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
