import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence
import numpy as np

class Data(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, key):
        return self.data[key], self.labels[key]
    
    def get_loader(self, batch_size = 32):
        return DataLoader(
            dataset = self,
            batch_size = batch_size,
            collate_fn = self.collate,
            shuffle = True
        )
    
    def collate(self, batch):
        lengths = []
        data = []
        labels = []
                
        for datum, label in batch:
            data.append(datum)
            lengths.append(len(datum))
            labels.append(label)
        
        lengths, sorted_idxs = torch.tensor(lengths).sort(descending=True)
        data = pad_sequence(data, batch_first=True)
        data = data[sorted_idxs]
        labels = torch.tensor(labels)[sorted_idxs]
        
        return [lengths, labels, data]