from scipy.signal import savgol_filter
from termcolor import colored
import matplotlib.pyplot as plt
import pickle
import os
import time
import torch
import pickle
from scipy.signal import lfilter
import time
from tabulate import tabulate
import operator

class Experiments:
    def __init__(self, trials = []):
        self.trials = trials
    
    def add(self, trial):
        self.trials.append(trial)
        return self
    
    def save(self, name):
        with open("experiments_{}.pkl".format(name, "wb+") as f:
            pickle.dump(self, f)

    def load(self, name):
        with open("experiments_{}.pkl".format(name, "rb") as f:
            return pickle.load(run_info, f)
    
    def summarize(self, keys):
        table = []
        for trial in self.trials:
            table_row = {}
            for key in keys:
                table_row[key] = trial[key]
            table.append(table_row)
        
        summary = tabulate(
            table, 
            headers="keys", 
            tablefmt="grid",
            showindex="always"
        )
        print(summary)
        
    def __getitem__(self, key):
        return self.trials[key]