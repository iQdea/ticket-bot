import telebot
import datetime
from db.matchesDB import MatchDB
from db.personDB import PersonDB
from db.ticketDB import TicketDB
from domain.terminal import Terminal, UserAlreadyExistsError, IncorrectInputFormat
from domain.customer import Customer, TicketDoesNotBelongToCustomerError, CustomerDoesNotExistError
from domain.fan_id_card import FanIDCard, NotEnoughMoneyError
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
        user_markup.row("Show info")
        user_markup.row("Register new customer")
        user_markup.row("Login")
        user_markup.row("Show matches")
        user_markup.row("Continue")
    else:
        user_markup.row("Show info")
        if user.role == "customer":
            user_markup.row("Show tickets")
            user_markup.row("Add balance")
            user_markup.row("Show matches")
            user_markup.row("Buy ticket", "Return ticket")
        elif user.role == "terminal":
            user_markup.row("Block Fan ID Card", "Unblock Fan ID Card")
        elif user.role == "organizer":
            user_markup.row("Add match", "Update match")
            user_markup.row("Delete match", "Cancel match")
        user_markup.row("My credentials")
        user_markup.row("Logout")
        user_markup.row("Confirm logout")
        user_markup.row("Continue")
    bot.send_message(message.chat.id, "Choose command", reply_markup=user_markup)

@bot.message_handler(regexp="Show info")
def show_info(message):
    if not user.authenticated:
        bot.send_message(message.chat.id, "Hello, friend! I am Football-Seller-bot.\n\n" 
        + "Press <<Login>> if you have account or <<Register new customer>> if you haven't yet.\n\n"
        + "Also you can press <<Show matches>> to see available matches."
        + "<<Continue>> is botton to get to user menu page after you succesfully log in")
    else:
        if user.role == "customer":
            bot.send_message(message.chat.id, "Press <<Show tickets>> to see your tickets\n\n" 
            + "Press <<Add balance>> to send money to your fan_id_card.\n\n"
            + "Press <<Show matches>> to see available matches.\n\n"
            + "Press <<Buy ticket>> to purchase ticket.\n\n"
            + "Press <<Return tciket>> to return ticket and get your money back. Warning!!! You will get 90 percents of ticket price\n\n"
            + "Press <<My credentials>> to see your account information\n\n"
            + "Press <<Logout>> to be logged out\n\n"
            + "<<Confirm logout>> and <<Continue>> are bottons to get to start page after you press <<Logout>>")
        elif user.role == "terminal":
            bot.send_message(message.chat.id, "Press <<Block Fan ID Card>> to block someone.\n\n"
            + "Press <<Unblock Fan ID Card>> to unblock user who has been blocket yet.\n\n"
            + "Press <<My credentials>> to see your account information\n\n"
            + "Press <<Logout>> to be logged out\n\n"
            + "<<Confirm logout>> and <<Continue>> are bottons to get to start page after you press <<Logout>>")
        else:
            bot.send_message(message.chat.id, "Press <<Add Match>> to create new match in system\n\n" 
            + "Press <<Update Match>> to update info about match in system\n\n"
            + "Press <<Delete Match>> to remove match from system after canceling\n\n"
            + "Press <<Cancel Match>> to cancel match in system\n\n"
            + "Press <<My credentials>> to see your account information\n\n"
            + "Press <<Logout>> to be logged out\n\n"
            + "<<Confirm logout>> and <<Continue>> are bottons to get to start page after you press <<Logout>>")



@bot.message_handler(regexp="Show matches")
def show_matches(message):
    matches = get_matches()
    send(message, matches if matches != 0 else "There are no available matches")


def get_matches():
    result = MatchDB.get_matches()
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
    send(message, "You sure to be logged out? If yes, press <<Confirm logout>>", answer)

def answer(message):
    send(message, "You have been logged out, press <<Continue>>", show)

@bot.message_handler(regexp="Login")
def login(message):
    if not user.authenticated:
        send(message, "Enter your username", enter_username)

def enter_username(message):
    username = message.text
    if PersonDB.does_exist(username):
        user.username = username
        send(message, "Enter your password", enter_password)
    else:
        send(message, "The entered username does not exist. Enter the username again", enter_username)

def enter_password(message):
    password = message.text
    if PersonDB.is_password_correct(user.username, password):
        user.password = password
        user.authenticated = True
        user.role = PersonDB.get_role_by_username(user.username)
        print(user.username, user.password, user.role)
        if user.role == "customer":
            try:
                user.person = Customer.construct(user.username)
                send(message, "You have been successfully logged in, press <<Continue>>", show)
            except:
                send(message, "User wasn't found. Check if you have your fun_id_card")
        elif user.role == "terminal":
            try:
                user.person = Terminal.construct(user.username)
                send(message, "You have been successfully logged in, press <<Continue>>", show)
            except:
                send(message, "User wasn't found. Check if you have all credentials to login")
        elif user.role == "organizer":
            try:
                user.person = Organizer.construct(user.username)
                send(message, "You have been successfully logged in, press <<Continue>>", show)
            except:
                send(message, "User wasn't found. Check if you have all credentials to login")
    else:
        send(message, "The entered password is wrong. Enter correct username and password again", enter_username)

