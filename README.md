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
* R
* python-dev
* rpy2
* requests
* dateutil 

###Installing rpy2
* Assumes you are working on Ubuntu 12.04

Getting rpy2 to work can be a bit tricky. First, make sure you install R:
1. Get the repository SSL key and import it to apt by doing 
  `gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9`
  `gpg -a --export E084DAB9 | sudo apt-key add -`
2. Edit the list of sources 
  `gksudo gedit /etc/apt/sources.list`
   then add the following repo at the bottom:
  `deb http://cran.ma.imperial.ac.uk/bin/linux/ubuntu precise/`
3. Install R
  `sudo apt-get update`
  `sudo apt-get install r-base`

By default, typically we don't have the python-dev available for python3 on Ubuntu and so have to
install it as it's a dependency for rpy2. We do this by simply running `sudo apt-get install python3-dev`
  
Now we are ready to install rpy2. Make sure python version 3 or greater is in use, such as using
a virtualenv and run `pip install rpy2`

###Additional Pip Packages
Install the following packages by doing `pip install `  and then the package 
name. Make sure you are using python3, such as using a virtualenv if using Ubuntu.

* SQL Alchemy (sqlalchemy)
* Py-PostgreSQL (py-postgresql)
* requests
* python-dateutil

###First-Time Database Setup
Set up the database for the first time by running the scan.py included in the CAS_Reader
repo like normal (see *Usage* below), but with
`[option]` parameter set to `initDb`

##Usage
In a terminal, type `python analyze.py ' to start analyzing

