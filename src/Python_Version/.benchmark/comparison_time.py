import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def add_aggregate_function(df, new_name, functions, keep=False):
    # Rows to aggregate
    mask = df["function"].isin(functions)

    agg = (
        df[mask]
        .groupby(
            [
                "entity",
                "entity_id",
                "PATH_LENGTH",
                "THRESHOLD",
                "NBR_MIXNODES",
                "NBR_STTPS",
                "NBR_CLIENTS",
            ],
            as_index=False,
        )
        .agg(
            time=("time", "sum"),
        )
    )

    agg["function"] = new_name
    
    # Remove original rows
    if not keep:
        df = df[~mask]
        
    return pd.concat([df, agg], ignore_index=True)
    

ORIGINAL_RESULTS = ".benchmark/data/original_sphinx_time.csv"
OUR_RESULTS = ".benchmark/data/timing.csv"

df = pd.read_csv(OUR_RESULTS)

# Clean & Filter - Implementation results
df['function'] = df['function'].str.strip()
df['entity'] = df['entity'].str.strip()
df['time'] = df['CPU_time_ms']
df = df[['entity', 'entity_id', 'function', 'time', 'PATH_LENGTH', 'THRESHOLD', 'NBR_MIXNODES', 'NBR_STTPS', 'NBR_CLIENTS']]

# Merge Client function time
df = add_aggregate_function(df,"route sampling", ['query_route', 'aggregate_shares', 'shared_secret_rerandomization'])
df = add_aggregate_function(df,"client", ["build", "route sampling"], keep=True)

df = df[df['PATH_LENGTH'] >= 3]
df = df[df['PATH_LENGTH'] <= 7]
df = df[df['THRESHOLD'] <= 20]

df = df[df['function']=='client']

# Path Length
x, hue = "PATH_LENGTH", 'THRESHOLD'
sns.lineplot(data=df, x=x, y="time", hue=hue)
plt.xticks(list(set(df[x])))
plt.ylabel("time (ms)")
plt.savefig(".benchmark/results/path_length.png")

plt.clf()

# Threshold
x, hue = 'THRESHOLD', "PATH_LENGTH"
sns.lineplot(data=df, x=x, y="time", hue=hue)
plt.xticks(list(set(df[x])))
plt.ylabel("time (ms)")
plt.savefig(".benchmark/results/threshold.png")