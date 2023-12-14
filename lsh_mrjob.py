import hashlib
from mrjob.job import MRJob
from mrjob.step import MRStep
import os
import random

os.environ['PYTHONHASHSEED'] = '0'
HASHUNIVERSE = 2**32 - 1


def hash_shingle(shingle):
    """
    Hashes the shingle to a integer -> index of the signature matrix
    :param shingle:
    :return:
    """
    return int(hashlib.sha1(shingle.encode()).hexdigest(), 16) % HASHUNIVERSE


def hash_band_signatures(signature):
    """
    Hashes the band signatures to a integer -> index of the bucket
    :param signature: band signature
    :return: index of the bucket
    """
    return int(hashlib.sha1(signature.encode()).hexdigest(), 16) % HASHUNIVERSE


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


class LocalitySensitiveHashing(MRJob):

    def __init__(self, *args, **kwargs):
        super(LocalitySensitiveHashing, self).__init__(*args, **kwargs)
        self.univ_hashes = [universal_hashing(2**32 - 5, HASHUNIVERSE) for _ in range(self.options.num_hash_functions)]

    def configure_args(self):
        super(LocalitySensitiveHashing, self).configure_args()
        self.add_passthru_arg('--num_hash_functions', type=int, default=20, help="Number of hash functions")
        self.add_passthru_arg('--num_bands', type=int, default=5, help="Number of bands")
        self.add_passthru_arg('--similarity_threshold', type=float, default=0.8, help="Similarity threshold")
        self.add_passthru_arg('--word_shingling', type=bool, default=False, help="Specify if word shingling is used, otherwise character shingling is used")
        self.add_passthru_arg('--k', type=int, default=3, help="Length of shingles")

    def lines_to_tuples(self, _, line):
        """
        Reads the data from the file and yields tuples of (hash, line)
        :param _: key
        :param line: A line from the file
        :return: (hash, line) tuple
        """
        line1, line2, hash1, hash2 = line.split('\t')
        yield hash1, line1
        yield hash2, line2

    def shingle_lines(self, doc_id, line):
        """
        Shingles the lines and yields tuples of (doc_id, shingle)
        :param doc_id: document id
        :param line: line from the file
        :return: (doc_id, shingle) tuple
        """
        if self.options.word_shingling:
            for inp in line:
                words = inp.split()
                for i in range(len(words) - self.options.k + 1):
                    yield doc_id, words[i:i+self.options.k]
        else:
            for inp in line:
                for i in range(len(inp) - self.options.k + 1):
                    yield doc_id, inp[i:i + self.options.k]

    def generate_signature(self, doc_id, shingles):
        """
        Generates the signature matrix
        :param doc_id: document id
        :param shingles: shingles of the document
        :return: (doc_id, signature) tuple
        """
        for shingle in shingles:
            if self.options.word_shingling:
                shingle = ' '.join(shingle)
            yield doc_id, hash_shingle(shingle)

    def min_hash(self, doc_id, signatures):
        """
        Min hashes the signature matrix
        :param doc_id: document id
        :param signatures: signature matrix
        :return: (doc_id, min_hash) tuple
        """
        min_hashes = [float('inf')] * self.options.num_hash_functions
        for signature in signatures:
            for i in range(self.options.num_hash_functions):
                min_hashes[i] = min(min_hashes[i], self.univ_hashes[i](signature))
        yield doc_id, min_hashes

    def generate_bands(self, doc_id, min_hashes):
        """
        Hashes the min hashes to buckets
        :param doc_id: document id
        :param min_hashes: min hashes
        :return: (doc_id, bucket) tuple
        """
        num_signatures_per_band = self.options.num_hash_functions // self.options.num_bands
        min_hashes = [item for sublist in list(min_hashes) for item in sublist]
        for i in range(self.options.num_bands):
            yield i, (doc_id, min_hashes[i*num_signatures_per_band:(i+1)*num_signatures_per_band])

    def locality_sensitive_hashing(self, band_id, docs):
        """
        Performs locality sensitive hashing
        :param band_id: band id
        :param docs: documents in the band
        :return: None
        """
        for doc_id, signature in docs:
            yield (band_id, hash_band_signatures(str(signature))), doc_id

    def find_pairs_from_bucket(self, band_bucket, document_ids):
        document_ids = list(document_ids)
        if len(document_ids) > 1:
            for i in range(len(document_ids)):
                for j in range(i+1, len(document_ids)):
                    yield (document_ids[i], document_ids[j]), 1

    def combine_pairs(self, pairs, step_num=0):

        pairs = list(pairs)
        for sublist in pairs:
            pair, count = sublist
            yield None, pair

    def final_reducer(self, _, pairs):
        """
        Final reducer to find the similar pairs
        Each pair is emitted only once
        Each pair counts as candidate
        :param _: key
        :param pairs: pairs of documents
        :return: None
        """
        pairs = list(pairs)
        for pair in pairs:
            yield pair[0], pair[1]

    def steps(self):
        return [
            MRStep(mapper=self.lines_to_tuples, reducer=self.shingle_lines),
            MRStep(reducer=self.generate_signature),
            MRStep(reducer=self.min_hash),
            MRStep(reducer=self.generate_bands),
            MRStep(reducer=self.locality_sensitive_hashing),
            MRStep(reducer=self.find_pairs_from_bucket),
            MRStep(combiner=self.combine_pairs, reducer=self.final_reducer)
        ]


if __name__ == '__main__':
    LocalitySensitiveHashing.run()