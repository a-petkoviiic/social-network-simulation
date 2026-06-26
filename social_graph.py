from collections import deque

from user import User

class SocialGraph(object):

    def __init__(self):

        self.users = dict() # kljucevi su id
        self.username_to_user = dict()
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
                self.username_to_user[user.username] = user

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

        if user2_id in self.following.get(user1_id, set()): # ako kljuc ne postoji, tj. ako user1 ne prati nikog jos uvek, vraca se prazan set()
            print("Veza vec postoji.\n")
            return False

        if user2_id in self.blocked_by_me.get(user1_id, set()): # user 1 blokirao user2
            print("Izmedju korisnika postoji block! :(\n")
            return False
        if user1_id in self.blocked_by_me.get(user2_id, set()): # user2 blokirao user1
            print("Izmedju korisnika postoji block! :(\n")
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

        # u mainu se poziva racunanje page ranka ponovo nakon uspesno dodate veze
        return True

    # bfs:

    def bfs(self, user_id, n):
        queue = deque()
        queue.append((user_id, 0))
        visited = set()
        visited.add(user_id)

        levels = dict()

        while queue:
            curr_id, curr_level = queue.popleft()

            if curr_level == n:
                continue

            for next_id in self.following.get(curr_id, set()):
                if next_id not in visited:
                    visited.add(next_id)
                    next_level = curr_level + 1
                    queue.append((next_id, next_level))

                    if next_level not in levels:
                        levels[next_level] = []
                    levels[next_level].append(next_id)

        return levels

