#%%
import numpy as np
import pandas as pd
import file_utils
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from pprint import pprint
from typing import Any, Callable, Generic, TypeVar,List

T = TypeVar('T')


@dataclass
class TimberVal(Generic[T]):
    k: str
    v: T


@dataclass
class TransformResult(Generic[T]):
    key: str
    val: str
    tf_val: T
    test: bool


#%%

class Transformer:
    class GenUtils:
        @staticmethod
        def parse_default_date(val) -> datetime:
            return datetime.strptime(val, '%Y%m%d%H%M%S')
        @staticmethod
        def is_equal(param1, param2):
            return {"condition": param1 == param2, "val1": param1, "val2": param2}

        @staticmethod
        def split_to_int(x):
            return [int(element) for element in x.split()]

    def transform(self, key, func: Any = lambda x: x, test: Callable[..., bool] = lambda x: True) -> TimberVal[T]:
        val = self.raw_data.loc[key]['val']
        tf_val: T = func(val)
        self.meta[key] = TransformResult(
            key=key, val=val, tf_val=tf_val, test=test(tf_val))
        return TimberVal[T](key, tf_val)

    def print_out_all_var(self):
        for k, v in vars(self).items():
            if isinstance(v, TimberVal):
                print(f"VARIABLE: {k}")
                print(self.meta[v.k])
                print()

    def __init__(self, raw_data):
        self.meta = {}
        self.raw_data = raw_data

#%%

class PrdTransformer(Transformer):
    def __init__(self, raw_data):
        self.meta = {}
        self.raw_data = raw_data
        #Initialize variables
        self.apt_file_name: TimberVal[str] = self.transform(key='2-2')
        self.last_reset: TimberVal[datetime] = self.transform(
            key='11-3', func=lambda val: datetime.strptime(val, '%y%m%d%H%M%S'))
        self.last_reset2: TimberVal[datetime] = self.transform(
            key='11-4', func=PrdTransformer.GenUtils.parse_default_date, test=lambda x: self.last_reset.v == x)
        self.last_saved: TimberVal[datetime] = self.transform(
            key='12-4', func=PrdTransformer.GenUtils.parse_default_date)
        self.buck_file_creation: TimberVal[datetime] = self.transform(
            key='13-4', func=PrdTransformer.GenUtils.parse_default_date, test=(lambda x: (self.last_saved.v - timedelta(days=30)) < x))
        self.production_start: TimberVal[datetime] = self.transform(
            key='16-4', func=PrdTransformer.GenUtils.parse_default_date, test=(lambda x: (self.last_saved.v - timedelta(days=10)) < x)) # Check that production did not start too much before last save. 
        self.production_start: TimberVal[datetime] = self.transform(
            key='16-4', func=PrdTransformer.GenUtils.parse_default_date, test=(lambda x: (self.last_saved.v - timedelta(days=10)) < x)) # Check that production did not start too much before last save. 
        self.nr_tree_species: TimberVal[int] = self.transform(key='111-1')
        
        self.print_out_all_var()


#%% 
DATA_PATH = '/workspaces/kv-scraper/timberly/results/'
TEST_FILE = 'apt_QB236-5.json'

fileinfo = file_utils.FileInfo(os.path.join(DATA_PATH, TEST_FILE))

sample_data = pd.read_json(fileinfo.abs_path, orient='index')

#%% 
class AptTransformer(Transformer):    

    def limits_to_interval(self, limits: str) -> List[tuple[int,int]]:
        lower_limits = [int(limit) for limit in limits.split()]
        return [( lower_limits[i], lower_limits[i+1] ) for i in range(len(lower_limits)-1)]

    # This function generates the price matrix based nr of diameter classes , nr of length classes and sortiments variable
  
    def __init__(self, raw_data):
        self.meta = {}
        self.raw_data = raw_data
        #Initialize variables
        self.apt_file_type: TimberVal[str] = self.transform(key='1-2')
        self.number_diameter_classes_per_sortiment: TimberVal[List[int]] = self.transform(key='117-1',func=Transformer.GenUtils.split_to_int )
        self.number_length_classes_per_sortiment: TimberVal[List[int]] = self.transform(key='118-1',func= Transformer.GenUtils.split_to_int)
        self.sortiments: TimberVal[List[str]] = self.transform(key='121-1',func= lambda x: [i.strip('\n') for i in x.split()])
        self.lower_diameter_limits: TimberVal[List[int]] = self.transform(key='131-1',func=Transformer.GenUtils.split_to_int )
        self.lower_length_limits: TimberVal[List[int]] = self.transform(key='132-1',func=Transformer.GenUtils.split_to_int)
        self.price_data: TimberVal[List[int]] = self.transform(key='162-2',func=  Transformer.GenUtils.split_to_int)
        self.print_out_all_var()

    


