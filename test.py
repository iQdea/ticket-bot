import hashlib

import numpy
from domain.customer import Customer
from domain.organizer import Organizer
from domain.terminal import Terminal
from entity.mongo import Mongo
from domain.seat import Seat
from domain.match import Match
from entity.ticketEntity import TicketEntity
from entity.matchesEntity import MatchEntity
from entity.personEntity import PersonEntity
from domain.ticket import SingleTicket, Ticket
from domain.fan_id_card import FanIDCard
import hashlib
import pymongo
import numpy as np
print(Mongo.client.get_collection('matches').count_documents({}))