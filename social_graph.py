import heapq
import re

from user import User

class SocialGraph(object):

    def __init__(self):

        self.users = dict()
        self.following = dict()   # korisnik id : izlazne veze (svi koje on prati)
        self.followers = dict()   # korisnik id : ulazne veze (svi koji njega prate)

        self.blocked_by_me = dict() # korisnik id : svi koje je blokirao
        self.blocked_by_others = dict() # korisnik id : svi koji su njega blokirali

        self.page_ranks = dict()
        self.damping = 0.85
        self.top5_users = []

        self.bio_words = dict()
        self.bio_inverted_index() # odmah popunjavamo recnih sa recima iz biografija


    # UCITAVANJE PODATAKA IZ FAJLOVA

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

    # ------------------------------------------------------------------------------------------


    # PAGE RANK

    def calculate_page_rank(self):
        old_ranks = self.page_ranks
        n = len(self.users)
        if len(self.page_ranks) == 0:
            for user_id in self.users:
                self.page_ranks[user_id] = 1 / n # inicijalni page rank, ako je ovo prvi krug racunanja page rankova


        new_ranks = dict()  # ovde upisujemo nove vrednosti, pa uporedjujemo sa starima

        x = (1 - self.damping) / n # sabirak koji dodajemo svuda na pocetak

        epsilon = 0.000001

        rounds = 0
        while True:
            total_diff = 0
            rounds += 1

            for user_id in self.users:
                new_ranks[user_id] = x

                # prolazimo kroz sve pratioce, AKO je trenutni korisnik u listi korisnika koji imaju bar jednog pratioca
                if user_id in self.followers:
                    for follower_id in self.followers[user_id]:
                        old_value = old_ranks[follower_id] # prethodni page rank tog korisnika
                        following_num = len(self.following[follower_id]) # koliko ljudi prati taj korisnik

                        new_ranks[user_id] += self.damping * (old_value / following_num)

                # razlika izmedju stare i nove vrednosti ranka za trenutnog korisnika
                total_diff += abs(old_ranks[user_id] - new_ranks[user_id])

            if total_diff < epsilon:
                print(f"\n{rounds} rundi")
                self.page_ranks = new_ranks
                self.top5_users = self.top_heap() # atribut klase dobija vrednost 5 najuticajnijih nakon izracunavanja page ranka
                return

            old_ranks = new_ranks
            new_ranks = dict()

    def top_heap(self):
        heap = [] # cuva top 5 korisnika sa najvecim page rankom (njihove id-jeve)
        num = 5

        for user_id in self.users:
            if len(heap) < num:
                heapq.heappush(heap, (self.page_ranks[user_id], user_id))
            else:
                if self.page_ranks[user_id] > heap[0][0]:
                    heapq.heapreplace(heap, (self.page_ranks[user_id], user_id))

        top5_users = sorted(heap, key=lambda x: x[0], reverse=True)
        return top5_users

    # ------------------------------------------------------------------------------------------

    # PRETRAGA KORISNIKA

    def bio_inverted_index(self):
        for user_id in self.users:
            bio = self.users[user_id].bio.lower()  # biografija trenutnog korisnika
            bio_words = bio.split()

            for word in bio_words:
                word = re.sub(r'[^\w\s]', '', word)  # \w su slova, brojevi i _

                if word in self.bio_words:
                    self.bio_words[word].add(user_id)
                else:
                    self.bio_words[word] = set()
                    self.bio_words[word].add(user_id)

    def search_users(self, username_input, bio_input):
        founded_matches = []

        for user_id in self.users:
            if self.users[user_id].username.lower().contains(username_input.strip().lower()):
                founded_matches.append(user_id)
        # ovo nije gotova funkcija ne gledaj je


if __name__ == "__main__":
    import time

    graph = SocialGraph()

    graph.load_users()
    graph.load_connections()
    graph.load_blocked()

    start = time.time()
    graph.calculate_page_rank()
    end = time.time()

    print(f"Vreme racunanja PageRank-a: {end - start:.4f} sekundi")

    print("\nTop 5 najuticajnijih korisnika: ")
    for rank, user_id in graph.top5_users:
        username = graph.users[user_id].username
        print(f"\t- {username}: {rank:.6f}")