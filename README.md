CAS Reader
==========

A git repository commit parser that inserts  each commit into a  PostgreSQL table.

##Installation
Clone this repository in to an empty directory 

###Dependencies
* Python  >= 3.3
* Pip for Python Version > 3.3
* Git > 1.7

###Pip Packages
Install the following packages by doing `pip install `  and then the package name

* SQL Alchemy (sqlalchemy)
* Py-PostgreSQL (py-postgresql)


##Quick Start
In a terminal, type `python readRepo.py "path/to/repo"` to parse the commits and store them in a database.

