from setuptools import setup, find_packages

setup(
    name="django-elasticsearch",
    version="0.6",
    description="Simple wrapper around py-elasticsearch to index/search a django Model.",
    author="Robin Tissot / n.korolkov",
    url="https://github.com/liberation/django_elasticsearch || "
        "https://github.com/Nick1994209/django-elasticsearch",
    packages=find_packages(),
)
