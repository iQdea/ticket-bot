import telebot
import datetime
from db.matches_db import Match_db
from db.person_db import Person_db
from db.ticket_db import Ticket_db
from domain.terminal import Terminal, UserAlreadyExistsError, IncorrectInputFormat
from domain.customer import Customer, TicketDoesNotBelongToCustomerError, CustomerDoesNotExistError
from domain.fan_id_card import NotEnoughMoneyError
from domain.match import Match, MatchDoesNotExistError
from domain.organizer import Organizer
from domain.seat import Seat
from domain.ticket import SingleTicket, Ticket, TicketDoesNotExistError

token = "2130797376:AAENz9nRcdRj0GiHnnzFOOQvY8XSpvTEzfs"
bot = telebot.TeleBot(token)

class CurrentUser:
    def __init__(self):
        self.authenticated = False
        self.username = self.password = self.operation = self.role = self.person = None

class NewCustomer:
    def __init__(self):
        self.username = self.age = self.first_name = self.last_name = None

class NewMatch:
    def __init__(self):
        self.host_team = self.guest_team = self.date = self.match_type = None

user = CurrentUser()
new_customer = None
new_match = None
match = None

def send(message, text, next_handler=None):
    sent = bot.send_message(message.chat.id, text)
    if next_handler is not None:
        bot.register_next_step_handler(sent, next_handler)

@bot.message_handler(commands=["start"], regexp="start")
def show(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if not user.authenticated:
        user_markup.row("Login")
    else:
        if user.role == "customer":
            user_markup.row("Show tickets")
            user_markup.row("Add balance")
            user_markup.row("Buy ticket", "Return ticket")
        elif user.role == "cashier":
            user_markup.row("Register new customer")
            user_markup.row("Block Fan ID Card", "Unblock Fan ID Card")
        elif user.role == "organizer":
            user_markup.row("Add match", "Update match")
            user_markup.row("Delete match", "Cancel match")
        user_markup.row("My credentials")
        user_markup.row("Logout")
    user_markup.row("Show matches")
    bot.send_message(message.chat.id, "Choose command", reply_markup=user_markup)

@bot.message_handler(regexp="Show matches")
def show_matches(message):
    matches = get_matches()
    send(message, matches if matches != "" else "There are no available matches")


def get_matches():
    result = Match_db.get_matches()
    matches = ""
    for row in result:
        matches += str(Match(*row)) + "\n\n"
    return matches


@bot.message_handler(regexp="My credentials")
def show_credentials(message):
    send(message, str(user.person))


@bot.message_handler(regexp="Logout")
def logout(message):
    user.authenticated = False
    user.role = ""
    send(message, "You have been logged out", show)


@bot.message_handler(regexp="Login")
def login(message):
    if not user.authenticated:
        send(message, "Enter your username", enter_username)

def enter_username(message):
    username = message.text
    if Person_db.does_exist(username):
        user.username = username
        send(message, "Enter your password", enter_password)
    else:
        send(message, "The entered username does not exist. Enter the username again", enter_username)

def enter_password(message):
    password = message.text
    if Person_db.is_password_correct(user.username, password):
        user.password = password
        user.authenticated = True
        user.role = Person_db.get_role_by_username(user.username)
        print(user.username, user.password, user.role)
        if user.role == "customer":
            try:
                user.person = Customer.construct(user.username)
                send(message, "You have been successfully logged in")
            except:
                send(message, "User wasn't found. Check if you have your fun_id_card")
        elif user.role == "cashier":
            try:
                user.person = Terminal.construct(user.username)
                send(message, "You have been successfully logged in")
            except:
                send(message, "User wasn't found. Check if you have all credentials to login")
        elif user.role == "organizer":
            try:
                user.person = Organizer.construct(user.username)
                send(message, "You have been successfully logged in")
            except:
                send(message, "User wasn't found. Check if you have all credentials to login")
    else:
        send(message, "The entered password is wrong. Enter correct username and password again", enter_username)

@bot.message_handler(regexp="Show tickets")
def show_tickets(message):
    if user.role == "customer":
        tickets = get_tickets()
        send(message, tickets if tickets != "" else "You do not have any tickets")


def get_tickets():
    card_id = user.person.fan_id_card
    result = Ticket_db.get_tickets_id_by_card_id(card_id.id)
    tickets = ""
    for row in result:
        ticket_id = row[0]
        tickets += str(SingleTicket.construct(ticket_id)) + "\n\n"
    return tickets


@bot.message_handler(regexp="Add balance")
def add_balance(message):
    if user.role == "customer":
        if user.person.is_blocked():
            send(message, "Your Fan ID Card is blocked")
        else:
            send(message, "Your current balance: ${}\nEnter the value you would like to increase your balance".format(round(user.person.fan_id_card.balance, 2)), enter_value)


def enter_value(message):
    try:
        value = round(float(message.text), 2)
        if value <= 0:
            send(message, "The value in $ can only be positive. Please enter the value again", enter_value)
            return
        user.person.increase_balance(value)
        send(message, "Your balance was increased and now equals ${}".format(round(user.person.fan_id_card.balance, 2)))
    except ValueError:
        send(message, "Wrong input format. You should enter the value in $. Please enter the value again", enter_value)

bot.polling()