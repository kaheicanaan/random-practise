import pandas as pd
import gzip
from utils.helper_func import parser_log, map_host_to_country
import collections
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--early-stopping', default=50, type=int)
args = parser.parse_args()


# log parsing
inputs = list()
with gzip.open('src/access_log_analytics/NASA_access_log_Aug95.gz', 'r') as f:
    content = f.readlines()
    inputs = [parser_log(line) for line in content]

df = pd.DataFrame(inputs, columns=['ip', 'datetime', 'request', 'response', 'bytes'])

# ======================================
# total number of HTTP requests recorded
# ======================================
total_number = df.shape[0]

# ===================
# top-10 (host) hosts
# ===================
# print(df['datetime'].map(lambda s: s.endswith(' -0400')).all())
# Since all timestamp share the same timezone,
# here I assume "18th Aug to 20th Aug" means "1995-08-18T00:00:00 -04:00 to 1995-08-21T00:00:00 -04:00"
df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%b/%Y:%X %z')
in_range_mask = (df['datetime'] >= pd.to_datetime('1995-08-18 00:00:01-04:00')) & \
                (df['datetime'] < pd.to_datetime('1995-08-21 00:00:01-04:00'))
host_counts = df[in_range_mask]['ip'].value_counts()
top_hosts = None
if host_counts.shape[0] >= 10:
    top_hosts = host_counts[:10].index.tolist()
else:
    # in case there are less than 10 hosts
    top_hosts = host_counts.index.tolist()

# ===========================================
# country with most requests originating from
# ===========================================
# this host-country mapping step is slow, set early stopping if needed
early_stopping = args.early_stopping  # n: cover top n hosts
processed = 0
country_counts = collections.defaultdict(int)

# use aggregated result, prevent querying the same record many times
for host, count in host_counts.items():
    country = map_host_to_country(host)
    country_counts[country] += count
    # count number of requests
    processed += 1
    if processed > early_stopping:
        break
series = pd.Series(country_counts)

# try to eliminate 'XX' (which is the result of not-detectable-country's host)
top_country = None
if series.shape[0] > 1:
    series = series.drop('XX', errors='ignore')
top_country = series.index[0]

# ============
# print result
# ============
print('total number of HTTP requests recorded:', total_number)
print('top-10 (host) hosts makes most requests from 18th Aug to 20th Aug:', top_hosts)
print('country with most requests originating from (XX means no detected country due to early stopping):', top_country)
