from setuptools import find_packages, setup

setup(
    name="rest_pollen",
    version=0.1,
    description="Description here",
    license="Apache 2.0",
    packages=find_packages(),
    package_data={},
    scripts=[],
    install_requires=[
        "boto3",
        "click",
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "python-jose[cryptography]",
        "pytest",
        "pytest-cov",
        "supabase",
        "replicate",
        "websocket-client",
    ],
    extras_require={
        "test": [
            "pylint!=2.5.0",
            "black",
            "mypy",
            "flake8",
            "requests",
        ],
    },
    entry_points={
        "console_scripts": [],
    },
    classifiers=[],
    tests_require=["pytest"],
    setup_requires=["pytest-runner"],
    keywords="",
)
