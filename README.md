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

## Simple counter

### Requirement analysis

#### Inbound traffic load are limited

There are tens/hundreds of kiosks. 
Number of votes per second is very limited even for traffic spikes (e.g. less than 1000 votes).

#### Outbound traffic load can be high

Voting result involves

1. total and 
1. 10-minutes vote distribution.

Large amount of data result may in poor query and process performance.

### Implementation

Graphical workflow is shown as:

![Workflow](https://github.com/kaheicanaan/random-practise/blob/master/src/simple_counter/mermaid-diagram-20200126214848.svg)

#### Kiosks to DB

We cannot insert every single vote to RDS from kiosks directly because the I/O overhead is large.
DB instance would be busy handling I/O rather than actual insert/select.
Therefore, Pub-Sub pattern should be used to isolate kiosks and DB via a message queue (e.g. kafka).
Votes are published to kafka from kiosks and let backend handle the rest.
This ensure that there is no bottleneck at submitting votes because kafka serves as a powerful buffer. 

Behind the message queue, a subscriber aggregate votes in message queue and preform batch insert to DB. 
Batch insertion of records greatly reduce I/O overhead. 
We can further monitor the CPU usage of subscriber(s) and allow auto-scaling of subscriber instance by setting certain thresholds.

#### Query from DB

Data required for visualizing voting distribution is huge (nearly all the records is needed).
To resolve performance issues, proper indexing is required to prevent scanning data that are located at disk.
i.e. candidateId must be a part of composite key.

Besides, direct query by hundreds of kiosks is also avoidable.
It is because for a particular timestamp, all data required by kiosks are the same.
It is meaningless for DB to query the same dataset multiple times.
If we further accept a small error in voting distribution, we can even use the result queried in the near past 
(e.g. 1 minute) to trade the overall workload required.

Caching layer (e.g. redis) is used to isolate data from DB to kiosks.
A scheduled job (e.g. cloudWatch + lambda) is responsible for query, aggregate and plotting voting results. 
All materials are then uploaded to the caching layer. Finally kiosks downloads data from cache.  
