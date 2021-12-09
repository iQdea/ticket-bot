import hashlib

import numpy
from domain.customer import Customer
from domain.organizer import Organizer
from domain.terminal import Terminal
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
import numpy as np
persons = Mongo.client.get_collection('person')
find_persons = persons.find({}, {"_id" : 0})
cnt = persons.count_documents({})
delim = len(find_persons[0].values())
Ans_list = [list(find_persons[i].items()) for i in range(cnt)]
result = [Ans_list[i][j][1] for i in range(len(Ans_list)) for j in range(len(Ans_list[i]))]
res = list(TicketDB.list_split(result, delim))
