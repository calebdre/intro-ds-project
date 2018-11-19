import pandas as pd
import pickle 
    
class DataTransformPipeline:
    def __init__(self, data):
        if type(data) is not pd.Series:
            raise Exception("Pipeline only accepts Pandas.Series objects.")
        
        self.data = data
        self.data_t = data
        self.transform_set = []
    
    @property
    def transforms(self):
        return [name for name, func in self.transform_set]

    def add_transform(self, name, func = None, args = []):
        if func is None and not hasattr(self, name):
            raise Exception("'{}' is not a valid transform.".format(name))
        
        self.transform_set.append((name, func, args))
        return self
    
    def apply(self, name):
        self.data_t = self.data
        
        for name, transform, args in transform_set:
            print("Applying {}".format(name))
            self.data_t = transform(self.data_t, *args)
        
        self.save(name)
        return self.data_t
    
    def save(self, name):
        transforms_path = "./transforms"
        if not os.path.exists(transforms_path):
            os.mkdir(transforms_path)
            
        with open("{}/{}.pkl".format(transforms_path, name), "wb+") as f:
            pickle.dump(self, f)