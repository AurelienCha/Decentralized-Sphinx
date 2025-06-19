NIST_TEST_NAME = {
    'Frequency':'     Frequency', 
    'BlockFrequency':'    Block Frequency', 
    'CumulativeSums': '    Cumulative Sums', 
    'Runs': '    Runs', 
    'LongestRun': '   Longest Run',      
    'Rank': '   Rank', 
    'FFT': '  Discrete Fourier Transform', 
    'NonOverlappingTemplate': '  Nonperiodic Template Matchings', 
    'OverlappingTemplate': '  Overlapping Template Matchings', 
    'Universal': '  Universal Statistical', 
    'ApproximateEntropy': ' Approximate Entropy', 
    'RandomExcursions': ' Random Excursions',
    'RandomExcursionsVariant': ' Random Excursions Variant', 
    'Serial': ' Serial', 
    'LinearComplexity': 'Linear Complexity'
}

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os 

def extract_data(file):

    def extract_results(lines):
        results = [[l for l in line.split() if l!='*'] for line in lines[7:195]]
        return results

    def extract_columns(lines):
        columns = lines[5].split()
        columns.pop(-2)

        return columns

    # Read 'result' file
    with open(file, 'r') as f:
        lines = f.read().split('\n')

    columns = extract_columns(lines) 
    results = extract_results(lines)
    df = pd.DataFrame(results, columns=columns)

    # Clean Test names
    df['TEST'] = df['TEST'].apply(lambda x: NIST_TEST_NAME[x])

    # Column typing
    for (c, t) in zip(columns, [int]*10 + [float, str, str, bool]):
        df[c] = df[c].astype(t)
    df['PROPORTION'] = [eval(_) for _ in df['PROPORTION']]

    # Aggregation of same test instances
    df = df.groupby('TEST').agg({
        'C1': 'mean', 'C2': 'mean', 'C3': 'mean', 'C4': 'mean', 'C5': 'mean', 
        'C6': 'mean', 'C7': 'mean', 'C8': 'mean', 'C9': 'mean', 'C10': 'mean', 
        'P-VALUE': 'mean', 
        'PROPORTION': 'min', 
    })
    df = df.reset_index()

    # Add extra info
    path = [l for l in lines[3].split('/') if l!='']
    df = df.assign(Simulation = path[-2])
    df = df.assign(Algo = path[-1].split('.')[0])
    return df

def gather_results(data_directory):
    result_files = [os.path.join(data_directory, f"{folder}/{file}") for folder in os.listdir(data_directory) for file in os.listdir(os.path.join(data_directory, folder)) if file.endswith('.result')]
    return pd.concat([extract_data(file) for file in result_files])


def plot_pvalue(df):
    plt.figure(figsize=(12, 6))

    # Boxplot
    sns.boxplot(
        x="TEST", y="P-VALUE", hue="Algo",
        data=df, palette="Set2", fliersize=0, 
    )

    # Rotate x labels for readability
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('')

    # P-value threshold (0.05)
    # Add horizontal red dotted line at y=0.05
    plt.axhline(y=0.05, color='red', linestyle=':', linewidth=1)

    # Add y-tick at 0.05 and label it
    current_yticks = plt.yticks()[0]
    if 0.05 not in current_yticks:
        new_yticks = list(current_yticks) + [0.05]
        plt.yticks(sorted(new_yticks))
    plt.ylim(0,1)
    plt.ylabel('p-value')

    # Get existing legend handles (for hue="Algo")
    handles, labels = plt.gca().get_legend_handles_labels()
    # Create custom handle for threshold line
    threshold_line = Line2D([0], [0], color='red', linestyle=':', linewidth=1)
    # Add all handles to legend
    plt.legend(handles + [threshold_line], labels + ['threshold'], loc='upper center')


    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/p-values.png')
    plt.show()


def plot_hist_pvalues(df):
    fig, ax = plt.subplots(5, 3, figsize=(15, 10), sharex=True, sharey=True)
    colors = {'decentralized': 'steelblue', 'original': 'darkorange'}

    # Group data
    mean_df = df[['TEST', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'Algo']].groupby(['TEST', 'Algo']).agg('sum')

    # Ensure reproducible test and algo order
    test_list = sorted(df['TEST'].unique())
    algo_list = sorted(df['Algo'].unique())

    for t, test in enumerate(test_list):
        row, col = t // 3, t % 3
        # Build the data for this subplot
        average = [
            pd.DataFrame(
                [i * 0.1 + 0.05 for i, val in enumerate(mean_df.loc[test, algo]) for _ in range(int(val))],
                columns=['p-value']
            ).assign(Algo=algo, TEST=test)
            for algo in algo_list
        ]
        plot_df = pd.concat(average)

        # Plot on the correct subplot
        sns.histplot(
            data=plot_df, ax=ax[row, col], x="p-value", hue="Algo",
            bins=10, binrange=(0, 1), palette=colors,
            alpha=.1, element="step", stat="density", common_norm=False,
            legend=False,  # Disable subplot legend
        )
        ax[row, col].text(0.5, 1.4, test, ha='center', size=14)  # Centered title
        # ax[row, col].axhline(y=1., color='gray', linestyle='--', linewidth=1)
        sns.despine(ax=ax[row, col])

    # Global axis labels and ticks
    for a in ax.flatten():
        a.set_ylim(0, 1.5)
        a.set_xlim(0, 1)
        a.set_xticks([i * 0.1 for i in range(11)])

    # Create a common legend
    handles, labels = ax[0, 0].get_legend_handles_labels()
    # ax[0,0].legend(handles, labels, loc='upper center')
    d = Patch(facecolor=colors['decentralized'], edgecolor=colors['decentralized'], label='decentralized', alpha=.3)
    e = Patch(facecolor=colors['original'], edgecolor=colors['original'], label='original', alpha=0.3, linewidth=1.5)

    plt.legend(handles=[d,e], loc='lower right')
    # fig.text(0.5, 0.04, 'p-value', ha='center')  # Common x-label
    # fig.tight_layout(rect=[0, 0.03, 1, 0.95])    # Adjust for legend space

    plt.savefig('src/experiments/results/hist_values.png')
    plt.show()
    plt.close()
    

def plot_results(data_directory = 'src/experiments/data/'):
    df = gather_results(data_directory)
    plot_pvalue(df)
    plot_hist_pvalues(df)


if __name__ == "__main__":
    plot_results()
