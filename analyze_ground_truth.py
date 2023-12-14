import os
from analyze_results import jaccard_similarity
from itertools import product
import json
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = 'data'


def main():

    # generate groud_truth folder if it doesn't exist
    if not os.path.exists('ground_truth'):
        os.makedirs('ground_truth')

    hyperparameter_dict = json.loads(open(f'hyperparameters.json').read())
    with open(f'{DATA_DIR}/preprocessed_data.txt', 'r') as f:
        inp = f.readlines()
    f.close()

    pairs = [line.split('\t')[:2] for line in inp]

    for pair in pairs:
        pair[0] = pair[0].strip()
        pair[1] = pair[1].strip()
        if pair[0] == "" or pair[1] == "":
            print(pair)

    for k, w in product(hyperparameter_dict["ks"], hyperparameter_dict["word_shingling"]):
        w = (w == 'True')
        print(f"k: {k}, w: {w}")
        data = [jaccard_similarity(pair[0], pair[1], k, w) for pair in pairs]
        plt.figure()
        sns.displot(data, kde=False)
        plt.xlabel('Jaccard Similarity')
        plt.ylabel('Frequency')
        plt.title(f'Jaccard Similarity Distribution for k={k} and word_shingling={w}')
        plt.savefig(f'ground_truth/k{k}_w{w}.png')
        plt.close()



if __name__ == '__main__':
    main()
