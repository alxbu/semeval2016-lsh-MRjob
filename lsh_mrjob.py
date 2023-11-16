import hashlib
from mrjob.job import MRJob
from mrjob.step import MRStep
import os
import random

os.environ['PYTHONHASHSEED'] = '0'

def hash_shingle(shingle):
    """
    Hashes the shingle to a integer -> index of the signature matrix
    :param shingle:
    :return:
    """
    HASHUNIVERSE = 2**32 - 1
    return int(hashlib.sha1(shingle.encode()).hexdigest(), 16) % HASHUNIVERSE


def universal_hashing(p, m):
    """
    Generates a universal hash function
    :param p: prime number
    :param m: number of buckets
    :return: universal hash function
    """
    a = random.randint(1, p-1)
    b = random.randint(0, p-1)
    return lambda x: ((a*x + b) % p) % m


univ_hashes = [universal_hashing(2**32 - 5, 100) for _ in range(20)]


class LocalitySensitiveHashing(MRJob):

    def configure_args(self):
        super(LocalitySensitiveHashing, self).configure_args()
        self.add_passthru_arg('--num_hash_functions', type=int, default=20, help="Number of hash functions")
        self.add_passthru_arg('--num_bands', type=int, default=5, help="Number of bands")
        self.add_passthru_arg('--similarity_threshold', type=float, default=0.8, help="Similarity threshold")
        self.add_passthru_arg('--word_shingling', type=bool, default=False, help="Specify if word shingling is used, otherwise character shingling is used")
        self.add_passthru_arg('--k', type=int, default=3, help="Length of shingles")

    def lines_to_tuples(self, _, line):
        # yield each word in the line
        line1, line2, hash1, hash2 = line.split('\t')
        yield hash1, line1
        yield hash2, line2

    def shingle_lines(self, doc_id, line):
        if self.options.word_shingling:
            for inp in line:
                words = inp.split()
                for i in range(len(words) - self.options.k + 1):
                    yield doc_id, words[i:i+self.options.k]
        else:
            for inp in line:
                for i in range(len(inp) - self.options.k + 1):
                    yield doc_id, inp[i:i + self.options.k]

    def steps(self):
        return [
            MRStep(mapper=self.lines_to_tuples, reducer=self.shingle_lines)
        ]


if __name__ == '__main__':
    LocalitySensitiveHashing.run()