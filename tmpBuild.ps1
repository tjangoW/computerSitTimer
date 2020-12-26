which python
which pip
pip install setuptools wheel
python .\setup.py sdist bdist_wheel
pip install twine
python -m twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ computerTimer-tjango
python -m computerTimer-tjango
