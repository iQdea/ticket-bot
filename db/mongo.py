from pymongo import MongoClient
class Mongo:
    CONNECTION_STRING = "mongodb+srv://qdea:Narud20@footballbase.oeakp.mongodb.net/myFirstDatabase"
    client = MongoClient(CONNECTION_STRING)['TicketTerminal']
    dbname = client
    if len(client.collection_names()) == 0:
        client.create_collection('person')
        client.create_collection('matches')
        client.create_collection('ticket')
        client.create_collection('fun_id_card')
        collection_name = dbname.get_collection('person')
        person_list = [ 
        {"username" : "mario","first_name" : "Mario","last_name" : "Martinez","age" : 25,"role" : "customer", "password" : "202cb962ac59075b964b07152d234b70", "creator" : "NULL"},
        {"username" : "terminal","first_name" : "Football","last_name" : "system","age" : 18,"role" : "terminal", "password" : "63a9f0ea7bb98050796b649e85481845", "creator" : "NULL"},
        ]
        collection_name.delete_many({})
        collection_name.insert_many(person_list)
        collection_name = dbname.get_collection('matches')
        collection_name.delete_many({})
        matches_list = [
        {"match_id" : 3,"host" : "Barselona","guest" : "Juventus","match_date" : "2020-12-08","organizer" : "cristian","match_type" : "group"},
        {"match_id" : 2,"host" : "Bars","guest" : "Juv","match_date" : "2020-12-09","organizer" : "cris","match_type" : "group"}
        ]
        collection_name.insert_many(matches_list)
        collection_name = dbname.get_collection('ticket')
        collection_name.delete_many({})
        tickets_list = [
        {"ticket_id" : 1,"card_id" : "NULL","price" : 50.99,"match_id" : 2,"block" : "1","row" : "1","place" : "1"},
        {"ticket_id" : 2,"card_id" : "NULL","price" : 40.99,"match_id" : 2,"block" : "1","row" : "1","place" : "2"}
        ]
        collection_name.insert_many(tickets_list)
        fun_id_cards = [
        {"card_id" : 1,"username" : 'mario',"expiration_date" : '2022-10-10',"balance" : 1000.0,"is_blocked" : False}
        ]
        collection_name = dbname.get_collection('fun_id_card')
        collection_name.delete_many({})
        collection_name.insert_many(fun_id_cards)
    