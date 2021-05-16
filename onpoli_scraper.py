import tweepy
import sqlite3
import time
import datetime
import my_Oauth as Oauth


consumer_key = Oauth.consumer_key
consumer_secret = Oauth.consumer_secret
access_token = Oauth.access_token
access_token_secret = Oauth.secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
dbname = "onpoli_graph.db"
conn = sqlite3.connect(dbname)


def limit_handled(cursor):
    while True:
        try:
            yield next(cursor)
        except tweepy.RateLimitError:
            print("waiting")
            print("sleeping at ", datetime.datetime.now())
            time.sleep(15 * 60)

with conn:
    cursor = conn.cursor()
    scrape_list = [
        "DolyBegum",
        "Dalton_McGuinty"
    ]   

    comp_scrape = []
    n_reqs = 0
    counter = 0
    avg = 0
    f = lambda count: 1 if count % 5000 else 0

    ready_list = time.time()
    for i in scrape_list:
        print(i)
        user = api.get_user(str(i))
        x = user.followers_count
        n_reqs += (x // 5000) + f(x)
        try:         
            entry = (user.id, user.name, user.screen_name, user.followers_count,
                        user.friends_count, user.description, 
                        user.location, user.url, user.profile_image_url_https)
        except:
            entry = (user.id, user.name, user.screen_name, user.followers_count,
                        user.friends_count, user.description, 
                        "DNE", "DNE", user.profile_image_url_https)
        comp_scrape.append(entry)
    ready_list_end = time.time()

    f2 = lambda rest: 0 if rest <= 15 else rest // 15
    limits = f2(n_reqs) 
    aprox_min = limits * 15 + (n_reqs // 15 * 20 / 60)   
    print(f"""Aprox time is {aprox_min} minute(s), the amount
    of Twitter-api requests made are {n_reqs} """)
    time.sleep(5)

    init = ready_list - ready_list_end


    for entry in comp_scrape:
        start_scrape = time.time()
        int_id = entry[0] 
        query = "INSERT OR IGNORE INTO pillars values(?,?,?,?,?,?,?,?,?)"
        cursor.execute(query, entry)
        conn.commit()
        try:            
            for count, tw_id in enumerate(limit_handled(
                tweepy.Cursor(api.followers_ids, user_id=int_id).items())):
                    entry2 = (tw_id, datetime.datetime.now(), int_id)
                    query = f"INSERT OR IGNORE INTO mega_ids VALUES(?,?,?)"
                    cursor.execute(query, entry2)
                    conn.commit()
                    print("added---", count)
        except RuntimeError:
            counter += 1
            end_scrape = time.time()
            avg = (avg + end_scrape - start_scrape) / counter


    final = time.time()     
    a_time = ready_list - final 

    print(f"""Prediction was {aprox_min} minute(s) 
        of Twitter-api requests made are {n_reqs}""")

    print(f"""Actual time taken {a_time}, the average time for a request + storage is {avg}.""")




