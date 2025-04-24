import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from read_data import get_data, get_files


data = get_data()
nbr_samples = len(data)

res = []
for d in data:
    res.append(sum([1 for b in d if b=='1']))

print(f"Average nbr of 1: {(sum(res)/len(res)) / len(data[0])}")
r = [1 if 2*r >= len(data[0]) else 0 for r in res]
print(f"Proportion bigger than half: {sum(r)/len(data)}")


res = []
for i, d in enumerate(list(zip(*data))):
    s = sum([1 for b in d if b=='1'])
    res.append(s)
    if s > 0.66*len(data) or s < 0.33*len(data):
        print(i, s)

print(f"Average nbr of 1: {(sum(res)/len(res)) / len(data)}")
r = [1 if 2*r >= len(data) else 0 for r in res]
print(f"Proportion bigger than half: {sum(r)/len(data[0])}")