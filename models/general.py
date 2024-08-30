import prd
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Documentation:
    title: str
    url: str
    description: str


# Look into this https://envir.ee/elusloodus-looduskaitse/metsandus/biomasskutuste-saastlikkuse-kriteeriumid
@dataclass
class Source:
    id: str
    weight: float
    source_type: str
    documentation_list: List[Documentation] = []

@dataclass
class ForestBiomassSource(Source):
    source_type: str = "forest_biomass"

@dataclass
class NonForestBiomassSource(Source):
    source_type: str = "non-forest_biomass"

@dataclass
class SecondaryBiomassSource(Source):
    source_type: str = "secondary_biomass"

@dataclass
class FarmingBiomassSource(Source):
    source_type: str = "farm_based_biomass"


class ForestWarehouse:    
    def __init__(self,id:str, sources: List[Source]):
        self.id = id
        self.sources:Dict[str, Source] = {source.id: source for source in sources}

    def total_weight(self):
        return sum([source.weight for source in self.sources.values()])
    
    def source_percentage(self, source_type):
        return sum([source.weight for source in self.sources.values() if source.source_type == source_type]) / self.total_weight()

    def remove_percentage_from_source(self, source_id, percentage):
        source = self.sources[source_id]
        source.weight -= source.weight * percentage
        self.sources[source_id] = source

    def print_all_source_percentages(self):
        for source_type in set([source.source_type for source in self.sources.values()]):
            print(f"{source_type}: {self.source_percentage(source_type)}")


class ForestManagementProject:#121
    def __init__(self, forest_warehouses: List[ForestWarehouse]):
        self.forest_warehouses: Dict[str, ForestWarehouse] = {forest_warehouse.id: forest_warehouse for forest_warehouse in forest_warehouses}
    
    def add_forest_warehouse(self, forest_warehouse):
        self.forest_warehouses[forest_warehouse.id] = forest_warehouse
 





