from lsh_mrjob import LocalitySensitiveHashing
from itertools import product
import os

ks = [2, 3, 4]
num_hash_functions = [20, 50, 100]
num_bands = [5, 10, 20]
word_shingling = [True, False]


def main():
    # generate output folder if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

    for k, h, b, w in product(ks, num_hash_functions, num_bands, word_shingling):
        print(f"k: {k}, h: {h}, b: {b}, w: {w}")
        mr_job = LocalitySensitiveHashing(
            args=['data/preprocessed_data.txt', '--num_hash_functions', str(h), '--num_bands', str(b), '--k', str(k),
                  '--word_shingling', str(w), '--output-dir', f'output/k{k}_h{h}_b{b}_w{w}.txt'])
        with mr_job.make_runner() as runner:
            runner.run()


if __name__ == '__main__':
    main()
