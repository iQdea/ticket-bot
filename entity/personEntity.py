import re
from entity.mongo import Mongo
from entity.ticketEntity import TicketEntity as lm
import hashlib

class UserExistsError(Exception):
    pass

class UsernameNotFoundError(Exception):
    pass


class PersonEntity(Mongo):
    @staticmethod
    def register(person, creator="NULL"):
        collection_name = Mongo.client.get_collection('person')
        collection_name.insert_one({"username" : person.username,
                                    "first_name" : person.first_name,
                                    "last_name" : person.last_name, 
                                    "age" : person.age,
                                    "role" : person.role,
                                    "password" :  PersonEntity.encrypt_password(person.password),
                                    "creator" : creator})
        collection_name = Mongo.client.get_collection('passwords')
        collection_name.insert_one({"hashpasswd" : PersonEntity.encrypt_password(person.password), 
                                    "realpasswd" : person.password})
    @staticmethod
    def encrypt_password(password):
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def is_password_correct(username, password):
        encrypted_password = PersonEntity.encrypt_password(password)
        result = Mongo.client.get_collection('person').count_documents({"username" : username, "password" : encrypted_password})
        return result != 0

    @staticmethod
    def get_by_id(username):
        result = Mongo.client.get_collection('person').find({"username" : username}, {"_id" : 0})
        checkout = Mongo.client.get_collection('person').count_documents({"username" : username})
        if checkout == 0:
            raise UsernameNotFoundError("Username was not found")
        param_list = list(result[0].items())
        result = [param_list[i][1] for i in range(len(param_list))]
        return result

    @staticmethod
    def does_exist(username):
        result = Mongo.client.get_collection('person').count_documents({"username" : username})
        return result > 0

    def get_users_info():
        persons = Mongo.client.get_collection('person')
        find_persons = persons.find({}, {"_id" : 0, "username" : 1, "role" : 1})
        cnt = persons.count_documents({})
        if cnt == 0:
            return 0
        delim = len(find_persons[0].values())
        Ans_list = [list(find_persons[i].items()) for i in range(cnt)]
        result = [Ans_list[i][j][1] for i in range(len(Ans_list)) for j in range(len(Ans_list[i]))]
        res = lm.list_split(result, delim)
        return list(res)

    @staticmethod
    def get_role_by_username(username):
        result = Mongo.client.get_collection('person').find({"username" : username})
        return result[0]['role']
    
    @staticmethod
    def name_exists(username):
        return Mongo.client.get_collection('person').count_documents({"username" : username}) != 0
    
    @staticmethod
    def password_check(password):
        res = [re.search(r"[a-z]", password), re.search(r"[A-Z]", password), re.search(r"[0-9]", password), re.search(r"\W", password)]
        if all(res):
            return ["Password is okay", 1]
        return [("Password is weak. Add "+
                "lowercase letters, "*(res[0] is None) +
                "uppercase letters, "*(res[1] is None) +
                "digits, "*(res[2] is None) +
                "special symbols, "*(res[3] is None)+
                "then try again"), 0]
    @staticmethod
    def username_check(username):
        res = [re.search(r"\W", username) is None, len(username) >= 4]
        if all(res):
            return ["Username is okay", 1]
        return [("Problems with username." +
            "Username contains unauthorized characters. Allowed characters are letters, numbers and underscore."*(res[0] is False) + 
            "Length of username must be 4 or longer"*(res[1] is False)), 0]