NIST_TEST_NAME = {
    'Frequency':'     Frequency', 
    'BlockFrequency':'    Block Frequency', 
    'CumulativeSums': '    Cumulative Sums', 
    'Runs': '    Runs', 
    'LongestRun': '   Longest Run',      
    'Rank': '   Rank', 
    'FFT': '  Discrete Fourier Transform', 
    'NonOverlappingTemplate': '  Non-overlapping Matchings', 
    'OverlappingTemplate': '  Overlapping Matchings', 
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


def plot_pvalue(df, colors={'DSphinx': 'steelblue', 'Sphinx': 'darkorange'}):
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
    plt.legend(handles[::-1] + [threshold_line], labels[::-1] + ['threshold'], loc='upper center')


    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/p-values-of-p-values.png')
    plt.show()

def plot_hist_pvalues(df, colors={'DSphinx': 'steelblue', 'Sphinx': 'darkorange'}):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(5, 3, figsize=(15, 10), sharex=True, sharey=True)
    fig.subplots_adjust(hspace=0.1, wspace=0.05)

    # Group data
    mean_df = df[['TEST', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'Algo']].groupby(['TEST', 'Algo']).agg('sum')

    # Assign numbers to tests
    test_list = sorted(df['TEST'].unique())
    test_number_map = {name: i+1 for i, name in enumerate(test_list)}
    algo_list = sorted(df['Algo'].unique())

    for t, test in enumerate(test_list):
        row, col = t // 3, t % 3
        test_num = test_number_map[test]  # number to display

        # Build the data for this subplot
        average = [
            pd.DataFrame(
                [i * 0.1 + 0.05 for i, val in enumerate(mean_df.loc[test, algo]) for _ in range(int(val))],
                columns=['p-value']
            ).assign(Algo=algo, TEST_NUM=test_num)
            for algo in algo_list
        ]
        plot_df = pd.concat(average)

        # Plot histogram
        sns.histplot(
            data=plot_df, ax=ax[row, col], x="p-value", hue="Algo", palette=colors,
            bins=10, binrange=(0, 1),
            alpha=.3, element="step", stat="density", common_norm=False,
            legend=False,  # Disable subplot legend
        )
        # Display the test number instead of the full name
        ax[row, col].text(0.5, 1.25, f'Test {test_num}', ha='center', size=18)
        sns.despine(ax=ax[row, col])

    # Global axis labels and ticks
    for a in ax.flatten():
        a.set_ylim(0, 1.5)
        a.set_yticks([0, 1])
        a.tick_params(axis='y', labelsize=15)
        a.set_ylabel('')
        a.set_xlim(0, 1)
        a.set_xticks([0, 1])
        a.set_xlabel('')
        a.tick_params(axis='x', labelsize=15)

    fig.text(0.08, 0.48, 'Density', va='center', rotation='vertical', fontsize=17)
    fig.text(0.5, 0.06, 'P-value', ha='center', rotation='horizontal', fontsize=17)

    # Create a common legend
    d = Patch(facecolor=colors['DSphinx'], edgecolor=colors['DSphinx'], label='DSphinx', alpha=.3)
    e = Patch(facecolor=colors['Sphinx'], edgecolor=colors['Sphinx'], label='Sphinx', alpha=0.3, linewidth=1.5)
    plt.legend(handles=[e, d], loc='lower right', prop={'size': 17}, labelspacing=0.3, borderpad=0.3, borderaxespad=0.5)

    # Optional: print mapping number -> test name
    print("Test number mapping:")
    for name, num in test_number_map.items():
        print(f"{num}: {name}")

    plt.savefig('src/experiments/results/hist_p-valuesV2.png')
    plt.show()
    plt.close()

   
def plot_proportion_box(df, colors={'DSphinx': 'steelblue', 'Sphinx': 'darkorange'}):
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
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[::-1], labels[::-1], loc='lower right')

    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/proportion_boxplot.png')
    plt.show()
    plt.close()

