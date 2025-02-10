from setuptools import setup, find_packages

setup(
    name="MemoryInvestigator",
    version="1.0.0",
    author="Jan-Hendrik Lang",
    author_email="j.lang@hm.edu",
    description="A Streamlit-based application for automated memory forensic analysis using Volatility3 and LLMs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jan-hendrik-lang/MemoryInvestigator",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "protobuf",
        "pandas",
        "openai",
        "langchain-google-genai",
        "langchain",
        "langchain-core",
        "langchain-chroma",
        "langchain-community",
        "langchain-openai",
        "requests",
        "keyboard",
        "psutil",
        "setuptools",
        "streamlit_agraph"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "MemoryInvestigator=main:main",
        ],
    },
)
