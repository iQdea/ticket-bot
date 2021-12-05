from db.mongo import Mongo
from db.personDB import UsernameNotFoundError
import pymongo

class FanIDCardNotFoundError(Exception):
    pass


class FanIDCardDB(Mongo):

    @staticmethod
    def get_by_id(card_id):
        result = Mongo.client.get_collection('fun_id_card').find({"card_id" : card_id}, {"_id" : 0})
        checkout = Mongo.client.get_collection('fun_id_card').count_documents({"card_id" : card_id})
        if checkout == 0:
            raise FanIDCardNotFoundError("Fan ID Card {} does not exist".format(card_id))
        param_list = list(result[0].items())
        result = [param_list[i][1] for i in range(len(param_list))]
        return result

    @staticmethod
    def get_card_by_username(username):
        result = Mongo.client.get_collection('fun_id_card').find({"username" : username}, {"_id" : 0})
        checkout = Mongo.client.get_collection('fun_id_card').count_documents({"username" : username})
        if checkout == 0:
            raise UsernameNotFoundError("Username {} was not found in the system".format(username))
        param_list = list(result[0].items())
        result = [param_list[i][1] for i in range(len(param_list))]
        return result

    @staticmethod
    def increase_balance(card_id, value):
        existing = Mongo.client.get_collection('fun_id_card').find_one({"card_id" : card_id})['balance']
        Mongo.client.get_collection('fun_id_card').update_one({"card_id" : card_id}, 
        {'$set':{"balance" : existing + value,
                }})

    @staticmethod
    def reduce_balance(card_id, value):
        FanIDCardDB.increase_balance(card_id, -value)

    @staticmethod
    def does_exist(card_id):
        result = Mongo.client.get_collection('fun_id_card').count_documents({"card_id" : card_id})
        return result > 0

    @staticmethod
    def insert(card):
        collection_name = Mongo.client.get_collection('fun_id_card')
        collection_name.insert_one({"card_id" : card.id,
                                    "username" : card.username,
                                    "expiration_date" : card.expiration_date,
                                    "balance" : card.balance, 
                                    "is_blocked" : card.is_blocked})

    @staticmethod
    def update(card):
        Mongo.client.get_collection('fun_id_card').update_one({"card_id" : card.id}, 
        {'$set':{"username" : card.username,
                "expiration_date" : card.expiration_date,
                "balance" : card.balance, 
                "is_blocked" : card.is_blocked}})

    @staticmethod
    def save(card):
        if FanIDCardDB.does_exist(card.id):
            FanIDCardDB.update(card)
        else:
            FanIDCardDB.insert(card)

    @staticmethod
    def get_max_card_id():
        return Mongo.client.get_collection('fun_id_card').find({}, {"_id" : 0}).sort('card_id', pymongo.DESCENDING)[0]['card_id']