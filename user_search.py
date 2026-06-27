import re
import difflib

from trie import Trie

class UserSearch(object):
    # klasa odgovorna za pretragu korisnika po username-u i po recima iz biografije
    # koristi inverted index nad bio recima, i Ranker za rangiranje rezultata po PageRank-u

    def __init__(self, graph, ranker):
        self.graph = graph      # referenca na SocialGraph -- ovde citamo users
        self.ranker = ranker    # referenca na Ranker -- ovde dobijamo top_heap i page_ranks

        self.bio_words = dict()

    def build_inverted_index(self): # pozivamo jednom nakon load_all() pri pokretanju programa
        for user_id in self.graph.users:
            bio = self.graph.users[user_id].bio.lower()  # biografija trenutnog korisnika
            bio_words = bio.split()

            for word in bio_words:
                word = re.sub(r'[^\w\s]', '', word)  # \w su slova, brojevi i _

                if not word:
                    continue  # ako je posle ciscenja ostao prazan string, preskoci

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

        for user_id in self.graph.users:
            bio_match = True

            if not (username_input.strip().lower() == '' or username_input.strip().lower() in self.graph.users[
                user_id].username.lower()):
                continue

            if bio_input != '':
                for word in bio_input_words:
                    if word not in self.bio_words or user_id not in self.bio_words[word]:
                        bio_match = False
                        break

            if bio_match:
                founded_matches.add(user_id)

        print("DEBUG founded_matches:", founded_matches)
        return self.ranker.top_heap_ranks(founded_matches, n)

    def did_you_mean(self, username):
        return difflib.get_close_matches(username, self.graph.username_to_user.keys(), n=3, cutoff=0.6)

    def build_trie(self):
        trie = Trie()
        for user in self.graph.users.values():
            trie.insert(user.username.lower())
        return trie