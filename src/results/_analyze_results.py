import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.stats import ks_2samp, ks_1samp, chisquare, wasserstein_distance, entropy, uniform
from collections import defaultdict

NIST_TEST_NAME = [
    "Monobit Frequency",                        #  1
    "Monobit Frequency per Block",              #  2
    "Runs Test",                                #  3
    "Longest-Run-of-Ones in a Block",           #  4
    # "Binary Matrix Rank",                       #  5
    # "Discrete Fourier Transform (Spectral)",    #  6
    # "Non-overlapping Template Matching",        #  7
    # "Overlapping Template Matching",            #  8
    # "Maurer's Universal Statistical Test,",     #  9
    # "Linear Complexity Test",                   # 10
    # "Serial Test",                              # 11
    # "Approximate Entropy Test",                 # 12
    # "Cumulative Sums Test",                     # 13
    # "Random Excursions Test",                   # 14
    # "Random Excursions Variant Test"           # 15
]

def read_results(mode, data_directory):
    if mode == 'bitwise':
        CSV_FILE  = f"{data_directory}/pvalues_bitwise.csv"
    elif mode == 'headerwise':
        CSV_FILE  = f"{data_directory}/pvalues_headerwise.csv"
    else:
        raise Exception('Not valid mode')
    DTYPES = {
        "algo": str,
        "iteration": int,
        "test": int,
        "p-value": float
    }

    return pd.read_csv(CSV_FILE, dtype=DTYPES).assign(by=mode)

def all_hist(results, data_directory, smoothed=False):
    def histogram(ax, data, algo, smoothed=False):
        bin_size = 100
        y = data[(data['algo']==algo)]['p-value']
        if smoothed: # add random number [-bin_width, bin_width]
            y += (1-2*np.random.rand(len(y)))/bin_size
        ax.hist(y, color=colors[algo], label=legends[algo], bins=bin_size, histtype='stepfilled', alpha=0.3, density=True, stacked=True)
        
    colors = {'Decentralized':'darkorange', 'Original':'steelblue'}
    legends = {'Decentralized':'Decentralized', 'Original':'Original'}

    nbr_test = results['test'].max()
    fig, axs = plt.subplots(nbr_test, 2, figsize=(20, 20))

    # Loop over each subplot (axis) and the corresponding data

    for i, ax in enumerate(axs.flatten()): 
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlim(0.0, 1.00)
        test = 1+(i//2)
        if i%2==0: # leftside - headerwise
            data = results[(results['by']=='headerwise') & (results['test']==test)]
            histogram(ax, data, 'Original', smoothed)
            histogram(ax, data, 'Decentralized', smoothed)   
            ax.set_ylabel('Density', size=14)
            if test==1: 
                ax.set_xlabel('Headerwise', fontweight="bold", size=14, labelpad=10.0)
                ax.xaxis.set_label_position("top")
                ax.legend(fontsize=14)
            elif test==nbr_test:
                ax.set_xlabel('P-value', size=14)
        else: # rightside - bitwise
            data = results[(results['by']=='bitwise') & (results['test']==test)]
            histogram(ax, data,'Original', smoothed)
            histogram(ax, data, 'Decentralized', smoothed)
            ax.set_ylabel(f"Test {test}\n{NIST_TEST_NAME[test-1]}", fontweight="bold", size=14, labelpad=10.0)
            ax.yaxis.set_label_position("right")
            if test==1: 
                ax.set_xlabel('Bitwise', fontweight="bold", size=14, labelpad=10.0)
                ax.xaxis.set_label_position("top")
            elif test==nbr_test:
                ax.set_xlabel('P-value', size=14)  

    plt.suptitle("NIST Statistical Test Results", fontweight="bold", size=20, y=1)
    plt.tight_layout()

    if smoothed:
        plt.savefig(f"{data_directory}/all_hist_smoothed.png")
    else:
        plt.savefig(f"{data_directory}/all_hist_raw.png")
    plt.close()

def compare_distributions(results, data_directory):
    def ks_dist(sample_1, sample_2=None):
        if sample_2 is None: # Compare to uniform distribution
            ks = ks_1samp(sample_1, uniform.cdf, method='exact')
        else:
            ks = ks_2samp(sample_1, sample_2, method='exact')
        return (float(ks.statistic), float(ks.pvalue))  # ignored ks.statistic_sign and ks.statistic_location

    bins = 100
    stats = []

    for test in tqdm(range(1, 1+results['test'].max()), desc="NIST SP 800-22 Test: "):
        for by in ['headerwise', 'bitwise']:
            data = results[(results['by']==by) & (results['test']==test)]
            original = data[data['algo']=='Original']['p-value']
            decentralized = data[data['algo']=='Decentralized']['p-value']

            # Statistical tests:
            ################################# COMPARE DISTRIBUTION ##############################################
            # A) Kolmogorov–Smirnov (K-S) Test: 
            # statistic: It ranges from 0 (to identical distributions) to 1 (to completely disjoint ones).
            # pvalue:	The probability, under the null hypothesis that the two samples come from the same continuous distribution. A small value ⇒ the difference is unlikely to be just sampling noise.

            # B) Earth Mover’s Distance (Wasserstein Distance): 
            # Quantifies the "distance" between two distributions (Lower value = closer distributions)
            # Wasserstein Distance is a measure of the distance between two probability distributions. It is also called Earth Mover’s distance, short for EM distance, because informally it can be interpreted as the minimum energy cost of moving and transforming a pile of dirt in the shape of one probability distribution to the shape of the other distribution. The cost is quantified by: the amount of dirt moved x the moving distance. (source: https://lilianweng.github.io/posts/2017-08-20-gan/#what-is-wasserstein-distance)
            
            ks = ks_dist(decentralized, original)
            ks_o = ks_dist(original)
            ks_d = ks_dist(decentralized)

            row = {
                'by':by,
                'test': test,
                'wasserstein': float(wasserstein_distance(decentralized, original)),
                'wasserstein_o': float(wasserstein_distance(original, np.linspace(0, 1, len(original)))),
                'wasserstein_d': float(wasserstein_distance(decentralized,  np.linspace(0, 1, len(decentralized)))),
                'ks': ks[0],
                'ks_pvalue': ks[1],
                'ks_o': ks_o[0],
                'ks_o_pvalue': ks_o[1],
                'ks_d': ks_d[0],
                'ks_d_pvalue': ks_d[1],
            }

            stats.append(row)
    
    df = pd.DataFrame(stats)
    df.to_csv(f"{data_directory}/stats.csv", mode='w', index=False)

    
def plot_stats(data_directory):
    TYPES = {'by': str,'test': int,'wasserstein':float,'wasserstein_o':float,'wasserstein_d':float,'ks':float,'ks_pvalue':float,'ks_o':float,'ks_o_pvalue':float,'ks_d':float,'ks_d_pvalue':float}
    df = pd.read_csv(f"{data_directory}/stats.csv", dtype=TYPES)
    df['ks']=df['ks'].apply(eval)
    df['ks_o']=df['ks_o'].apply(eval)
    df['ks_d']=df['ks_d'].apply(eval)
    print(df)

    # TODO

def plot_results(data_directory = 'src/results/data'):
    bitwise = read_results('bitwise', data_directory)
    headerwise = read_results('headerwise', data_directory)
    results = pd.concat([bitwise[["algo", "test", "p-value", "by"]], headerwise[["algo", "test", "p-value", "by"]]])

    all_hist(results, data_directory, smoothed=False)
    all_hist(results, data_directory, smoothed=True)
    compare_distributions(results, data_directory)
    plot_stats(data_directory)

if __name__ == "__main__":
    plot_results()
