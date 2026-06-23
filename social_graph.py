from encodings.punycode import selective_find

from hashmap import ChainedHashMap
from user import User

class SocialGraph(object):

    def __init__(self):

        self.users = ChainedHashMap()
        self.following = ChainedHashMap() # korisnik id : izlazne veze (svi koje on prati)
        self.followers = ChainedHashMap() # korisnik id : ulazne veze (svi koji njega prate)

        self.blocked_by_me = ChainedHashMap() # korisnik id : svi koje je blokirao
        self.blocked_by_others = ChainedHashMap() # korisnik id : svi koji su njega blokirali

    def load_users(self):

        with open("dataset/small/users.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # preskoči praznu liniju

                parts = line.split("|")
                user = User(parts[0], parts[1], parts[2])  # id, username, bio

                self.users.__setitem__(user.user_id, user)

    # ipak ne treba po specifikaciji
    # def save_users(self):
    #     with open("dataset/small/users.txt", "w", encoding="utf-8") as f:
    #         for user_id in self.users:
    #             user = self.users[user_id]
    #             f.write(f"{user.user_id}|{user.username}|{user.bio}\n")

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

    # ipak ne treba
    # def save_connections(self):
    #     with open("dataset/small/users.txt", "w", encoding="utf-8") as f:
    #         for user in self.users:
    #             f.write(f"{user.user_id}|{user.username}|{user.bio}\n")

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
                self.blocked_by_others[blocked_id].add(blocked_id)
