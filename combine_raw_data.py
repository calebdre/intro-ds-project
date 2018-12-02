import pandas as pd
import os
import pickle as pkl

combined_data_filename = "combined_raw_data_prod.pkl"

def split_genres(row):
    if "/" in row["genre"]:
        genres = row["genre"].split("/")
        for i, genre in enumerate(genres):
            row["genre{}".format(i+1)] = genre
        return row
    else:
        row["genre1"] = row["genre"]
        row["genre2"] = row["genre"]
        row["genre3"] = row["genre"]
        return row

def combine_raw_data():
    dfs = []
    files = [file for file in os.listdir("data") if ".csv" in file]    
    for file in files:
        path = "data_prod/{}".format(file)
        try:
            genre_data = pd.read_csv(path, sep="|", index_col=None, header=0)
            dfs.append(genre_data)
        except Exception:
            print("Skipping {}".format(path))
    
    df = pd.concat(dfs, axis = 0, ignore_index = True)
    df = df[~df["story".isnull()]]
    df = df.apply(split_genres, axis=1)
    
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