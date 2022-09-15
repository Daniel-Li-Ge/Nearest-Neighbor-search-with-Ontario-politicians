import os
import numpy as np
from sknetwork.data import convert_edge_list
import pandas as pd
from google.cloud import bigquery
from apikey import api_key, CREDENTIALS

os.environ[CREDENTIALS] = api_key

class CustomBigQueryKNN:
    """Custom graph based off of edge_list computed in BigQuery
    Parameters
    ----------
    raw_result: google.cloud.bigquery.job.query.QueryJob
        The iterable result from BigQuery API

    """
    def __init__(self, raw_result=None):
        self.raw_result = raw_result
        self.graph = None
        self.pd_edge_list = None
        self.index = {}
        self.handle = {}
    
    def query_raw(self):
        """Contains a BQ API call to set and get jaccard distance edge list
        isn't initialzed right away because queries cost money

        Returns
        -------
        self
        """ 
        try:    
            client = bigquery.Client()
            query = """
                    SELECT 
                (select handle from `steady-triumph-343200.mesh.pillars` 
                    where CAST(id AS INT) = node_1) handle, 
                (select handle from `steady-triumph-343200.mesh.pillars` 
                    where CAST(id AS INT) = node_2) handle2,
                jacc
                FROM `steady-triumph-343200.mesh.jacc_edge`
                """
            query_job = client.query(query)

            q2 = """
                SELECT handle FROM `steady-triumph-343200.mesh.pillars`
            """
            query_job_2 = client.query(q2)

            self.index = {row.handle: i for i, row in enumerate(query_job_2)}
            self.handle = {v: k for k, v in self.index.items()}
            
            self.raw_result = query_job
            return self

        except Exception as e:
            print(e)
            print("API call failed")
             
    def get_skngraph(self, max_weight=None, min_weight=None, soergel=False): 
        """
        Params
        -------
        max_weight:
             dictates maxmimum edge weight of the created graph
        min_weight:
             dictates minimum edge weight of the created graph
        soergel:
            1 - jaccard index
        Returns
        -------
        self
        
        """
        if self.raw_result: 
            data = [(i.handle, i.handle2, i.jacc) for i in self.raw_result]         
            df = pd.DataFrame(data, columns =['Handle1', 'Handle2', 'jacc'])
            self.pd_edge_list = df.copy(deep=True)
            if soergel:
                df['jacc'] = 1 - df['jacc']
            if max_weight:
                df = df[df['jacc'] < max_weight]
            elif min_weight:
                df = df[df['jacc'] > min_weight]
            edge_list = df.to_numpy()
            self.graph = convert_edge_list(edge_list, weighted=True)

            return self

        else:
            raise Exception("There is no data to work with \
            Make an API call or load your own data")
    
    def knn(self, node, k=1):
        """
        Params
        -------
        node: str | int
            the target node to find k-nearest neighbors
        k: optional[int]
            number of nearest neighbors
        Returns
        -------
        neigh: dict
        
        """
       
        if isinstance(node, int): 
            node = self.handle.get(node)
        k = k if isinstance(k, int) and k<4 else 1
        df = self.pd_edge_list
        nr = df[(df["Handle1"].str.match(node)) | (df["Handle2"].str.match(node))]\
                    .nlargest(k, ['jacc'])
        neigh = {}
        for i in range(k):
            n = nr["Handle1"].tolist()[i] if \
            nr["Handle1"].tolist()[i] != node else \
            nr["Handle2"].tolist()[i]
            neigh[n] = nr["jacc"].tolist()[i]  
        return neigh