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

client_df = df[df['function']=='client']

# Path Length
x, hue = "PATH_LENGTH", 'THRESHOLD'
sns.lineplot(data=client_df, x=x, y="time", hue=hue)
plt.xticks(list(set(client_df[x])))
plt.ylabel("time (ms)")
plt.savefig(".benchmark/results/path_length.png")

plt.clf()

# Threshold
x, hue = 'THRESHOLD', "PATH_LENGTH"
sns.lineplot(data=client_df, x=x, y="time", hue=hue)
plt.xticks(list(set(client_df[x])))
plt.ylabel("time (ms)")
plt.savefig(".benchmark/results/threshold.png")

client_df = client_df[['time', 'PATH_LENGTH', 'THRESHOLD']]

client_df=client_df.groupby(['PATH_LENGTH', 'THRESHOLD']).mean().reset_index()
client_df = client_df.pivot(
    index="PATH_LENGTH",
    columns="THRESHOLD",
    values="time"
)
# latex = client_df.to_latex(
#     index=True,
#     float_format="%.3f"
# )

# print(latex)


## PROPORTION ##
################

df = df[['entity','function','time','PATH_LENGTH','THRESHOLD']]
client = df[df['entity']=='CLIENT']
sttp = df[df['entity']=='STTP']
mix = df[df['entity']=='MIX']
mix = mix[mix['function'].isin(['setup', 'process_header'])]

### client
print("\n Client")
build_means = client[client['function']=='build'].groupby(['entity','function','THRESHOLD', 'PATH_LENGTH'])['time'].mean()
route_means = client[client['function']=='route sampling'].groupby(['entity','function','THRESHOLD', 'PATH_LENGTH'])['time'].mean()
print(f"Build time: {build_means.min()} - {build_means.max()}")
print(f"Route time: {route_means.min()} - {route_means.max()}")
#sttp.groupby(['entity','function','PATH_LENGTH','THRESHOLD']).mean()

grouped = client.groupby(['entity','function','PATH_LENGTH', 'THRESHOLD']).mean()
df_pivot = grouped.reset_index().pivot_table(
    index=['entity','PATH_LENGTH','THRESHOLD'],
    columns='function',
    values='time'
)
df_pivot['route sampling %'] = df_pivot['route sampling'] / df_pivot['client'] * 100
df_pivot['build %'] = df_pivot['build'] / df_pivot['client'] * 100

tot_build = sum(client[client['function']=="build"]['time'])
tot_route = sum(client[client['function']=="route sampling"]['time'])
print(f"Packet construction: {round(100 * tot_build / (tot_build + tot_route))} % of client time")
print(f"Route sampling: {round(100 * tot_route / (tot_build + tot_route))} % of client time")



### Nodes
print("\n Nodes")
setup_means = mix[mix['function']=='setup'].groupby(['entity','function','THRESHOLD', 'PATH_LENGTH'])['time'].mean()
process_means = mix[mix['function']=='process_header'].groupby(['entity','function','THRESHOLD', 'PATH_LENGTH'])['time'].mean()
print(f"Setup time: {setup_means.min()} - {setup_means.max()}")
print(f"Header processing: {process_means.min()} - {process_means.max()}")
#mix.groupby(['entity','function','PATH_LENGTH','THRESHOLD']).mean()


### STTP
print("\n STTP")
setup_means = sttp[sttp['function']=='send_share'].groupby(['entity','function','THRESHOLD', 'PATH_LENGTH'])['time'].mean()
route_means = sttp[sttp['function']=='store_share'].groupby(['entity','function','THRESHOLD', 'PATH_LENGTH'])['time'].mean()
print(f"STTP Setup time: {setup_means.min()} - {setup_means.max()}")
print(f"STTP Route time: {route_means.min()} - {route_means.max()}")
#sttp.groupby(['entity','function','PATH_LENGTH','THRESHOLD']).mean()
