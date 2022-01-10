import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="monobank_handler",
    version="0.1.7",
    author="bezumnui",
    author_email="bezumnui.mistikgt@gmail.com",
    description="Monobank.ua API implementation with handlers(poll/webhook)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bezumnui/monobank_handler",
    project_urls={
        "Bug Tracker": "https://github.com/bezumnui/monobank_handler/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)