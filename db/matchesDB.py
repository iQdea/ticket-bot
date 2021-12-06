import pymongo
from db.mongo import Mongo
from db.ticketDB import TicketDB as lm

class MatchNotFoundError(Exception):
    pass

class MatchDB(Mongo):

    @staticmethod
    def add_match(match):
        collection_name = Mongo.client.get_collection('matches')
        collection_name.insert_one({"match_id" : match.id,
                                    "host" : match.host_team,
                                    "guest" : match.guest_team,
                                    "match_date" : match.date, 
                                    "organizer" : match.organizer,
                                    "match_type" : match.match_type})
        return MatchDB.get_max_match_id()
    @staticmethod
    def update_match(match):
        Mongo.client.get_collection('matches').update_one({"match_id" : match.id}, 
        {'$set':{"host" : match.host_team,
                "guest" : match.guest_team,
                "match_date" : match.date, 
                "organizer" : match.organizer,
                "match_type" : match.match_type}})

    @staticmethod
    def delete_match(match_id):
        Mongo.client.get_collection('matches').delete_one({"match_id" : match_id})

    @staticmethod
    def get_by_id(match_id):
        result = Mongo.client.get_collection('matches').find({"match_id" : match_id}, {"_id" : 0})
        checkout = Mongo.client.get_collection('matches').count_documents({"match_id" : match_id})
        if checkout == 0:
            raise MatchNotFoundError("Match was not found")
        param_list = list(result[0].items())
        result = [param_list[i][1] for i in range(len(param_list))]
        return result


    @staticmethod
    def get_matches():
        matches = Mongo.client.get_collection('matches')
        find_matches = matches.find({}, {"_id" : 0}).sort('match_id', pymongo.DESCENDING)
        cnt = matches.count_documents({})
        if cnt == 0:
            return 0
        delim = len(find_matches[0].values())
        Ans_list = [list(find_matches[i].items()) for i in range(cnt)]
        result = [Ans_list[i][j][1] for i in range(len(Ans_list)) for j in range(len(Ans_list[i]))]
        res = lm.list_split(result, delim)
        return list(res)

    @staticmethod
    def does_exist(match_id):
        result = Mongo.client.get_collection('matches').count_documents({"match_id" : match_id})
        return result > 0

    @staticmethod
    def get_max_match_id():
        return Mongo.client.get_collection('matches').find({}, {"_id" : 0}).sort('match_id', pymongo.DESCENDING)[0]['match_id']

    @staticmethod
    def get_tickets_cnt():
        A = []
        cnt = 0
        for i in MatchDB.get_matches():
            A.append(i[0])
        for j in A:
            ticket = Mongo.client.get_collection('ticket')
            find_ticket = ticket.find({"match_id" : j, "card_id" : "NULL"}, {"ticket_id" : 1, "price" : 1, "block": 1, 'row': 1, 'place': 1, "_id" : 0}).sort('ticket_id', pymongo.ASCENDING)
            cnt += len(list(find_ticket))
        return cnt