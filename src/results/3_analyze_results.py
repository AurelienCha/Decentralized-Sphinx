import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp, chisquare, wasserstein_distance, entropy

data_directory = 'src/results/data'
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

def read_results(mode):
    if mode == 'bitwise':
        CSV_FILE  = f"{data_directory}/pvalues_bitwise.csv"
        COLUMN_NAMES = ["algo", "bit", "test", "p-value"]
        DTYPES = {
            "algo": str,
            "bit #": int,
            "test": int,
            "p-value": float
        }
    elif mode == 'headerwise':
        CSV_FILE  = f"{data_directory}/pvalues_headerwise.csv"
        COLUMN_NAMES = ["algo", "date", "iteration", "layer", "test", "p-value"]
        DTYPES = {
            "algo": str,
            "date": str,
            "iteration": int,
            "layer": int,
            "test": int,
            "p-value": float
        }
    else:
        raise Exception('Not valid mode')

    return pd.read_csv(CSV_FILE, names=COLUMN_NAMES, dtype=DTYPES, header=0).assign(by=mode)

def all_hist(results):
    def histogram(ax, data, algo):
        ax.hist(data[(data['algo']==algo)]['p-value'], color=colors[algo], label=legends[algo] + " (100 bins)", bins=100, histtype='stepfilled', alpha=0.3, density=True, stacked=True)
        ax.hist(data[(data['algo']==algo)]['p-value'], color=colors[algo], label=legends[algo] + " (15 bins)", bins=15, histtype='step', alpha=1.0, density=True, stacked=True)
        
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
            histogram(ax, data, 'Original')
            histogram(ax, data, 'Decentralized')   
            ax.set_ylabel('Density', size=14)
            if test==1: 
                ax.set_xlabel('Headerwise', fontweight="bold", size=14, labelpad=10.0)
                ax.xaxis.set_label_position("top")
                ax.legend(fontsize=14)
            elif test==nbr_test:
                ax.set_xlabel('P-value', size=14)
        else: # rightside - bitwise
            data = results[(results['by']=='bitwise') & (results['test']==test)]
            histogram(ax, data,'Original')
            histogram(ax, data, 'Decentralized')
            ax.set_ylabel(NIST_TEST_NAME[test-1], fontweight="bold", size=14, labelpad=20.0)
            ax.yaxis.set_label_position("right")
            if test==1: 
                ax.set_xlabel('Bitwise', fontweight="bold", size=14, labelpad=10.0)
                ax.xaxis.set_label_position("top")
            elif test==nbr_test:
                ax.set_xlabel('P-value', size=14)  

    plt.suptitle("NIST Statistical Test Results", fontweight="bold", size=20, y=1)
    plt.tight_layout()

    plt.savefig(f"{data_directory}/all_hist.png")
    plt.close()

def compare_distributions(results):
    bins = 100
    stats = []

    for by in ['headerwise', 'bitwise']:
        for test in range(1, 1+results['test'].max()):
            data = results[(results['by']==by) & (results['test']==test)]
            original = data[data['algo']=='Original']['p-value']
            decentralized = data[data['algo']=='Decentralized']['p-value']

            # Statistical tests:
            ################################# COMPARE DISTRIBUTION ##############################################
            # A) Kolmogorov–Smirnov (K-S) Test: 
            # statistic: It ranges from 0 (to identical distributions) to 1 (to completely disjoint ones).
            # pvalue:	The probability, under the null hypothesis that the two samples come from the same continuous distribution. A small value ⇒ the difference is unlikely to be just sampling noise.
            ks = ks_2samp(decentralized, original, method='exact')

            # B) Earth Mover’s Distance (Wasserstein Distance): 
            # Quantifies the "distance" between two distributions (Lower value = closer distributions)
            # Wasserstein Distance is a measure of the distance between two probability distributions. It is also called Earth Mover’s distance, short for EM distance, because informally it can be interpreted as the minimum energy cost of moving and transforming a pile of dirt in the shape of one probability distribution to the shape of the other distribution. The cost is quantified by: the amount of dirt moved x the moving distance. (source: https://lilianweng.github.io/posts/2017-08-20-gan/#what-is-wasserstein-distance)
            ws = wasserstein_distance(decentralized, original)

            ################################# EVALUATE UNIFORMITY ##############################################
            # A) Chi-Squared Goodness-of-Fit Test (on histogram):
            # statistic: measure of how far the observed counts deviate from the expected ones. Larger values indicate larger deviation from expected distribution.
            # pvalue: means the probability of observing such a large discrepancy just by chance is essentially zero (often below 1e-16 in floating point).
            chi2_d = chisquare(np.histogram(decentralized, bins=bins, range=(0,1))[0],[len(decentralized)/bins] * bins)
            chi2_o = chisquare(np.histogram(original, bins=bins, range=(0,1))[0], [len(original)/bins] * bins)

            # B) Entropy of the p-value histogram: 
            # Measures how close your histogram is to uniform entropy (uniform -> max entropy)
            entropy_d = entropy(np.histogram(decentralized, bins=bins, range=(0,1))[0])
            entropy_o = entropy(np.histogram(original, bins=bins, range=(0,1))[0])


            row = {
                'by':by,
                'test': test,
                'chi2_decentralized': {'statistic':float(chi2_d[0]), 'p-value':float(chi2_d[1])},
                'chi2_original': {'statistic':float(chi2_o[0]), 'p-value':float(chi2_o[1])},
                'entropy_decentralized': (entropy_d),
                'entropy_original': (entropy_o),
                'ks': {'statistic':float(ks[0]), 'p-value':float(ks[1])},
                'wasserstein': float(ws)
            }

            stats.append(row)
    
    df = pd.DataFrame(stats)
    df.to_csv(f"{data_directory}/stats.csv", mode='w', index=False)
    print(df)
    



if __name__ == "__main__":
    bitwise = read_results('bitwise')
    headerwise = read_results('headerwise')
    results = pd.concat([bitwise[["algo", "test", "p-value", "by"]], headerwise[["algo", "test", "p-value", "by"]]])
    
    #all_hist(results)
    compare_distributions(results)
