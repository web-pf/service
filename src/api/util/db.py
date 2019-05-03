def get_next_seq(col, name):
    return col.find_and_modify(query={
        "_id": name
    }, update={
        "$inc": {
            "seq": 1
        }
    })['seq']
