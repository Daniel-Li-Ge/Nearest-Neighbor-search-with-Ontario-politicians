import sqlite3

dbname = "onpoli_graph.db"
conn = sqlite3.connect(dbname)

with conn:
    cursor = cursor = conn.cursor()
    mega = """
        CREATE TABLE IF NOT EXISTS
            mega_ids(
                id interger NOT NULL,
                time_added text NOT NULL,
                following INTERGER NOT NULL,
                CONSTRAINT users_pk PRIMARY KEY (id, time_added)
                CONSTRAINT following_fk FOREIGN KEY(following) REFERENCES pillars(id)               
            );
        """
    
    pillars = """
        CREATE TABLE IF NOT EXISTS
            pillars(
                id INTEGER NOT NULL,
                name TEXT NOT NULL,
                handle TEXT NOT NULL, 
                followers_count INTEGER NOT NULL,
                following_count INTEGER NOT NULL, 
                bio TEXT,
                location TEXT,
                pf_url TEXT NOT NULL,
                pfp_url TEXT NOT NULL, 
                CONSTRAINT users_pk PRIMARY KEY (id)
            );
        """
    jaccard = """
        CREATE TABLE IF NOT EXISTS
            jaccard_edge(
                node INTEGER NOT NULL,
                node2 INTEGER NOT NULL,
                jaccard_index REAL NOT NULL,
                CONSTRAINT node_pk PRIMARY KEY (node, node2)
                CONSTRAINT node_fk FOREIGN KEY (node) REFERENCES pillars(id)
            );
        """
    follower_intersect = """
        CREATE TABLE IF NOT EXISTS
            follower_intersect(
                node INTEGER NOT NULL,
                node2 INTEGER NOT NULL,
                f_intersect INTEGER NOT NULL,
                CONSTRAINT node_pk PRIMARY KEY (node, node2)
                CONSTRAINT node_fk FOREIGN KEY (node) REFERENCES pillars(id)
            );
        """
    cursor.execute(jaccard)
    cursor.execute(follower_intersect)
    # cursor.execute(mega)
    # cursor.execute(pillars) 
