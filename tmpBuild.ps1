#which python
#which pip
#pip install setuptools wheel
#pip install twine

rm -Recurse -Force build
rm -Recurse -Force dist
rm -Recurse -Force *.egg-info
python .\setup.py sdist bdist_wheel
#python -m twine upload --repository testpypi dist/*

#pip install -i https://test.pypi.org/simple/ computerTimer-tjango
#python -m computerTimer-tjango
