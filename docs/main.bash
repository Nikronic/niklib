# you can use following refs for help:
#  https://github.com/finsberg/sphinx-tutorial

# use following the start the template
sphinx-quickstart

# build api docs
sphinx-apidoc -o source/ ../niklib/

# WARNING: the default `docs/source/conf.py`` is not good enough
#  use the file `docs/conf.py` to fill more details

# make files
make html
