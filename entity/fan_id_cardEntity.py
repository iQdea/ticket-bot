from entity.mongo import Mongo
from entity.personEntity import UsernameNotFoundError

class FanIDCardNotFoundError(Exception):
    pass


class FanIDCardEntity(Mongo):

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
        FanIDCardEntity.increase_balance(card_id, -value)

    @staticmethod
    def does_exist(card_id):
        result = Mongo.client.get_collection('fun_id_card').count_documents({"card_id" : card_id})
        return result > 0

    @staticmethod
    def insert(card):
        collection_name = Mongo.client.get_collection('fun_id_card')
        collection_name.insert_one({"card_id" : card.card_id,
                                    "username" : card.username,
                                    "expiration_date" : card.expiration_date,
                                    "balance" : card.balance, 
                                    "is_blocked" : card.is_blocked})

    @staticmethod
    def update(card):
        Mongo.client.get_collection('fun_id_card').update_one({"card_id" : card.card_id}, 
        {'$set':{"username" : card.username,
                "expiration_date" : card.expiration_date,
                "balance" : card.balance, 
                "is_blocked" : card.is_blocked}})

    @staticmethod
    def save(card):
        if FanIDCardEntity.does_exist(card.card_id):
            FanIDCardEntity.update(card)
        else:
            FanIDCardEntity.insert(card)

    @staticmethod
    def get_max_card_id():
        return Mongo.client.get_collection('fun_id_card').count_documents({})