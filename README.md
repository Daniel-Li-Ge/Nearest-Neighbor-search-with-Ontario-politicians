# onpoli-TWITTER-OSINT-graph
I scraped some Ontario politicians and their follower information. I did a nearest neighbor analysis with low dimensional data and built a graph--each node being a politician. The graph is implemented through a table in SQLite that adheres to 3NF. I'm currently working on visualizing the graph and pushing another notebook of basic data visualizations using matplotlib

There's also a forked file from twint API which I used to build a rotating proxy. The purpose was to bypass twitter's temprorary IP bans for sending too many GET requests. It's currently working but unfinished as I'm working on getting it auto rotate free and working proxies. 

#Raw SQLite vs Spark SQL (Why i used spark)

I did the Jaccard similarity calculations by writing SELECT statements in SQLite first. On an indexed table with row length in the tens of millions, a single calculation (~83,000 followers vs ~141,000) costed ~12.98 seconds. Completing an entire nearest neighbor graph is an (O(n)^2-O(n))/2 operation, With n being a few hundred the runtime would easily exceed 24 hours. 

The heart of the SQL statement used to calculate intersection of followers between two politicians:

```
SELECT COUNT(*) FROM
(
    SELECT id FROM mega_ids WHERE following = <id of politician of interest>
    INTERSECT
    SELECT id FROM mega_ids WHERE following = <another id of politician of interest>
)
```

I translated this to Spark dataframe commands in the Jaccard.IPYNB. I'm fairly certain Spark SQL supports this notation directly as well but because of Windows and missing Hadoop dependencies I wasn unable to directly us SQL syntax in Pyspark (see: [this](https://cwiki.apache.org/confluence/display/HADOOP2/WindowsProblems) and [this](https://github.com/cdarlint/winutils)) Certain libraries were not working on my computereven after troubleshooting and spending long hours configuring winutils, Spark and environment variables. But for the sake of learning I planned on rewriting it with dataframe operations anyways.

# Note:
The jaccard notebook has errors as outputs however the code is 100% working fine. The errors were caused by leaving Pyspark dataframes in memory for too long. 


