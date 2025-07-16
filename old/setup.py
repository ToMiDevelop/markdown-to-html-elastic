from setuptools import setup, find_packages

setup(
    name="markdown-to-html-converter",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "markdown>=3.3",
        "python-frontmatter>=1.0.0",
        "pymdown-extensions>=9.0",
        "Pygments>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "md2html=md2html.converter:main",
        ],
    },
    python_requires=">=3.11",
) 