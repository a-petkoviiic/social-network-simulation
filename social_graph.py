from user import User

class SocialGraph(object):

    def __init__(self):

        self.users = dict()
        self.following = dict()   # korisnik id : izlazne veze (svi koje on prati)
        self.followers = dict()   # korisnik id : ulazne veze (svi koji njega prate)

        self.blocked_by_me = dict() # korisnik id : svi koje je blokirao
        self.blocked_by_others = dict() # korisnik id : svi koji su njega blokirali

        self.following_history = dict() # kad on nekog zaprati dodaje se ovde kao kljuc
        self.followers_history = dict() # kad neko njega zaprati dodaje se ovde kao kljuc

    # ucitavanje iz fajlova:

    def load_users(self):

        with open("dataset/small/users.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # preskoči praznu liniju

                parts = line.split("|")
                user = User(parts[0], parts[1], parts[2])  # id, username, bio

                self.users[user.user_id] = user

    def load_connections(self):
        with open("dataset/small/connections.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                follower_id = parts[0]  # onaj koji prati
                followed_id = parts[1]  # onaj koji je praćen

                if follower_id not in self.following:
                    self.following[follower_id] = set()  # ako vec nema tog kljuca
                self.following[follower_id].add(followed_id)

                if followed_id not in self.followers:
                    self.followers[followed_id] = set()
                self.followers[followed_id].add(follower_id)

    def load_blocked(self):
        with open("dataset/small/blocked.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                blocker_id = parts[0]  # onaj koji blokira
                blocked_id = parts[1]  # onaj koji je blokiran

                if blocker_id not in self.blocked_by_me:
                    self.blocked_by_me[blocker_id] = set()  # ako vec nema tog kljuca
                self.blocked_by_me[blocker_id].add(blocked_id)

                if blocked_id not in self.blocked_by_others:
                    self.blocked_by_others[blocked_id] = set()
                self.blocked_by_others[blocked_id].add(blocker_id)

    def load_all(self):
        self.load_users()
        self.load_connections()
        self.load_blocked()


    # nova pracenja:

    def add_connection(self, user1_id, user2_id):
        if user1_id not in self.users or user2_id not in self.users:
            print("Jedan ili oba korisnika ne postoje.\n")
            return False

        if user2_id in self.following.get(user1_id, set()):
            print("Veza vec postoji.\n")
            return False

        # azuriram following i followers
        if user1_id not in self.following:
            self.following[user1_id] = set()
        self.following[user1_id].add(user2_id)
        if user2_id not in self.followers:
            self.followers[user2_id] = set()
        self.followers[user2_id].add(user1_id)

        # korisnik2 je zapracen od korisnika1 - ide u followers_history[user2_id]
        if user2_id not in self.followers_history:
            self.followers_history[user2_id] = []
        self.followers_history[user2_id].append(user1_id)

        # korisnik1 je zapratio korisnika2 - ide u following_history[user1_id]
        if user1_id not in self.following_history:
            self.following_history[user1_id] = []
        self.following_history[user1_id].append(user2_id)

        self.calculate_page_rank()
        return True

    def user_following_history(self, user_id):
        return self.following_history[user_id]