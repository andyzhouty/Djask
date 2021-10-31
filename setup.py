from setuptools import setup

setup(
    name="Djask",
    install_requires=[
        "flask >= 2.0.0",
        "apiflask >= 0.10.0",
        "flask-sqlalchemy >= 2.5.0",
        "flask-wtf >= 0.15.0",
        "wtforms-sqlalchemy >= 0.2.0",
    ],
    extras_require={
        "async": ["asgiref >= 3.2"],
    },
)
