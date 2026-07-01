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
    

# ORIGINAL_RESULTS = ".benchmark/data/original_sphinx_time.csv"
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

#############
## boxplot ##
#############

def avg_store_share(sttp):
    store = sttp[sttp['function'] == 'store_share']
    store = store.sort_index().reset_index(drop=True)
    # regroup by 100 (because receive 100 shares and after sort them)
    store['entity_id'] = store.index // 100
    store = store.groupby(['entity','entity_id','function','PATH_LENGTH','THRESHOLD']).sum().reset_index()

    store['entity']='STTP'
    store['function']='setup'
    
    return pd.concat([store, sttp[sttp['function'] == 'send_share']], ignore_index=True)


df = df[['entity','entity_id','function','time','PATH_LENGTH','THRESHOLD']]

client = df[df['entity']=='CLIENT']
sttp   = df[df['entity']=='STTP']
mix    = df[df['entity']=='MIX']

client = client[client['function'].isin(['route sampling', 'build'])]
sttp   = sttp[sttp['function'].isin(['store_share', 'send_share'])]
mix    = mix[mix['function'].isin(['setup', 'process_header'])]

sttp = avg_store_share(sttp)

client['role'] = 'Client'
mix['role'] = 'Node'
sttp['role'] = 'STTP'


plot_df = pd.concat([
    client[['role','function','time','PATH_LENGTH','THRESHOLD']],
    mix[['role','function','time','PATH_LENGTH','THRESHOLD']],
    sttp[['role','function','time','PATH_LENGTH','THRESHOLD']]
], ignore_index=True)

plot_df.replace({'function': {'route sampling': 'Route', 'build': 'Packet', 'setup': 'Setup', 'process_header': 'Process', 'send_share': 'Route'}}, inplace=True)

sns.set_theme(style="whitegrid", context="paper", font_scale=1.8)

g = sns.catplot(
    data=plot_df,
    kind="box",
    col="role",        
    x="function",
    y="time",
    sharex=False,
    sharey=True,        # IMPORTANT for log comparison
    height=4,
    aspect=1,
    showfliers=False
)

g.set_axis_labels("", "Execution time (ms)")
g.set_titles("{col_name}")

# Apply log scale + styling per subplot
for ax in g.axes.flat:
    ax.set_yscale("log")
    ax.tick_params(axis='x', rotation=0)  # horizontal labels
    ax.set_xlabel("")  # remove repeated "function" label

plt.tight_layout()
plt.savefig(".benchmark/results/boxplot.png")
plt.clf()

##############
## lineplot ##
##############

client = df[df['entity']=='CLIENT']
client_time = client[client['function']=='client']
sns.set_theme(style="whitegrid", context="paper", font_scale=1.8)

# Path Length
x, hue = "PATH_LENGTH", 'THRESHOLD'
sns.lineplot(data=client_time, x=x, y="time", hue=hue, marker="o", linewidth=2)
plt.xticks(range(3,8))
plt.xlabel("Route length $m$ (hops)")
plt.ylabel("Client execution time (ms)")
plt.legend(title="Threshold $d$")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(".benchmark/results/path_length.png")
plt.clf()

# Threshold
x, hue = 'THRESHOLD', "PATH_LENGTH"
sns.lineplot(data=client_time, x=x, y="time", hue=hue, marker="o", linewidth=2)
plt.xticks([3, 5, 10, 15, 20])
plt.xlabel("Reconstruction threshold $d$")
plt.ylabel("Client execution time (ms)")
plt.legend(title="Route length $m$")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(".benchmark/results/threshold.png")
plt.clf()