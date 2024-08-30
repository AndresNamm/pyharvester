from dataclasses import dataclass
from typing import List,Tuple
from datetime import date
import numpy as np
import numpy.typing as npt
import pandas as pd 

class MeasureMentMatrix:
    def __init__(self, diameter_classes: List[Tuple[int, int]], length_classes: List[Tuple[int, int]]):
        # Create a 2D pandas dataframe with diameter and length classes as columns and rows filled with zeros
        self.matrix = pd.DataFrame(
            0,
            index=[f"{diameter_class[0]}-{diameter_class[1]}" for diameter_class in diameter_classes],
            columns=[f"{length_class[0]}-{length_class[1]}" for length_class in length_classes]
        )
    
    def assign(self, diameter_class: Tuple[int,int], length_class: Tuple[int,int], value):
        self.matrix.loc[f"{diameter_class[0]}-{diameter_class[1]}", f"{length_class[0]}-{length_class[1]}"] = value
        
    def get(self, diameter_class: Tuple[int,int], length_class: Tuple[int,int]):
        return self.matrix.loc[f"{diameter_class[0]}-{diameter_class[1]}", f"{length_class[0]}-{length_class[1]}"]

    def __repr__(self):
        return self.matrix.__repr__()

@dataclass
class Sortiment:
    # List of tuples (diameter, length)
    diameter_classes: List[Tuple[int, int]] 
    length_classes: List[Tuple[int, int]]
    price_matrix: MeasureMentMatrix

@dataclass
class CalibrationInfo:
    calibration_dates: List[date]
    nr_of_calibrations: int
    nr_of_calibrations_per_tree_species: List[int]

@dataclass
class PrdFile:
    sortiments: List[Sortiment]
    calibration_info: CalibrationInfo 
    

if __name__ == "__main__":
    # Test
    diameter_classes = [(10, 20), (20, 30), (30, 40)]
    length_classes = [(1, 2), (2, 3), (3, 4)]
    price_matrix = MeasureMentMatrix(diameter_classes, length_classes)
    
    # Assign random prices for the price matrix
    for diameter_class in diameter_classes:
        for length_class in length_classes:
            price_matrix.assign(diameter_class, length_class, np.random.randint(1, 100))

    sortiment = Sortiment(diameter_classes, length_classes, price_matrix)
    

    print(price_matrix)
