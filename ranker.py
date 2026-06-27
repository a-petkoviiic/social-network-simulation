import heapq
import re

from unicodedata import normalize


class Ranker(object):
    # klasa odgovorna za racunanje PageRank vrednosti nad SocialGraph objektom

    def __init__(self, graph, damping=0.85, epsilon=0.000001):
        self.graph = graph
        self.damping = damping
        self.epsilon = epsilon

        self.page_ranks = dict()    # user_id -> trenutna page rank vrednost
        self.top_influencers = []   # lista (rank, user_id) tuple-ova, popunjava se nakon racunanja

    def calculate_page_rank(self):
        old_ranks = self.page_ranks
        n = len(self.graph.users)

        if len(self.page_ranks) == 0:
            for user_id in self.graph.users:
                self.page_ranks[user_id] = 1 / n  # inicijalni page rank, ako je ovo prvi krug racunanja

        new_ranks = dict()  # ovde upisujemo nove vrednosti, pa uporedjujemo sa starima

        x = (1 - self.damping) / n  # sabirak koji dodajemo svuda na pocetak

        rounds = 0
        while True:
            total_diff = 0
            rounds += 1

            for user_id in self.graph.users:
                new_ranks[user_id] = x

                # prolazimo kroz sve pratioce, ako trenutni korisnik ima bar jednog pratioca
                if user_id in self.graph.followers:
                    for follower_id in self.graph.followers[user_id]:
                        old_value = old_ranks[follower_id]  # prethodni page rank tog korisnika
                        following_num = len(self.graph.following[follower_id])  # koliko ljudi prati taj korisnik

                        new_ranks[user_id] += self.damping * (old_value / following_num)

                # razlika izmedju stare i nove vrednosti ranka za trenutnog korisnika
                total_diff += abs(old_ranks[user_id] - new_ranks[user_id])

            if total_diff < self.epsilon:
                # print(f"\n{rounds} rundi")
                self.page_ranks = new_ranks
                self.top_influencers = self.top_heap_ranks(self.graph.users)
                return

            old_ranks = new_ranks
            new_ranks = dict()

    def top_heap_ranks(self, users, n=5):
        # cuva top n korisnika sa najvecim page rankom (njihove id-jeve), koristeci heap
        heap = []

        for user_id in users:
            if len(heap) < n:
                heapq.heappush(heap, (self.page_ranks[user_id], user_id))
            else:
                if self.page_ranks[user_id] > heap[0][0]:
                    heapq.heapreplace(heap, (self.page_ranks[user_id], user_id))

        top = sorted(heap, key=lambda x: x[0], reverse=True)
        return top

    def calculate_personal_page_rank(self, source_id):
        old_ranks = dict()
        personal_ranks = dict()  # ovde upisujemo nove vrednosti, pa uporedjujemo sa starima

        x = 1 - self.damping
        for user_id in self.graph.users:
            old_ranks[user_id] = 0.0
        old_ranks[source_id] = 1.0

        while True:
            total_diff = 0

            for user_id in self.graph.users:
                if user_id == source_id:
                    personal_ranks[user_id] = x
                else:
                    personal_ranks[user_id] = 0

                # # resavanje problema cvorova koji nikog ne prate
                # sink_ppr = 0.0
                # for uid in self.graph.users:
                #     # ako korisnik ne prati nikoga, njegov rank se teleportuje na source_id
                #     if uid not in self.graph.following or len(self.graph.following[uid]) == 0:
                #         sink_ppr += old_ranks[uid]
                #
                # # dodajemo doprinos slepih ulica direktno na source_id
                # personal_ranks[source_id] += self.damping * sink_ppr

                # prolazimo kroz sve pratioce, ako trenutni korisnik ima bar jednog pratioca
                if user_id in self.graph.followers:
                    for follower_id in self.graph.followers[user_id]:
                        old_value = old_ranks[follower_id]  # page rank tog korisnika
                        following_num = len(self.graph.following[follower_id])  # koliko ljudi prati taj korisnik

                        personal_ranks[user_id] += self.damping * (old_value / following_num)

                total_diff += abs(old_ranks[user_id] - personal_ranks[user_id])

            if total_diff < self.epsilon:
                return self.normalize(personal_ranks)

            old_ranks = personal_ranks
            personal_ranks = dict()

    def bio_similarity(self, graph, source_id):
        source_words = set()
        for word in graph.users[source_id].bio.lower().split():
            word = re.sub(r'[^\w\s]', '', word)
            if not word:
                continue
            source_words.add(word)

        similarity = dict() # kljuc je id korisnika, value slicnost sa biografijom od source idja

        for user_id in graph.users:
            if user_id == source_id:
                continue

            user_words = set()
            for word in graph.users[user_id].bio.lower().split():
                word = re.sub(r'[^\w\s]', '', word)
                if not word:
                    continue
                user_words.add(word)

            intersection = len(source_words & user_words)
            union = len(source_words | user_words)

            if union == 0:
                similarity[user_id] = 0.0
                continue

            result = intersection / union
            similarity[user_id] = result

        return self.normalize(similarity)

    def normalize(self, scores):
        if not scores:
            return scores

        max_val = max(scores.values())  # najveća vrednost u rečniku
        if max_val == 0:
            return scores

        normalized = dict()
        for user_id in scores:
            normalized[user_id] = scores[user_id] / max_val
        return normalized

    def top_heap_recommendations(self, not_following_users, n=5):
        heap = []

        for user_id in not_following_users:
            if len(heap) < n:
                heapq.heappush(heap, (not_following_users[user_id], user_id))
            else:
                if not_following_users[user_id] > heap[0][0]:
                    heapq.heapreplace(heap, (not_following_users[user_id], user_id))

        top = sorted(heap, key=lambda x: x[0], reverse=True)
        return top