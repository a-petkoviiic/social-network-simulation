import heapq


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
                self.top_influencers = self.top_heap(self.graph.users)
                return

            old_ranks = new_ranks
            new_ranks = dict()

    def top_heap(self, users, n=5):
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