t = AptTransformer(sample_data)

# %%



class ModelGenerator():
    def __init__(self, apt_data: AptTransformer):
        self.apt_data = apt_data
        self.sortiment_association = self.generate_sortiment_association()
        self.price_matrix = self.generate_price_matrix()

    def generate_sortiment_association(self):
        # Create a dictionary that associates each sortiment with its diameter and length classes
        sortiment_association = {}
        global_diam_counter = 0
        global_length_counter = 0
        for i,sortiment in enumerate(self.apt_data.sortiments.v):
            sort_diam_classes_count:int = self.apt_data.number_diameter_classes_per_sortiment.v[i]
            sort_length_classes_count:int = self.apt_data.number_length_classes_per_sortiment.v[i]
            sortiment_association[sortiment] = {"diameter_classes":{"count": sort_diam_classes_count,"classes":[], "boundaries":(0,0)},"length_classes":{"count": sort_length_classes_count,"classes":[], "boundaries":(0,0)}}
            for j in range(global_diam_counter,global_diam_counter+sort_diam_classes_count):
                sortiment_association[sortiment]["diameter_classes"]["classes"].append((self.apt_data.lower_diameter_limits.v[j],self.apt_data.lower_diameter_limits.v[j+1]))
            global_diam_counter += sort_diam_classes_count + 1 
            sortiment_association[sortiment]["diameter_classes"]["boundaries"] = (sortiment_association[sortiment]["diameter_classes"]["classes"][0][0],sortiment_association[sortiment]["diameter_classes"]["classes"][-1][1])
            for j in range(global_length_counter,global_length_counter+sort_length_classes_count):
                sortiment_association[sortiment]["length_classes"]["classes"].append((self.apt_data.lower_length_limits.v[j],self.apt_data.lower_length_limits.v[j+1]))
            global_length_counter += sort_length_classes_count + 1
            sortiment_association[sortiment]["length_classes"]["boundaries"] = (sortiment_association[sortiment]["length_classes"]["classes"][0][0],sortiment_association[sortiment]["length_classes"]["classes"][-1][1])

        return sortiment_association

    def generate_price_matrix(self):
        # Create price matrix for each sortiment base on lower diameter and length limits
        price_matrix = {}
        counter=0
        for i,sortiment in enumerate(self.apt_data.sortiments.v):
            # Create an empty pandas dataframe with the correct dimensions for each sortiment
            row_index = [ f"{diam_class[0]}-{diam_class[1]}" for diam_class in self.sortiment_association[sortiment]["diameter_classes"]["classes"]]
            column_index=[f"{length_class[0]}-{length_class[1]}" for length_class in self.sortiment_association[sortiment]["length_classes"]["classes"]]
            price_matrix[sortiment] = pd.DataFrame(index=row_index,columns=column_index)

            sort_diam_classes_count:int = self.apt_data.number_diameter_classes_per_sortiment.v[i]
            sort_length_classes_count:int = self.apt_data.number_length_classes_per_sortiment.v[i]
            for j in range(sort_diam_classes_count):
                for k in range(sort_length_classes_count):
                    price_matrix[sortiment].loc[row_index[j],column_index[k]] = self.apt_data.price_data.v[counter]
                    counter+=1
            #print(sortiment)
            #print(price_matrix[sortiment])
        return price_matrix





m = ModelGenerator(t)


#%%


price_matrix_directory = f"{DATA_PATH}/{TEST_FILE.split('.')[0]}_price_matrixes"
os.makedirs(price_matrix_directory,exist_ok=True)
for sortiment,matrix in m.price_matrix.items():
    with open(f"{price_matrix_directory}/{sortiment}.csv","w") as f:
        # Write the price matrix to a csv file with separator ";"
        f.write(matrix.to_csv(sep=";"))

# %%


for sortiment,association in m.sortiment_association.items():
    print(sortiment)
    print(association)
    print("")

# %%
