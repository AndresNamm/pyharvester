from prefect import flow, task, get_run_logger
from pydantic import BaseModel
from prefect_azure import AzureCosmosDbCredentials
from prefect_azure.cosmos_db import cosmos_db_query_items
from models.general import ForestWarehouse
from typing import List
import logging
from dataclasses import dataclass


class ForestManagementProject(BaseModel):
    id: str
    forest_warehouses: List[ForestWarehouse] = []

@flow
def add_new_forest_management_project(id: str, owner_id:str ):
    forest_management_project = ForestManagementProject(id=id)	

@dataclass
class Kataster:
    id:str

@dataclass 
class Tarne:
    kataster: List[Kataster]
    saate_nr: str
    saate_kpv: str
    kogus: float
    hind: float

@flow
def check_for_forest_cutting_permissions(catasters:str):
    logger = get_run_logger()
    logger.info("Checking for forest notifications")
    logger.info(catasters)

@flow
def get_sales_act_nr(cataster:str):
    logger = get_run_logger()
    logger.info("Getting sales act nr")
    logger.info(cataster)

class TarneExtended:
    def __init__(self, tarne: Tarne):
        self.tarne = tarne
        self.cataster_notifications = []

@dataclass
class ReceivedGoods:







