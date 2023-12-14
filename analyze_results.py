import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = 'output'
DATA_DIR = 'data'
REPORT_DIR = 'report'


def shingle(line, k=3, word_shingling=False):
    if word_shingling:
        words = line.split()
        return set([str(words[i:i + k]) for i in range(len(words) - k + 1)])

    else:
        return set([line[i:i + k] for i in range(len(line) - k + 1)])


def jaccard_similarity(line1, line2, k=3, word_shingling=False):
    """
    Calculates the Jaccard similarity between two sets
    :param set1: set 1
    :param set2: set 2
    :return: Jaccard similarity
    """
    set1 = shingle(line1, k, word_shingling)
    set2 = shingle(line2, k, word_shingling)

    if len(set1.union(set2)) == 0:
        return 0

    return len(set1.intersection(set2)) / len(set1.union(set2))


def main():

    # generate report folder if it doesn't exist
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    data_dict = json.loads(open(f'{DATA_DIR}/preprocessed_data.json').read())
    for sub_output in os.listdir(OUTPUT_DIR):
        res_str = ''
        jac_list = []
        if sub_output.endswith('.txt'):
            parameters = sub_output.split('.')[0].split('_')
            print(parameters)
            k = int(parameters[0][1:])
            h = int(parameters[1][1:])
            b = int(parameters[2][1:])
            w = parameters[3][1:] == 'True'
            with open(f'{OUTPUT_DIR}/{sub_output}/part-00000', 'r') as f:
                for line in f:
                    hash1, hash2 = line.strip().split('\t')
                    hash1, hash2 = hash1[1:-1], hash2[1:-1]
                    line1, line2 = data_dict[hash1], data_dict[hash2]
                    jac = jaccard_similarity(line1, line2, k, w)
                    jac_list.append(jac)
                    res_str += f'{line1}\t{line2}\t{jac}\n'
            with open(f'{REPORT_DIR}/{sub_output}', 'w') as f:
                f.write(res_str)

            # empty plot
            plt.clf()
            # plot histogram using displot
            #sns.displot(jac_list, kde=True)
            sns.histplot(jac_list, kde=True)
            plt.title(f'LSH with k={k}, h={h}, b={b}, w={w}')
            plt.xlabel('Jaccard similarity')
            plt.ylabel('Frequency')
            plt.savefig(f'{REPORT_DIR}/{sub_output}.png')


if __name__ == '__main__':
    main()