@bot.message_handler(regexp="Show tickets")
def show_tickets(message):
    if user.role == "customer":
        try:
            tickets = get_tickets()
            send(message,tickets) 
        except:
            send(message,"You do not have any tickets")


def get_tickets():
    card_id = user.person.fan_id_card
    result = TicketDB.get_tickets_id_by_card_id(card_id.card_id)
    tickets = ""
    for row in result:
        ticket_id = row[0]
        match_id = row[1]
        tickets += str(SingleTicket.construct(ticket_id, match_id)) + "\n\n"
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

@bot.message_handler(regexp="Buy ticket")
def buy_ticket(message):
    if user.role == "customer":
        if user.person.is_blocked():
            send(message, "Your Fan ID Card is blocked")
        else:
            matches = get_matches()
            if matches == "":
                send(message, "There are no available matches")
            else:
                tickets_exist = MatchDB.get_tickets_cnt()
                if tickets_exist > 0:
                    send(message, "Enter match ID you would like to attend")
                    send(message, matches, enter_match_id_to_buy_ticket)
                else:
                    send(message, "There are no tickets at all. Come back later")
                    return



def enter_match_id_to_buy_ticket(message):
    global match_id
    try:
        match_id = int(message.text)
        if not MatchDB.does_exist(match_id):
            send(message, "The entered match id does not exist. Please enter the match id again", enter_match_id_to_buy_ticket)
            return
        try:
            available_seats = get_available_seats(match_id)
            send(message, "Choose an available seat for this match. Your balance: ${}".format(round(user.person.fan_id_card.balance, 2)))
            send(message, available_seats, choose_seat)
        except:
            send(message, "There are no available seats for this match. Please choose another match", enter_match_id_to_buy_ticket)
            return
    except ValueError:
        send(message, "Match ID must be an integer. Please enter the match id again", enter_match_id_to_buy_ticket)
def choose_seat(message):
    try:
        ticket_id = int(message.text)
        if not TicketDB.does_exist(ticket_id):
            send(message, "The entered ID does not exist. Please enter the ID again", choose_seat)
            return
        ticket = TicketDB.get_by_id(ticket_id, match_id)
        user.person.buy_ticket(ticket)
        send(message, "The seat and ticket were successfully reserved. Balance: ${}".format(round(user.person.fan_id_card.balance, 2)))
    except ValueError:
        send(message, "You should enter an ID for choosing a seat. Please enter the ID again", choose_seat)
    except NotEnoughMoneyError as error:
        send(message, str(error))
        return



def get_available_seats(match_id):
    result = TicketDB.get_available_tickets_id_and_seats_and_price(match_id)
    ans = []
    tickets_id_and_seats_and_prices = ""
    for row in result:
        tickets_id_and_seats_and_prices += str(row[0]) + ": " + str(Seat(row[2], row[3], row[4])) + ". Price: ${}\n".format(row[1])
        ans.append([row[0], row[2], row[3], row[4], row[1]])
    return tickets_id_and_seats_and_prices
    
@bot.message_handler(regexp="Return ticket")
def return_ticket(message):
    if user.role == "customer":
        if user.person.is_blocked():
            send(message, "Your Fan ID Card is blocked")
        else:
            tickets = get_tickets()
            if tickets == "":
                send(message, "You do not have any tickets")
            else:
                send(message, "Enter ticket ID you would like to return")
                send(message, tickets, enter_ticket_id_to_return)


def enter_ticket_id_to_return(message):
    try:
        card_id = user.person.fan_id_card
        result = TicketDB.get_tickets_id_by_card_id(card_id.card_id)
        ticket_id = int(message.text)
        cnt = 0
        for row in result:
            if row[0] == ticket_id:
                cnt += 1
        for row in result:
            if cnt > 1:
                send(message, "There are losts of matches with same ID")
                return
            ticket_id = row[0]
            match_id = row[1]
            ticket = TicketDB.get_by_id(ticket_id, match_id)
            user.person.return_ticket(ticket)
            send(message, "Ticket {} was successfully returned. Balance: ${}".format(ticket_id, round(user.person.fan_id_card.balance, 2)))
            return
    except ValueError:
        send(message, "Ticket ID must be an integer. Please enter the ticket ID again", enter_ticket_id_to_return)
    except TicketDoesNotExistError:
        send(message, "The entered ticket ID does not exist. Please enter the ticket ID again", enter_ticket_id_to_return)
    except TicketDoesNotBelongToCustomerError:
        send(message, "Entered ticket ID does not belong to you. Please enter another ticket ID", enter_ticket_id_to_return)

