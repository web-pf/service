import pymongo


def check_counters(names=[]):
    for name in names:
        counter = client['web_pf']['counters'].find_one({
            "_id": name
        })
        if not counter:
            client['web_pf']['counters'].insert_one({
                "_id": name,
                "seq": 0
            })


client = pymongo.MongoClient(host='localhost', port=27017)

check_counters(['userId', 'websiteId'])
