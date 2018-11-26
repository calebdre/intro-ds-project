import pandas as pd
import os
import pickle as pkl

combined_data_filename = "combined_raw_data.pkl"

def combine_raw_data():
    dfs = []
    files = [file for file in os.listdir("data") if ".csv" in file]    
    for file in files:
        path = "data/{}".format(file)
        genre_data = pd.read_csv(path, sep="|", index_col=None, header=0)
        dfs.append(genre_data)
    
    df = pd.concat(dfs, axis = 0, ignore_index = True)
    with open(combined_data_filename, "wb+") as f:
        pkl.dump(df, f, pkl.HIGHEST_PROTOCOL)
    
    return df

def get_combined_data():
    if os.path.exists(combined_data_filename):
        with open(combined_data_filename, "rb") as f:
            return pkl.load(f)
    else:
        return combine_raw_data()

if __name__ == "__main__":
    combine_raw_data()