@bot.message_handler(regexp="Register new customer")
def register_new_customer(message):
    if user.role == "terminal" or not user.authenticated:
        global new_customer
        new_customer = NewCustomer()
        send(message, "Enter username", enter_new_username)


def enter_new_username(message):
    new_customer.username = message.text
    send(message, "Enter age", enter_age)


def enter_age(message):
    try:
        new_customer.age = int(message.text)
        if new_customer.age < 12:
            send(message, "The minimum age must be at least 12")
        else:
            send(message, "Enter first name", enter_first_name)
    except ValueError:
        send(message, "Age must be an integer. Please enter the age again in the correct format", enter_age)


def enter_first_name(message):
    new_customer.first_name = message.text
    send(message, "Enter last name", enter_last_name)


def enter_last_name(message):
    new_customer.last_name = message.text
    send(message, "Enter password", enter_password_of_customer)

def enter_password_of_customer(message):
    new_customer.password = message.text
    customer = Customer(new_customer.username, new_customer.first_name, new_customer.last_name, new_customer.age, "customer", new_customer.password, "NULL", None)
    try:
        if not user.person == None:
            PersonDB.register(customer, creator="terminal")
            FanIDCard.create(customer.username)
        else:
            PersonDB.register(customer, creator="terminal")
            FanIDCard.create(customer.username)
        send(message, "The customer was successfully registered".format(customer.username))
        send(message, "Username: {}\nPassword: {}".format(customer.username, customer.password))
    except IncorrectInputFormat as error:
        send(message, error)
    except UserAlreadyExistsError as error:
        send(message, error)


@bot.message_handler(regexp="Unblock Fan ID Card")
def unblock_fan_id_card(message):
    if user.role == "terminal":
        send(message, "Enter Fan ID Card holder's username you would like to unblock", enter_username_to_unblock)


def enter_username_to_unblock(message):
    username = message.text
    try:
        customer = Customer.construct(username)
        user.person.unblock_fan_id_card(customer)
        send(message, "The Fan ID Card {} was successfully unblocked".format(customer.fan_id_card.id))
    except CustomerDoesNotExistError:
        send(message, "Customer with username \"{}\" does not exist. Please enter the username again".format(username), enter_username_to_unblock)


@bot.message_handler(regexp="Block Fan ID Card")
def block_fan_id_card(message):
    if user.role == "terminal":
        send(message, "Enter Fan ID Card holder's username you would like to block", enter_username_to_block)


def enter_username_to_block(message):
    username = message.text
    try:
        customer = Customer.construct(username)
        user.person.block_fan_id_card(customer)
        send(message, "The Fan ID Card {} was successfully blocked".format(customer.fan_id_card.id))
    except CustomerDoesNotExistError:
        send(message, "Customer with username \"{}\" does not exist. Please enter the username again".format(username), enter_username_to_block)

@bot.message_handler(regexp="Add match")
def add_match(message):
    if user.role == "organizer":
        global new_match
        new_match = NewMatch()
        send(message, "Enter host team", enter_host_team)


def enter_host_team(message):
    new_match.host_team = message.text
    send(message, "Enter guest team", enter_guest_team)


def enter_guest_team(message):
    new_match.guest_team = message.text
    send(message, "Enter match date in format YYYY-MM-DD", enter_match_date)


def is_valid_date(datestring):
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def enter_match_date(message):
    new_match.date = message.text
    if not is_valid_date(new_match.date):
        send(message, "The entered date is not in the format YYYY-MM-DD. Please enter the match date again in the correct format", enter_match_date)
        return
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("Group")
    user_markup.row("Quarterfinal")
    user_markup.row("Semifinal")
    user_markup.row("Final")
    user_markup.row("Continue")
    sent = bot.send_message(message.chat.id, "Choose match type", reply_markup=user_markup)
    bot.register_next_step_handler(sent, enter_match_type)


def enter_match_type(message):
    match_type = message.text
    if not (match_type == "Group" or match_type == "Quarterfinal" or match_type == "Semifinal" or match_type == "Final"):
        send(message, "\"{}\" does not exist as a match type. Please enter the match type again".format(match_type), enter_match_type)
        return
    new_match.match_type = match_type
    match = Match(None, new_match.host_team, new_match.guest_team, new_match.date, user.person.username, new_match.match_type)
    user.person.add_match(match)
    send(message, "The match {} between {} and {} was successfully added".format(match.id, match.host_team, match.guest_team) + "press <<Continue>>", show)



bot.polling()