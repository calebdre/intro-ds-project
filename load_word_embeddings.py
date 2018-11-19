import torch
import io
import pickle
import sys
from math import ceil
import os

base_dir = "embeds"
embeddings_filename = "wiki-news-300d-1M-embedding"
vec_filename = "{}/wiki-news-300d-1M.vec".format(base_dir)

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.0f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def load_word_embeddings(top_n = 1000000, file_size = 50000):
    fin = io.open(vec_filename, 'r', encoding='utf-8', newline='\n', errors='ignore')
    vocab_size, vector_size = map(int, fin.readline().split())
    word_idx = {}
    saved_count = 1
    num_files = ceil(top_n / file_size)
    formatted_top_n = human_format(top_n)
    
    path = "{}/{}".format("embeds", formatted_top_n)
    if not os.path.exists(path):
        os.mkdir(path)

    print("Loading {} words into memory...".format(formatted_top_n))
    for i in range(top_n):
        tokens = fin.readline().rstrip().split(' ')
        word = tokens[0]
        vec = torch.tensor(list(map(float, tokens[1:])))
        
        word_idx[word] = vec
        if i > 0 and i % file_size == 0 or i == top_n-1:
            print("Saving file {} of {}".format(saved_count, num_files))
            save_file(saved_count, formatted_top_n, (word_idx, top_n, vector_size))
            word_idx = {}
            saved_count += 1
    
    filenames = ["{}/{}/{}-{}.pkl".format(base_dir, formatted_top_n, embeddings_filename, i) for i in range(1, saved_count)]
    print("\nDone! Embeddings can be found at:\n{}".format(", ".join(filenames)))
    print("Done!")

def read_word_embeddings(amount):
    directory = "{}/{}".format(base_dir, amount)
    files = os.listdir(directory)
    files = ["{}/{}".format(directory, file) for file in files if file.endswith(".pkl")]
    print("Reading files...")
    
    word_idx = {}
    
    first = files.pop(0)
    print("opening {}".format(first))
    with open(first, "rb") as f:
        w_i, vocab_size, vector_size = pickle.load(f)
        word_idx.update(w_i)

    for fname in files:
        print("opening {}".format(fname))
        with open(fname, "rb") as f:
            w_i, top_n, vec_size = pickle.load(f)
            word_idx.update(w_i)
    
    return word_idx, vocab_size, vector_size
    
def save_file(index, total, info):
    fname = "{}/{}/{}-{}.pkl".format(base_dir, total, embeddings_filename, index)
    with open(fname, "wb+") as f:
        pickle.dump(info, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        rows = int(sys.argv[1])
        file_size = int(sys.argv[2])
        load_word_embeddings(rows, file_size)
    else:
        load_word_embeddings()
