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

customer = Customer.construct("mario")
organizer = Organizer.construct("orgkom")
terminal = Terminal.construct("terminal")

# match = Match(None, "Dortmund", "Sevilla", "2021-03-10", organizer.username, "quarterfinal")
# organizer.add_match(match)

# new_customer = Customer("alexis", "alexis", "sanchez", 29, None, "Naref", "terminal", None)
# terminal.register(new_customer)

def encrypt_password(password):
    return hashlib.md5(password.encode()).hexdigest()


print(encrypt_password("Naref"))