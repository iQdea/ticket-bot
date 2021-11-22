from db.mongo import Mongo
import hashlib

class UserExistsError(Exception):
    pass

class UsernameNotFoundError(Exception):
    pass


class Person_db(Mongo):
    @staticmethod
    def register(person, creator="NULL"):
        collection_name = Mongo.client.get_collection('person')
        collection_name.insert_one({"username" : person.username,
                                    "first_name" : person.first_name,
                                    "last_name" : person.lastname, 
                                    "age" : person.age,
                                    "role" : person.role,
                                    "password" :  Person_db.encrypt_password(person.password),
                                    "creator" : creator})
    @staticmethod
    def encrypt_password(password):
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def is_password_correct(username, password):
        encrypted_password = Person_db.encrypt_password(password)
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

    @staticmethod
    def get_role_by_username(username):
        result = Mongo.client.get_collection('person').find({"username" : username})
        return result[0]['role']