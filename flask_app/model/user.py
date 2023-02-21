from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import date, datetime
import re

name_regex = re.compile(r'^[a-zA-Z]')
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db = "friends"
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.alias = data["alias"]
        self.email = data["email"]
        self.password = data["password"]
        self.birthday = data["birthday"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @staticmethod
    def validate_registration(registration):
        is_valid = True
        #names
        if len(registration["name"]) < 3 or not name_regex.match(registration["alias"]):
            flash(u"Name must be letters and have more than 2 characters.","register")
            is_valid = False
        if len (registration["alias"]) < 3 or not name_regex.match(registration["alias"]):
            flash(u"Alias must be letters and have more than 2 characters.","register")
            is_valid = False
        #emails
        if not email_regex.match(registration["email"]):
            flash(u"Please enter a valid email address.","register")
            is_valid = False

        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL("friends").query_db(query, registration)
        if len(results) >= 1:
            flash(u"Email is already in use.","register")
            is_valid = False

        #passwords
        if len(registration["password"]) <= 8:
            flash(u"Password must be at least 8 characters long.","register")
            is_valid = False
        if registration["password"] != registration["cpassword"]:
            flash(u"Password and Confirm Password is not the same.","register")
            is_valid = False
        

        #birthday
        def get_age():
            born = registration["birthday"]
            born = datetime.strptime(born, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - born.year - ((today.month,today.day) < (born.month, born.day))
            return age
        if registration["birthday"] == "":
            flash(u"Please enter your date of birth.", "register")
            is_valid = False
        if registration["birthday"] != "":
            if get_age() < 16:
                flash(u"You must be 16 years or older to register.", "register")
                is_valid = False
            else:
                is_valid = True
        return is_valid

    @classmethod
    def get_all_users(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for user in results:
            users.append(cls(user))
        return users

    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s"

        result = connectToMySQL(cls.db).query_db(query, data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def add_user(cls, data):
        query = "INSERT INTO users (name, alias, email, password, birthday) VALUES (%(name)s, %(alias)s, %(email)s, %(password)s, %(birthday)s);"
        results = connectToMySQL(cls.db).query_db(query, data)
        return results
    
    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s"

        result = connectToMySQL(cls.db).query_db(query, data)

        return cls(result[0])
    
    @classmethod
    def add_friend(cls, data):
        query = "INSERT INTO friendships (user_id, user2_id) VALUES (%(user_id)s, %(user2_id)s), (%(user2_id)s, %(user_id)s);"

        result = connectToMySQL(cls.db).query_db(query, data)

        return result
    
    @classmethod
    def get_user_friends(cls,data):
        query = "SELECT friendships.id, users.alias, users2.alias as friend, users2.id as friend_id FROM users JOIN friendships on friendships.user_id = users.id JOIN users as users2 ON users2.id = friendships.user2_id WHERE users.id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        return results
    
    @classmethod
    def get_none_friends (cls, data):
        query = "SELECT * FROM users WHERE users.id NOT IN (SELECT user2_id FROM friendships WHERE user_id =%(id)s);"

        results = connectToMySQL(cls.db).query_db(query, data)
        not_friends = []
        for person in results:
            not_friends.append(cls(person))
        return not_friends
    
    @classmethod
    def remove_friend (cls, data):
        query = "DELETE FROM friendships WHERE (user_id = %(user_id)s AND user2_id = %(user2_id)s) OR (user2_id = %(user_id)s AND user_id = %(user2_id)s);"
        result = connectToMySQL(cls.db).query_db(query, data)
        return result