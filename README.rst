
collect_stata
=============

The tool reads dta-files, calculates some univariate statistics for each variable 
and writes out a json-file with these calculations and the metadata (extracted from stata).

The purpose of the project is the preprocessing of data for `ddionrails <https://github.com/ddionrails/ddionrails>`_.

Setup for development
---------------------


* Install dev tools

  * ``pipenv install --dev`` 
  * ``pipenv run pre-commit install`` 

Usage
-----

.. code-block:: shell

   pipenv shell

   (collect_stata) collect_stata -i [input_path] -o [output_path] -s [study_name]

Example:

.. code-block:: shell

   collect_stata -i ~/teststudy/ -o ~/test/ -s teststudy

optional arguments:

--help,    -h : Show help information

--debug,   -d : Set logging Level to DEBUG

--verbose, -v : Set logging Level to INFO

License
-------

`BSD-3-Clause <https://opensource.org/licenses/BSD-3-Clause>`_
