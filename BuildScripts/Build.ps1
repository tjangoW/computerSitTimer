#which python
#which pip
pip install setuptools wheel

rm -Recurse -Force build
rm -Recurse -Force dist
rm -Recurse -Force *.egg-info
python .\setup.py sdist bdist_wheel
pip uninstall computerSitTimer
twine check .\dist\*
echo "pip install .\dist\computerSitTimer-*.whl"
