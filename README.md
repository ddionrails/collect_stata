# collect_stata

The tool reads dta-files, calculates some univariate statistics for each variable 
and writes out a json-file with these calculations and the metadata (extracted from stata).

The purpose of the project is the preprocessing of data for [ddionrails](https://github.com/ddionrails/ddionrails).

## Install from source

```
pip install git+git://github.com/ddionrails/collect_stata.git@v0.1.0
```

## Setup for development

* Install dev tools
  + `pipenv install --dev` 
  + `pipenv run pre-commit install` 

## Usage

```shell
collect_stata -i [input_path] -o [output_path] -s [study_name]
```

Example:
```shell
collect_stata -i ~/teststudy/ -o ~/test/ -s teststudy
```

optional arguments:

--help,    -h : Show help information
--multiprocessing, -m
                      Process stata files in parallel
--latin1, -l          Set this if your source stata files are encoded with Latin-1 or Windows-1252
--debug, -d           Set logging Level to DEBUG
--verbose, -v         Set logging Level to INFO

## License
[BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause)
