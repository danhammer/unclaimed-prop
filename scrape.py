import sys
import getopt
import multiprocessing
import pickle
from random import sample
from numpy.random import randint
from cartodb_insert import upload, processed_ids


def create_list(n):
    """Generate a list of IDs to process, based on previous IDs that
    have been looked at.  Replace the file `processed.p` with a new
    pickle dump of all IDs considered.

    """
    with open("processed.p", "rb") as f:
        processed = pickle.load(f)
    series = randint(100, 99999999, n*2)
    idx_array = list(set(series) - set(processed))
    newids = sample(idx_array, n)

    with open("processed.p", "wb") as f:
        pickle.dump(processed + newids, f)

    return newids


def process_data(n):
    """Accepts and integer value and attempts to upload the n
    entries.

    """
    cpu = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpu)
    pool.map(upload, create_list(n))

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:")
    except getopt.GetoptError as err:
        print str(err) 

    for opt, arg in opts:
        if opt in ('-n'):
            process_data(int(arg))

if __name__ == "__main__":
   main()
