import hashlib

import numpy
from domain.customer import Customer
from domain.organizer import Organizer
from db.mongo import Mongo
from domain.seat import Seat
from domain.match import Match
from db.ticketDB import TicketDB
from db.matchesDB import MatchDB
from db.personDB import PersonDB
from domain.ticket import SingleTicket, Ticket
from domain.fan_id_card import FanIDCard
import hashlib
import pymongo

string_l = "2022-10-08"

real_date = "2023-10-07"


res = Mongo.client.get_collection('matches').count_documents({"match_date" : {"$gt" : string_l}})
print(res)