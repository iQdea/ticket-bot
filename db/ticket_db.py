from db.mongo import Mongo
import pymongo
class TicketNotFoundError(Exception):
    pass
class Ticket_db(Mongo):

    @staticmethod
    def add_ticket(ticket, card_id):
        seat = ticket.seat
        collection_name = Mongo.client.get_collection('ticket')
        collection_name.insert_one({"ticket_id" : ticket.id,
                                    "card_id" : card_id,
                                    "price" : ticket.price,
                                    "match_id" : ticket.match.id,
                                    "block" : seat.block, 
                                    "row" : seat.row,
                                    "place" : seat.place})

    @staticmethod
    def get_by_id(ticket_id):
        result = Mongo.client.get_collection('ticket').find({"ticket_id" : ticket_id}, {"_id" : 0})
        checkout = Mongo.client.get_collection('ticket').count_documents({"ticket_id" : ticket_id})
        if checkout == 0:
            raise TicketNotFoundError("Ticket was not found")
        param_list = list(result[0].items())
        result = [param_list[i][1] for i in range(len(param_list))]
        return result

    @staticmethod
    def does_exist(ticket_id):
        result = Mongo.client.get_collection('ticket').count_documents({"ticket_id" : ticket_id})
        return result > 0


    @staticmethod
    def get_tickets_id_by_card_id(card_id):
        tickets = Mongo.client.get_collection('ticket')
        find_tickets = tickets.find({"card_id" : card_id}, {"_id" : 0, "ticket_id" : 1}).sort('ticket_id', pymongo.ASCENDING)
        cnt = tickets.count_documents({"card_id" : card_id})
        delim = len(find_tickets[0].values())
        Ans_list = [list(find_tickets[i].items()) for i in range(cnt)]
        result = [Ans_list[i][j][1] for i in range(len(Ans_list)) for j in range(len(Ans_list[i]))]
        res = Ticket_db.list_split(result, delim)
        return list(res)

    @staticmethod
    def get_available_tickets_id_and_seats_and_price(match_id):
        ticket = Mongo.client.get_collection('ticket')
        find_ticket = ticket.find({"match_id" : match_id, "card_id" : "NULL"}, {"ticket_id" : 1, "price" : 1, "block": 1, 'row': 1, 'place': 1, "_id" : 0})
        res = find_ticket.sort('ticket_id', pymongo.ASCENDING)
        return list(res)

    @staticmethod
    def reserve_ticket(ticket_id, card_id):
        Mongo.client.get_collection('ticket').update_one({"ticket_id" : ticket_id}, {'$set':{"card_id" : card_id}})

    @staticmethod
    def return_ticket(ticket_id):
        Mongo.client.get_collection('ticket').update_one({"ticket_id" : ticket_id}, {'$set':{"card_id" : "NULL"}})

    @staticmethod
    def delete_tickets_by_match_id(match_id):
        Mongo.client.get_collection('ticket').delete_many({"match_id" : match_id})

    @staticmethod
    def list_split(src_list, length):
            for i in range(0, len(src_list), length):
                yield src_list[i:i+length]

    @staticmethod
    def get_paid_money(match_id):
        ticket = Mongo.client.get_collection('ticket')
        find_ticket = ticket.find({"match_id" : match_id}, {"_id" : 0, "card_id" : 1, "price": 1})
        cnt = ticket.count_documents({"match_id" : match_id})
        Ans_list = [list(find_ticket[i].items()) for i in range(cnt)]
        result = [Ans_list[i][j][1] for i in range(len(Ans_list)) for j in range(len(Ans_list[i]))]
        res = Ticket_db.list_split(result, 2)
        return list(res)