CAS Analyzer
==========

Analyzes repositories and generate median values of the buggy versus non buggy metrics

##Installation
1. Clone this repository in to an empty directory
2. Copy the `./config.example.json` to `./config.json` and change the 
appropriate credentials and settings to match the environment.

###Dependencies
* Python  >= 3.3
* Pip for Python Version > 3.3
* Git > 1.7
* rpy2
* R

###Pip Packages
Install the following packages by doing `pip install `  and then the package 
name

* SQL Alchemy (sqlalchemy)
* Py-PostgreSQL (py-postgresql)
* rpy2

###First-Time Database Setup
Set up the database for the first time by running the scan.py included in the CAS_Reader
repo like normal (see *Usage* below), but with
`[option]` parameter set to `initDb`

##Usage
In a terminal, type `python analyze.py ' to start analyzing

