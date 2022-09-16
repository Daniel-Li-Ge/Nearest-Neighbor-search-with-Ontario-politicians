# K-NN, Clustering and Visualizing group dynamics with Covid politicians 

![image](https://user-images.githubusercontent.com/67663508/190527177-6ae49ba5-63d2-42db-b876-02e3567fa2b4.png)

I scraped some Ontario politicians and their follower information. I did a nearest neighbour analysis with low dimensional data and built a graph--each node being a politician. The graph is initially implemented as an undirected weighted edge list, with weights calculated locally on spark (and with the SQLite engine itself but that didn't go well), materialzed as a normalized table in SQLite. 

On my second iteration of this project I exported the original follower data to bigquery where I ran a few performance geared transformations and recomputed the edgelist. It **blew my old benchmarks out of the water**. Lastly I explore any potential socio-political patterns by visualizing the graph with various embedding and clustering methods

### SQLite & Spark (first iteration)

I did single pair Jaccard similarity calculations by writing SELECT statements in SQLite first. On an indexed table with row length in the tens of millions, a single calculation (~83,000 followers vs ~141,000) took ~12.98 seconds. An exhaustive KNN search (computing all the edges) would be an ```(O(n)^2-O(n))/2``` operation, With `n` being a few hundred the runtime would easily exceed 24 hours. For more reading on the its runtime: [Neo4j](https://neo4j.com/docs/graph-algorithms/current/labs-algorithms/jaccard/) has a great doc on it. 

The heart of the SQL statement used to calculate the intersection of followers between any two politicians:

```
SELECT COUNT(*) FROM
(
    SELECT id FROM mega_ids WHERE following = <id of politician of interest>
    INTERSECT
    SELECT id FROM mega_ids WHERE following = <another id of politician of interest>
)
```

I translated this to a Spark dataframe commands in the Jaccard.IPYNB. I'm fairly certain Spark SQL supports this notation directly as well but because of Windows (I've since started using Linux) and missing Hadoop dependencies I wasn't unable to directly use SQL syntax in Pyspark (see: [this](https://cwiki.apache.org/confluence/display/HADOOP2/WindowsProblems) and [this](https://github.com/cdarlint/winutils)) Certain libraries were not working on my computer even after troubleshooting and spending long hours configuring winutils, Spark and environment variables.

But for the sake of learning, I planned on rewriting it with data frame operations anyways. Here is the pairwise implementation of above in PySpark:

```

def jaccard(id_1, id_2, df_mega, f_count):
    start = time.time()
    intersect = df_mega.filter(df_mega.following == id_1)\
        .select("id")\
        .intersect(df_mega.filter(df_mega.following == id_2)\
        .select("id"))\
        .count()
    union = f_count.get(id_1) + f_count.get(id_2) - intersect
    print(time.time()-start)
    
    return intersect/union, intersect
 
 
 for i in range(len(keys)):
        node = keys[i]
        for k in range(i+1, len(keys)):
            count += 1
            node2 = keys[k]
            start = time.time()
            jaccard_i, intersect = jaccard(
                node,
                node2, 
                df_mega, 
                followers_count
            )
```

The same semantical operation in Pyspark in contrast averaged ~3.7 seconds--which is much faster

## BigQuery (2nd iteration)

Once I imported the SQL tables into BigQuery The previously normalized follower data was denormalized and stored in arrays. The table was unflattened in a query like this: 

```
CREATE TABLE `steady-triumph-343200.mesh.flat_edgelist` AS
  SELECT 
    p.id,
    ARRAY_AGG(
      e.id
    ) as followers
    
FROM `steady-triumph-343200.mesh.edgelist` AS e
  JOIN `steady-triumph-343200.mesh.pillars` AS p
    on P.id = e.following_id
 GROUP BY p.id
```

OLAP engines like BQ take advantage of denormalized schemas in complex, join heavy computations, I tested a single comparison--the jaccard index between 2 politicians: [SQL](https://github.com/Daniel-Li-Ge/Nearest-Neighbor-search-with-Ontario-politicians/blob/bq-clustering/bigquery-clustering/jaccard_single_comparison.sql). There was improvement from Spark but not by much.

I wasn't satisfied and there was room for improvement. I created a new, partioned and clustered table in BigQuery with otherwise the exact same data and schema. A pre-partitioned version of the linked query cost ~70mbs and took just under 3 seconds to run, whereas after, the cost was ~24mbs and ~2 seconds. **At scale, the exhaustive comparisons would cost ~2/3 less because whole columns scans wouldn't be necessary!** 

The following is the SQL for the pairwise comparisons needed to recompute a weighted edge list:

```
CREATE TEMP FUNCTION intersec(set1 ARRAY<INT64>, set2 ARRAY<INT64>)
  AS((
    SELECT COUNT(inter) FROM 
    (
      SELECT * FROM (SELECT * FROM UNNEST(set1))
        INTERSECT DISTINCT
      SELECT * FROM (SELECT * FROM UNNEST(set2))
     ) as inter
    ));
           
CREATE TEMP FUNCTION jacc(set1 ARRAY<INT64>, set2 ARRAY<INT64>, f1 INT64, f2 INT64)
  AS((
        SELECT ((select intersec(set1, set2)) / (f1 + f2)
      ) as index
    ));

SELECT 
  e1.id as node_1, 
  e2.id as node_2,
  jacc(e1.followers, e2.followers, e1.f_count, e2.f_count) as jacc
 FROM 
  `steady-triumph-343200.mesh.elist` e1
 INNER JOIN
  `steady-triumph-343200.mesh.elist` e2
 ON
  e1.id < e2.id
```
Because of BigQuery's parallelization behind the scenes, the entire pairwise computation took ~56 seconds!

### CLUSTERING:

I built a class to handle importing the edge list from BQ and converting it into a [SKLearn graph](https://scikit-network.readthedocs.io/en/latest/). I then explored a few different clustering methods and embeddings. 

For me details checkout my: [notebook](https://github.com/Daniel-Li-Ge/Nearest-Neighbor-search-with-Ontario-politicians/blob/bq-clustering/bigquery-clustering/ontario_poli.ipynb) (download it to view the images in full)

![image](https://user-images.githubusercontent.com/67663508/190526746-647282e2-f5f9-403d-b770-6378faf93b02.png)

## Note:
The Jaccard notebook has errors as outputs however the code is 100% working fine. The errors were caused by leaving Pyspark dataframes in memory for too long. 

In the scraper folder there's a forked file from twint API which I used to build a rotating proxy. The purpose was to bypass twitter's temporary IP bans for sending too many GET requests. It's currently working but unfinished as I'm working on getting it auto-rotate free and working proxies. 
