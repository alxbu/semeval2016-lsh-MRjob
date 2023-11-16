# check_hash_collision.py
# check if there are any hash collisions in the preprocessed data

from preprocess_data import data_generator


def spread_to_buckets():
    """
    Spreads the data to buckets based on the hash
    :return: dictionary of buckets
    """
    buckets = {}

    for line in data_generator(source="data/preprocessed_data.txt", hash=False):
        line1, line2, hash_url1, hash_url2 = line
        if hash_url1 not in buckets:
            buckets[hash_url1] = []
        buckets[hash_url1].append(line1)
        if hash_url2 not in buckets:
            buckets[hash_url2] = []
        buckets[hash_url2].append(line2)

    return buckets


def count_false_positives(buckets):
    """
    Counts the number of false positives in the buckets - number of distinct urls in a bucket
    :param buckets: dictionary of buckets
    :return: None
    """
    false_positives = 0

    for bucket in buckets:
        if len(buckets[bucket]) > 1:
            distinct = set(buckets[bucket])
            num_distinct = len(distinct)
            if num_distinct > 1:
                print('False positive found!')
                false_positives += num_distinct - 1
            print(f"{bucket} : {distinct}")

    print('False positives: {}'.format(false_positives))


def main():
    """
    Main function
    :return: None
    """
    buckets = spread_to_buckets()
    count_false_positives(buckets)


if __name__ == '__main__':
    main()
