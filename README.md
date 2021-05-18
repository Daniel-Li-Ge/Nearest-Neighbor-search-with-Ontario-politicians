# onpoli-TWITTER-OSINT-graph
I scraped some Ontario politicians and their follower information. I did a nearest neighbour analysis with low dimensional data and built a graph--each node being a politician. The graph is implemented through a table in SQLite that adheres to 3NF. I'm currently working on visualizing the graph and pushing another notebook of basic data visualizations using matplotlib

There's also a forked file from twint API which I used to build a rotating proxy. The purpose was to bypass twitter's temporary IP bans for sending too many GET requests. It's currently working but unfinished as I'm working on getting it auto-rotate free and working proxies. 

# Raw SQLite vs Spark SQL (Why I used spark)

I did the Jaccard similarity calculations by writing SELECT statements in SQLite first. On an indexed table with row length in the tens of millions, a single calculation (~83,000 followers vs ~141,000) costed ~12.98 seconds. Completing an entire nearest neighbour graph is an ```(O(n)^2-O(n))/2``` operation, With `n` being a few hundred the runtime would easily exceed 24 hours. For more reading on the Jaccard algorithm, its runtime: [Neo4j](https://neo4j.com/docs/graph-algorithms/current/labs-algorithms/jaccard/) has a great doc on it. 

The heart of the SQL statement used to calculate the intersection of followers between two politicians:

```
SELECT COUNT(*) FROM
(
    SELECT id FROM mega_ids WHERE following = <id of politician of interest>
    INTERSECT
    SELECT id FROM mega_ids WHERE following = <another id of politician of interest>
)
```

I translated this to Spark dataframe commands in the Jaccard.IPYNB. I'm fairly certain Spark SQL supports this notation directly as well but because of Windows and missing Hadoop dependencies I wasn't unable to directly use SQL syntax in Pyspark (see: [this](https://cwiki.apache.org/confluence/display/HADOOP2/WindowsProblems) and [this](https://github.com/cdarlint/winutils)) Certain libraries were not working on my computer even after troubleshooting and spending long hours configuring winutils, Spark and environment variables. But for the sake of learning, I planned on rewriting it with data frame operations anyways.

The same semantical operation in Pyspark in contrast averaged ~3.4 seconds--which is much faster

# In construction

I'm working on pushing another notebook of Matplotlib visualizations for simple Statistics ie. top 10 most similar follower overlaps. 

# In the future 

I plan on doing this exact project again but at a much larger scale--hopefully with another person. This time data can be mined in parallel. We can increase the dimensions of our data (such as including individual follower features) for more interesting and accurate analyses. I also want to do parallel computing with the data to drastically increase the speeds of calculations. I already wrote code for it but again because of configuration issues I was unable to get it working. Lastly I'd like to take the data and apply a clustering algorithm on it. 

# Note:
The Jaccard notebook has errors as outputs however the code is 100% working fine. The errors were caused by leaving Pyspark dataframes in memory for too long. 


