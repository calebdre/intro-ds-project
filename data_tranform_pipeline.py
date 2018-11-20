import pandas as pd
import pickle 
import os
    
class DataTransformPipeline:
    def __init__(self, data):
        self.data = data
        self.data_t = data
        self.transform_set = []
    
    @property
    def transforms(self):
        return [name for name, func in self.transform_set]

    def add(self, func, name = None, args = []):
        if name is None:
            name = func.__name__
            
        self.transform_set.append((name, func, args))
        return self
    
    def apply(self, pipeline_name):
        self.data_t = self.data
        
        for name, transform, args in self.transform_set:
            print("Applying '{}'".format(name))
            self.data_t = transform(self.data_t, *args)
        
        self.save(pipeline_name)
        return self.data_t
    
    def save(self, name):
        transforms_path = "./transforms"
        if not os.path.exists(transforms_path):
            os.mkdir(transforms_path)
            
        with open("{}/{}.pkl".format(transforms_path, name), "wb+") as f:
            pickle.dump(self, f)