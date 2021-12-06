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

# organizer = Organizer.construct("orgkom")
# match = Match(None, "Dor", "lla", "2021-03-10", organizer.username, "quarterfinal")
# organizer.add_match(match)
# # seats = Seat.get_seats()
# # cutomer = Customer.construct("mario")
# # ticket = SingleTicket(1, "NULL", 28.99, match, seats[0])
# # cutomer.buy_ticket(ticket)

print(numpy.arange(1, 2 + 1)[0])