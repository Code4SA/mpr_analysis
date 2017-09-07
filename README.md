# MPR Analysis

Medicine Price Registry data cleaning and prep for analysis.

## Manifest

- data
  - mpr-YYYY-MM-DD.xls - the original xls from MPR, maybe with columns added or adjusted to align over the years?
  - all-consistent-date-cleaned.{csv,xlsx}
    - Company and Product names normalised
    - Date column in consistent format
- mpr_analysis - python modules building on SQLAlchemy ORM models to model and manage this data
- cleaning.json - OpenRefine cleaning steps on all-consistent-date-cleaned.csv??
- queries.sql - cool queries on the data in postgres

## Setup

### Create a Postgres database at localhost named mpr owned by role mpr. e.g.

```
# psql
psql (9.6.3)
Type "help" for help.

postgres=# create role mpr with login;
CREATE ROLE
postgres=# create database mpr with owner mpr;
CREATE DATABASE
```

### Create a python virtual environment for the project, activate it, and install dependencies. e.g.

```
virtualenv2 env
source env/bin/activate
pip install -r requirements.txt
```

Create DB schema by running migrations:
```
PYTHONPATH=. alembic upgrade head
```

### Load the data

Run trhough all the cells in clean.ipynb
Save the exported mpr-reliable-data.csv file in /data as mpr-reliable-data.xlsx

```
python mpr_analysis/importsep.py data/mpr-reliable-data.xlsx
```

This prints out some messages like "Could not process Pedea (a40/3.1/0174) due to lack of nappi code" and progress stats like
```
---------------------
products    22300 (8412)
prices      22300 (17300)
ingredients 39732 (2947)
{'schedule': u'S3', 'applicant_licence_no': u'242', 'is_generic': None, 'regno': u'41/7.1.3/0147', 'pack_size': 28, 'applicant_name': u'Novartis SA (Pty) Ltd', 'num_packs': 1, 'name': u'Co-Diovan', 'ingredients': [{'strength': '13', 'name': u'Valsartan', 'unit': u'mg'}, {'strength': '13', 'name': u'Hydrochlorothiazide', 'unit': u'mg'}], 'sep': 241.36, 'effective_date': datetime.datetime(2012, 4, 24, 0, 0), 'nappi_code': '710048001', 'dosage_form': u'Tab'}
---------------------
```
