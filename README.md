# random-practise

## init conda environment

Prepare a virtual environment for this repo. Please follow the installation steps if you don't have 
[Miniconda](https://docs.conda.io/en/latest/miniconda.html#) installed.

```bash
conda create -n random python=3
```

Activate the environment and install required packages / libraries.

```bash
conda activate random
cd /path/to/repo
pip install -r requirements.txt
```

## Access Log analytics

No extra configuration is required, just run the script.

```bash
python src/main_q1.py --early-stopping 50
```

The args "early-stopping" is needed to control the number of conversion of top frequent visit hosts to its IP address.
It is necessary because host-to-country mapping is slow.
Note that by considering top 50 hosts. We covered ~12% of total records.
