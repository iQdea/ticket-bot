from db.mongo import Mongo
from domain.seat import Seat
from domain.match import Match
from db.ticketDB import TicketDB
from db.matchesDB import MatchDB
import pymongo
ticket_id = 1
result = Mongo.client.get_collection('ticket').update_one({"ticket_id" : ticket_id, "card_id" : "NULL"}, {'$set':{"card_id" : 2}})
print(result.modified_count)