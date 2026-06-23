class User(object):

    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

    @property
    def user_id(self):
        return self.user_id
    @property
    def username(self):
        return self.username
    @property
    def password(self):
        return self.password

    # mozda i nece trebati al ajde
    @password.setter
    def password(self, new_password):
        self.password = new_password