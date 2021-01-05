pip install twine

## old stuff for testpypi
#python -m twine upload --repository testpypi dist/*
#pip install -i https://test.pypi.org/simple/ computerSitTimer

python -m twine upload dist/*
pip uninstall computerSitTimer
pip install computerSitTimer
computerSitTimer