def plot_proportion_dot(df, colors={'DSphinx': 'steelblue', 'Sphinx': 'darkorange'}):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import math

    plt.figure(figsize=(12, 6))

    # Assign numbers to tests
    test_list = sorted(df['TEST'].unique())
    test_number_map = {name: i+1 for i, name in enumerate(test_list)}
    df['TEST_NUM'] = df['TEST'].map(test_number_map)

    # Compute mean proportions per test & algorithm
    d = df[['TEST_NUM','PROPORTION','Algo']].groupby(['TEST_NUM','Algo']).mean().reset_index()

    # Plot
    g = sns.relplot(data=d, x='TEST_NUM', y='PROPORTION', hue='Algo', palette=colors, alpha=.6, s=80)
    g._legend.remove()
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[::-1], labels[::-1], loc='lower right', fontsize=12)

    # Axes
    plt.xticks(ticks=list(test_number_map.values()))  # numbers only
    plt.xlabel('Test #')
    plt.ylabel('Proportion')
    plt.ylim(0.95,1.001)
    plt.xlim(0.5, len(test_number_map)+0.5)

    # Confidence interval
    alpha = 0.01
    p = 1 - alpha
    m = 100 * (len(df) / 30)
    delta = 3 * math.sqrt(p * (1 - p) / m)
    p_min = p - delta
    p_max = p + delta
    plt.axhline(y=p_min, color='red', linestyle=':', linewidth=1)
    plt.axhline(y=p_max, color='red', linestyle=':', linewidth=1)

    plt.text(
        x=len(test_number_map)+0.5,
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
    plt.savefig('src/experiments/results/proportion_dotV2.png')
    plt.show()
    plt.close()

    # Optional: print mapping
    print("Test number mapping:")
    for name, num in test_number_map.items():
        print(f"{num}: {name}")


def plot_chisquare(df, colors={'DSphinx': 'steelblue', 'Sphinx': 'darkorange'}):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from scipy.stats import chisquare
    from matplotlib.lines import Line2D

    plt.figure(figsize=(8, 5)) 
    df = df[['TEST', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10','Algo']]
    df = df.groupby(['TEST','Algo']).sum().reset_index()

    # Assign numbers to tests
    test_names = sorted(df['TEST'].unique())
    test_number_map = {name: i+1 for i, name in enumerate(test_names)}
    df['TEST_NUM'] = df['TEST'].map(test_number_map)

    resultat = []
    for _, row in df.iterrows():
        test, algo, *values, test_num = row
        chi_square = chisquare(values)
        resultat.append([test_num, test, algo, chi_square[0], chi_square[1]])
        
    df_result = pd.DataFrame(resultat, columns=['TEST_NUM', 'TEST', 'Algo', 'STATISTIC', 'P-VALUE'])

    ax = sns.barplot(data=df_result, x='TEST_NUM', y='P-VALUE', hue='Algo', palette=colors, alpha=.6, width=0.85)
    
    # Horizontal threshold line
    plt.axhline(y=0.0001, color='red', linestyle=':', linewidth=1)
    
    # Log scale
    ax.set_yscale('log')
    
    plt.ylabel('P-value')
    plt.xlabel('Test #')
    
    # Legend
    handles, labels = plt.gca().get_legend_handles_labels()
    threshold_line = Line2D([0], [0], color='red', linestyle=':', linewidth=1)
    plt.legend(handles[::-1] + [threshold_line], labels[::-1] + ['threshold'], loc='lower right', fontsize=12)

    sns.despine()
    plt.tight_layout()
    plt.savefig('src/experiments/results/chisquareV2.png')
    df_result.to_csv('src/experiments/results/chisquareV2.csv')
    plt.show()
    plt.close()


def plot_results(data_directory = 'src/experiments/data/'):
    df = gather_results(data_directory)
    df = df.replace({'Algo': 'decentralized'}, 'DSphinx')
    df = df.replace({'Algo': 'original'}, 'Sphinx')
    colors = {'DSphinx': 'darkorange', 'Sphinx': 'darkblue'}
    # plot_pvalue(df, colors)
    plot_hist_pvalues(df, colors)
    # plot_proportion_box(df, colors)
    plot_proportion_dot(df, colors)
    plot_chisquare(df, colors)

if __name__ == "__main__":
    plot_results()
