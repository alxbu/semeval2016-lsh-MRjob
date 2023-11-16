# python preprocess_data.py
# Description: Preprocess data for training
import hashlib


def hash_url(url):
    """
    Hashes the url to a 8 digit hex number
    :param url: url to be hashed
    :return: 8 digit hex number representing the url
    """
    return hashlib.sha1(url.encode()).hexdigest()[:8].upper()


def data_generator(source='data/sts2016-english-with-gs-v1.0/STS2016.input.answer-answer.txt', hash=True):
    """
    Generator for reading data from source
    :param source: file to read data from
    :return: preprocessed lines from data in format (line1, line2, hash_url1, hash_url2)
    """

    with open(source, 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            if hash:
                yield line[0], line[1], hash_url(line[2]), hash_url(line[3])
            else:
                yield line


def write_data_to_file(data_generator, target='data/preprocessed_data.txt'):
    """
    Writes data to target file
    :param data_generator: generator for data to be written
    :param target: target file to write data to
    :return: None
    """
    with open(target, 'w') as f:
        for line in data_generator:
            f.write('\t'.join(line) + '\n')


def main():
    """
    Main function
    :return: None
    """
    write_data_to_file(data_generator())


if __name__ == '__main__':
    main()
