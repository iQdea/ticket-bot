from pymongo import MongoClient
class Mongo:
    CONNECTION_STRING = "mongodb+srv://qdea:Narud20@footballbase.oeakp.mongodb.net/myFirstDatabase"
    client = MongoClient(CONNECTION_STRING)['TicketTerminal']
    def reset(client=client):
        for i in client.list_collection_names():
            collection_name = client.get_collection(i)
            collection_name.delete_many({})
            if i == 'person':
                collection_name.insert_one({
                "username" : "terminal",
                "first_name" : "Football",
                "last_name" : "system",
                "age" : 18,
                "role" : "terminal",
                "password" : "63a9f0ea7bb98050796b649e85481845", 
                "creator" : "NULL"})