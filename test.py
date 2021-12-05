import hashlib
from db.mongo import Mongo
from domain.seat import Seat
from domain.match import Match
from db.ticketDB import TicketDB
from db.matchesDB import MatchDB
from db.personDB import PersonDB
import hashlib
import pymongo
password = "Narud"
res = hashlib.md5("OOP".encode()).hexdigest()
print(res)
print("ce4195da808656beae0c97fed9194192")
# result = Mongo.client.get_collection('person').find({"username" : username, "password" : encrypted_password})
# print(list(result))