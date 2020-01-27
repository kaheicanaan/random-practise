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

### test

To run with testing data, use the following scripts to initialize DB tables and insert test data
```bash
cd path/to/repo
psql -h [host] -U [username] -d [database] -f src/RDBMS/schema.sql
psql -h [host] -U [username] -d [database] -f src/RDBMS/tes_data.sql
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
Number of votes per second is very limited even for traffic spikes (e.g. less than 1000 votes per second).

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

### Implementation

* src/main_q3_web_backend.py
    1. provide url for voting
    1. send vote to SQS
    1. get voting result
* src/main_q3_subscriber.py
    1. get data from SQS
    1. insert them into DB
* src/simple_counter/message_queue.py
    1. helper class to interact with AWS SQS
* src/simple_counter/query_and_cache.py
    1. query voting results
    1. visualize voting results (not implemented)
    1. simulate caching layer locally

### Testing endpoint

Hosted at http://home.kahei.io:24601. 
Provide restful API http://home.kahei.io:24601/vote for voting and http://home.kahei.io:24601/voting_distribution for visualize voting results.
Since the service is hosted locally, please use the url http://home.kahei.io:24601/hello_world to check whether my computer is operating.

There is no UI for this platform, I simulate the voting process by visiting the following address

1. http://home.kahei.io:24601/vote_to_1
    * vote to 薯片
1. http://home.kahei.io:24601/vote_to_2
    * vote to 林林
1. http://home.kahei.io:24601/vote_to_3
    * vote to 正氣

### Set up sample code

Building the total solution would be quite time consuming.
Here I provide a simplified version to demonstrate the software architecture.

Assuming the conda environment and PostgreSQL (if not, please follow the steps in [here](https://www.postgresql.org/download/linux/ubuntu/)) are ready.

#### db table init

Build DB table according to schema provided in this repo.
```bash
cd path/to/repo
psql -h [host] -p [port] -U [username] -d [db_name] -f src/simple_counter/db_schema.sql
``` 

#### run web backend

First assign environment variables. Restful API will be hosted in localhost at port *APP_PORT*. 
SQS_URL locate the AWS SQS service for message queue layer.
```bash
export APP_PORT=24601
export APP_DEBUG_MODE=false
export SQS_URL=https://your-sqs-url
```

AWS credentials is required for uploading vote info to AWS SQS message queue. Enter the required account info.
```bash
aws configure
```

Also include the Postgres connection information for query voting result.
Postgres info is needed here because module for getting cache and module for querying voting result are closely coupled for simplicity.
```bash
export PG_HOST=ip_address
export PG_PORT=5432
export PG_DB=db_name
export PG_USERNAME=my_name
export PG_PASSWORD=xxxxxx
```

Then run the script to start the web backend. Kiosk id should be unique across all kiosks.
```bash
cd path/to/repo
python src/main_q3_web_backend.py --kiosk-id 42
```

#### run subscriber

Similarly, set up environment variables - SQS_URL, PG_INFO, aws credential for connecting AWS SQS and PostgreSQL.
Run subscriber script for regular batch insert into DB.

```bash
cd path/to/repo
python src/main_q3_subscriber.py
```
