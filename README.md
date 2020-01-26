# random-practise

## Access Log analytics

### init conda environment

Prepare a virtual environment for this repo. Please follow the installation steps if you don't have 
[Miniconda](https://docs.conda.io/en/latest/miniconda.html#) installed.

```bash
conda create -n random python=3
```

Activate the environment and install required packages / libraries.

```bash
conda activate random
cd path/to/repo
pip install -r requirements.txt
```

### run

No extra configuration is required, just run the script.

```bash
python src/main_q1.py --early-stopping 50
```

The args "early-stopping" is needed to control the number of conversion of top frequent visit hosts to its IP address.
It is necessary because host-to-country mapping is slow.
Note that by considering top 50 hosts. We covered ~12% of total records.

## RDBMS

Prepare PostgreSQL command line tool for running the following script.

```bash
sudo apt-get install postgresql
```

### run

It is a simple SQL query, we can submit the script directly.

```bash
cd path/to/repo
psql -h [host] -U [username] -d [database] -f src/main_q2.sql
```
