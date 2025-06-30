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

from scipy.stats import chisquare
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import math
import os 

# Set Seaborn and Matplotlib font sizes
sns.set_context("paper", font_scale=1.5)  # or "talk", "notebook", "poster"

# Optional: Customize even more
# plt.rcParams.update({
#     "axes.titlesize": 16,
#     "axes.labelsize": 14,
#     "xtick.labelsize": 12,
#     "ytick.labelsize": 12,
#     "legend.fontsize": 12,
#     "font.size": 14,
# })

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


def plot_pvalue(df, colors={'decentralized': 'steelblue', 'original': 'darkorange'}):
    plt.figure(figsize=(12, 6))

    # Boxplot
    sns.boxplot(data=df, x="TEST", y="P-VALUE", hue="Algo", palette=colors, fliersize=3)

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
    plt.savefig('src/experiments/results/p-values-of-p-values.png')
    plt.show()

def plot_hist_pvalues(df, colors={'decentralized': 'steelblue', 'original': 'darkorange'}):
    fig, ax = plt.subplots(5, 3, figsize=(15, 10), sharex=True, sharey=True)
    fig.subplots_adjust(hspace=0.4)

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
            data=plot_df, ax=ax[row, col], x="p-value", hue="Algo", palette=colors,
            bins=10, binrange=(0, 1),
            alpha=.1, element="step", stat="density", common_norm=False,
            legend=False,  # Disable subplot legend
        )
        ax[row, col].text(0.5, 1.3, test, ha='center', size=15)  # Centered title
        # ax[row, col].axhline(y=1., color='gray', linestyle='--', linewidth=1)
        sns.despine(ax=ax[row, col])

    # Global axis labels and ticks
    for a in ax.flatten():
        a.set_ylim(0, 1.5)
        a.set_xlim(0, 1)
        a.set_xticks([i * 0.2 for i in range(6)])

    # Create a common legend
    handles, labels = ax[0, 0].get_legend_handles_labels()
    # ax[0,0].legend(handles, labels, loc='upper center')
    d = Patch(facecolor=colors['decentralized'], edgecolor=colors['decentralized'], label='decentralized', alpha=.3)
    e = Patch(facecolor=colors['original'], edgecolor=colors['original'], label='original', alpha=0.3, linewidth=1.5)

    plt.legend(handles=[d,e], loc='lower right')
    # fig.text(0.5, 0.04, 'p-value', ha='center')  # Common x-label
    # fig.tight_layout(rect=[0, 0.03, 1, 0.95])    # Adjust for legend space

    plt.savefig('src/experiments/results/hist_p-values.png')
    plt.show()
    plt.close()
   
def plot_proportion_box(df, colors={'decentralized': 'steelblue', 'original': 'darkorange'}):
    plt.figure(figsize=(12, 6))

    df = df[['TEST', 'Algo', 'PROPORTION']]
    sns.boxplot(data=df, x='TEST', y='PROPORTION', hue='Algo', palette=colors, fliersize=3)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('')
    plt.ylim(0.94,1.001)
    plt.xlim(-0.5,14.7)

    alpha = 0.01
    p = 1 - alpha
    m = 100 * (len(df) / 30)
    delta = 3 * math.sqrt(p * (1 - p) / m)
    p_min = p - delta
    p_max = p + delta

    plt.axhline(y=p_min, color='red', linestyle=':', linewidth=1)
    plt.axhline(y=p_max, color='red', linestyle=':', linewidth=1)

    plt.text(
        x=14.7,
        y=(p_min+p_max)/2,
        s='Confidence Interval',
        color='red',
        fontsize=10,
        ha='right',
        va='center',
        rotation=-90,
        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none')
    )
    plt.legend(loc='lower right')

    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/proportion_boxplot.png')
    plt.show()
    plt.close()

def plot_proportion_dot(df, colors={'decentralized': 'steelblue', 'original': 'darkorange'}):
    plt.figure(figsize=(12, 6))

    d = df[['TEST','PROPORTION','Algo']].groupby(['TEST','Algo']).mean()
    d = d.reset_index()
    g = sns.relplot(data=d, x='TEST', y='PROPORTION', hue='Algo', palette=colors, alpha=0.7)
    g._legend.remove()
    plt.legend(loc='lower right')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('')
    plt.ylabel('Proportion')
    plt.ylim(0.94,1.001)
    plt.xlim(-0.5,14.5)

    alpha = 0.01
    p = 1 - alpha
    m = 100 * (len(df) / 30)
    delta = 3 * math.sqrt(p * (1 - p) / m)
    p_min = p - delta
    p_max = p + delta

    plt.axhline(y=p_min, color='red', linestyle=':', linewidth=1)
    plt.axhline(y=p_max, color='red', linestyle=':', linewidth=1)

    plt.text(
        x=14.5,
        y=p_max,
        s='Confidence Interval',
        color='red',
        fontsize=11,
        ha='right',
        va='center',
        rotation=0,
        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none')
    )

    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/proportion_dot.png')
    plt.show()
    plt.close()

def plot_chisquare(df, colors={'decentralized': 'steelblue', 'original': 'darkorange'}):

    size = len(df)/30
    df = df[['TEST', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10','Algo']]
    df = df.groupby(['TEST','Algo']).sum().reset_index()

    resultat = []
    for _, row in df.iterrows():
        test, algo, *values = row
        chi_square = chisquare(values)
        resultat.append([test, algo, chi_square[0], chi_square[1]])
        
    df = pd.DataFrame(resultat, columns=['TEST', 'Algo', 'STATISTIC', 'P-VALUE'])
    ax = sns.barplot(data=df, x='TEST', y='P-VALUE', hue='Algo', palette=colors, alpha=0.7)
    plt.axhline(y=0.0001, color='red', linestyle=':', linewidth=1)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('P-value')
    plt.xlabel('')
    ax.set_yscale('log')

    handles, labels = plt.gca().get_legend_handles_labels()
    threshold_line = Line2D([0], [0], color='red', linestyle=':', linewidth=1)
    plt.legend(handles + [threshold_line], labels + ['threshold'], loc='lower right', fontsize=15)

    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/chisquare.png')
    df.to_csv('src/experiments/results/chisquare.csv')
    plt.show()
    plt.close()

def plot_results(data_directory = 'src/experiments/data/'):
    colors = {'decentralized': 'steelblue', 'original': 'darkorange'}
    df = gather_results(data_directory)
    plot_pvalue(df, colors)
    plot_hist_pvalues(df, colors)
    plot_proportion_box(df, colors)
    plot_proportion_dot(df, colors)
    plot_chisquare(df, colors)

if __name__ == "__main__":
    plot_results()
