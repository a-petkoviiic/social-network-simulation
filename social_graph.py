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
        self.top_influencers = []

        self.bio_words = dict()

        self.following_history = dict() # kad on nekog zaprati dodaje se ovde kao kljuc
        self.followers_history = dict() # kad neko njega zaprati dodaje se ovde kao kljuc


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

    def load_all(self):
        self.load_users()
        self.load_connections()
        self.load_blocked()

        self.bio_inverted_index() # odmah popunjavamo i inverted index hash mapu za bio reci

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
                #print(f"\n{rounds} rundi")
                self.page_ranks = new_ranks
                self.top_influencers = self.top_heap(self.users) # atribut klase dobija vrednost 5 najuticajnijih nakon izracunavanja page ranka
                return

            old_ranks = new_ranks
            new_ranks = dict()

    def top_heap(self, users, n=5):
        heap = [] # cuva top 5 korisnika sa najvecim page rankom (njihove id-jeve)

        for user_id in users:
            if len(heap) < n:
                heapq.heappush(heap, (self.page_ranks[user_id], user_id))
            else:
                if self.page_ranks[user_id] > heap[0][0]:
                    heapq.heapreplace(heap, (self.page_ranks[user_id], user_id))

        top= sorted(heap, key=lambda x: x[0], reverse=True)
        return top

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

    def search_users(self, username_input, bio_input, n):
        founded_matches = set()

        bio_input_words = ''
        if bio_input != '':
            bio_input_words = bio_input.strip().lower().split()

        for user_id in self.users:
            bio_match = True

            if not (username_input.strip().lower() == '' or username_input.strip().lower() in self.users[user_id].username.lower()):
                continue

            if bio_input != '':
                for word in bio_input_words:
                    if word not in self.bio_words or user_id not in self.bio_words[word]:
                        bio_match = False
                        break

            if bio_match:
                founded_matches.add(user_id)

        return self.top_heap(founded_matches, n)

    # ------------------------------------------------------------------------------------------


    # NOVA PRACENJA

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


if __name__ == "__main__":
    graph = SocialGraph()
    graph.load_all()

    graph.calculate_page_rank()

    # print(f"Vreme racunanja PageRank-a: {end - start:.4f} sekundi")

    while True:
        print("\nMeni:")
        print("1) Pretraga korisnika\n"
              "2) Prikaz top 5 najuticajnijih korisnika\n"
              "3) Dodavanje nove veze praćenja\n"
              "4) Prikaz istorije praćenja\n"
              "x za izlaz iz programa")

        option = input("\nUnesite broj ispred željene opcije: ")

        if option not in ["1", "2", "3", "4", "x"]:
            print("Neispravan unos, pokusajte ponovo.\n")

        elif option == "1":
            username = input("\nUsername: ")
            bio = input("Bio: ")
            while True:
                top_num = input("Top num: ")
                if not top_num.isdigit():
                    print("Neispravan unos, pokusajte ponovo.\n")
                    continue
                break
            search = graph.search_users(username, bio, int(top_num))

            if search:
                print("Pronadjeni: ")
                for rank, user_id in search:
                    username = graph.users[user_id].username
                    print(f"\t- {username}: {rank:.6f}")
            else:
                print("Nema pronadjenih.")

        elif option == "2":
            print("\nTop 5 najuticajnijih korisnika: ")
            for rank, user_id in graph.top_influencers:
                username = graph.users[user_id].username
                print(f"\t- {username}: {rank:.6f}")

        elif option == "3":
            while True:
                new_connection = input("\nUnesite novu vezu u formatu follower_id->following_id: ")
                if '->' not in new_connection:
                    print("Neispravan unos, pokusajte ponovo")
                    continue
                break

            users_id = new_connection.strip().split('->')
            if len(users_id) != 2:
                print("Neispravan unos, pokusajte ponovo")
                continue

            success = graph.add_connection(users_id[0], users_id[1])

            if success:
                print(f"{graph.users[users_id[0]].username} je zapratio {graph.users[users_id[1]].username}!")
            else:
                # vec ispisana poruka zasto u funkciji
                continue

        elif option == "4":
            user_id = input("\nUnesite user_id korisnika ciju istoriju zelite da pregledate: ")
            if user_id not in graph.users:
                print("Trazeni korisnik ne postoji.")
                continue
            if user_id not in graph.following_history:
                print("U ovoj sesiji ovaj korisnik nije zapratio nikoga.")
                continue

            following_history = graph.following_history[user_id]
            print(f"Hronoloski prikazano koga je zapraćivao korisnik {graph.users[user_id].username}: ")
            for user_id in following_history:
                print(f"\t- {graph.users[user_id].username}")

        elif option == "x":
            print("\nIzlazak iz programa...")
            break