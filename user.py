class User(object):

    def __init__(self, user_id, username, bio):
        self._user_id = user_id
        self._username = username
        self._bio = bio

    @property
    def user_id(self):
        return self._user_id
    @property
    def username(self):
        return self._username
    @property
    def bio(self):
        return self._bio