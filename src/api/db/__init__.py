import pymongo


def check_counter():
    return client['web_pf']['counters'].find_one({
        "_id": "userId"
    })


def init_db():
    if check_counter():
        return
    else:
        client['web_pf']['counters'].insert_many([{
            "_id": 'websiteId',
            "seq": 2
        }, {
            "_id": 'userId',
            "seq": 2
        }])
        client['web_pf']['inv_codes'].insert_one({
            "code": "BETAPLAN",
            "remaining": 9999
        })
        client['web_pf']['websites'].insert_one({
            "websiteId": 1, "uid": 1, "url": "https://webpf.net", "name": "WebPF Monitoring Platform", "description": "This is the official monitor of webpf.net, providing an example for web app developers.", "appId": "platform"
        })
        client['web_pf']['users'].insert_one({
            "uid": 1, "email": "guest@webpf.net", "nickname": "guest", "used_inv_code": "GUEST", "passwords": "pbkdf2:sha256:50000$uCHbJvCE$b61b8967bde811b1add7381f41891212c56f157e1faaf9d4e9aa9e5211f2b627", "privilegeCode": 0
        })


client = pymongo.MongoClient(host='localhost', port=27017)
init_db()
