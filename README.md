# onpoli-TWITTER-OSINT-graph
I scraped some Ontario politicians and their follower information. I did a nearest neighbor analysis with low dimensional data and built a graph--each node being a politician. The graph is implemented through a table in SQLite that adheres to 3NF. I'm working on visualizing the graph. 

There's also a forked file from twint API which I used to build a rotating proxy. The purpose was to bypass twitter's temprorary IP bans for sending too many GET requests. It's currently working but unfinished as I'm working on getting it auto rotate free and working proxies. 
