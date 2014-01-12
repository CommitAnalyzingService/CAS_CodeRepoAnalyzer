CAS Reader
==========

A git repository commit parser that inserts  each commit into a  PostgreSQL 
table.

##Installation
1. Clone this repository in to an empty directory
2. Copy the `./config.example.json` to `./config.json` and change the 
appropriate credentials and settings to match the environment.

###Dependencies
* Python  >= 3.3
* Pip for Python Version > 3.3
* Git > 1.7

###Pip Packages
Install the following packages by doing `pip install `  and then the package 
name

* SQL Alchemy (sqlalchemy)
* Py-PostgreSQL (py-postgresql)

###First-Time Database Setup
Set up the database for the first time by running the script like normal 
(see *Usage* below), but with
`[option]` parameter set to `initDb`

##Usage
In a terminal, type `python scan.py [option]` to scan the repository table for 
repositories that need to be downloaded and then store the commits in the
database

On Windows, `casr` can be used in the project directory instead of 
`python scan.py`
###Options
`initDb` - Create all the tables

`testRepos` - Makes dummy repository data entries to test the script.
