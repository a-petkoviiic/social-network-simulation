from social_graph import SocialGraph
from ranker import Ranker
from user_search import UserSearch

def from_username_to_id(graph, search, username):
    username = username.lower()
    if username not in graph.username_to_user:
        possible = search.did_you_mean(username)

        if possible:
            print("Did you mean?")
            for i, name in enumerate(possible, start=1):
                print(f"{i}) {name}")
            while True:
                chosen = input("Unesite broj korisnika kog ste hteli (ili Enter za odustajanje): ")

                if chosen.strip() == "":
                    print("Odustali ste.\n")
                    return False
                elif not chosen.isdigit():
                    print("Niste uneli ispravan broj.\n")
                    continue
                elif int(chosen) < 1 or int(chosen) > len(possible):
                    print("Broj nije u opsegu ponudjenih opcija.\n")
                    continue
                else:
                    chosen_username = possible[int(chosen) - 1]
                    chosen_user_id = graph.username_to_user[chosen_username.lower()].user_id
                    return chosen_user_id
        else:
            print("Izabrani username ne postoji, kao ni neki njemu slican.\n")
            return False

    else:
        chosen_user_id = graph.username_to_user[username.lower()].user_id
        return chosen_user_id


if __name__ == "__main__":
    graph = SocialGraph()
    ranker = Ranker(graph)
    search = UserSearch(graph, ranker)

    graph.load_all() # podaci iz fajlova
    search.build_inverted_index() # reci iz biografije se pune u inverted index
    trie = search.build_trie() # odmah od usernama gradiomo trie stablo

    ranker.calculate_page_rank()

    while True:
        print("\nMeni:")
        print("1) Pretraga korisnika\n"
              "2) Prikaz top 5 najuticajnijih korisnika\n"
              "3) Dodavanje nove veze praćenja\n"
              "4) Prikaz istorije praćenja\n"
              "5) Prikaz direktnih i indirektnih konekcija\n"
              "6) Prikaz preporuka za datog korisnika\n"
              "7) Autocomplete pretraga po prefiksu\n"
              "x za izlaz iz programa")

        option = input("\nUnesite broj ispred željene opcije: ")

        if option not in ["1", "2", "3", "4", "5", "6", "7", "x"]:
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
            results = search.search_users(username, bio, int(top_num))

            if results:
                print("Pronadjeni: ")
                for rank, user_id in results:
                    username = graph.users[user_id].username
                    print(f"\t- {username}: {rank:.6f}")
            else:
                print("Nema pronadjenih.")

        elif option == "2":
            print("\nTop 5 najuticajnijih korisnika: ")
            for rank, user_id in ranker.top_influencers:
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
                ranker.calculate_page_rank()
            else:
                # vec ispisana poruka zasto u funkciji
                continue


        elif option == "4":
            username = input("\nUnesite username korisnika ciju istoriju zelite da pregledate: ")

            result = from_username_to_id(graph, search, username)
            if result is False:
                continue
            else:
                user_id = result
                user = graph.users[user_id]

            if user_id not in graph.following_history:
                print("U ovoj sesiji ovaj korisnik nije zapratio nikoga.\n")
                continue

            print(f"Hronoloski koga je zapratio korisnik {user.username}:")
            for followed_id in graph.following_history[user_id]:
                print(f"\t- {graph.users[followed_id].username}")

        elif option == "5":
            username = input("\nUnesite username korisnika cije konekcije zelite da pregledate: ")

            result = from_username_to_id(graph, search, username)
            if result is False:
                continue
            else:
                user_id = result
                user = graph.users[user_id]

            while True:
                level = input("\nUnesite level: ")

                if not level.isdigit():
                    print("Neispravan unos, pokusajte ponovo.\n")
                    continue
                level = int(level)
                break

            result_levels = graph.bfs(user_id, level)

            if not result_levels:
                print("Ovaj korisnik nema konekcija.")
            else:
                for l in result_levels.keys():
                    print(f"Level {l}:")
                    for connection_user_id in result_levels[l]:
                        print(f"\t- {graph.users[connection_user_id].username}")

        elif option == "6":
            username = input("\nUnesite username korisnika cije konekcije zelite da pregledate: ")

            result = from_username_to_id(graph, search, username)
            if result is False:
                continue
            else:
                user_id = result
                user = graph.users[user_id]

            while True:
                alpha = input("Unesite alpha (0 do 1): ")

                try:
                    alpha = float(alpha)
                except ValueError:
                    print("Neispravan unos, pokusajte ponovo.\n")
                    continue

                if not 0 <= float(alpha) <= 1:
                    print("Neispravan unos, pokusajte ponovo.\n")
                    continue

                break

            recommendations = dict()
            ppr = ranker.calculate_personal_page_rank(user_id)  # jednom
            sim = ranker.bio_similarity(graph, user_id)
            for uid in graph.users:
                score = 0
                if uid == user_id:
                    continue
                if uid in graph.following.get(user_id, set()):  # koga već prati
                    continue
                if uid in graph.blocked_by_me.get(user_id, set()):  # koga je blokirao
                    continue
                if uid in graph.blocked_by_others.get(user_id, set()):  # ko je blokirao njega
                    continue
                else:
                    score = (alpha * ppr.get(uid, 0) + (1 - alpha) * sim.get(uid, 0))
                    recommendations[uid] = score

            top_recommendations = ranker.top_heap_recommendations(recommendations)
            if not top_recommendations:
                print("Nema preporuka za ovog korisnika.")
            else:
                print(f"\nPreporuke za {user.username}:")
                for score, uid in top_recommendations:
                    print(f"\t- {graph.users[uid].username}: {score:.6f}")

        elif option == "7":
            username = input("\nUnesite username: ").lower()
            all_usernames = trie.autocomplete(username)

            all_user_id = set()
            for username in all_usernames:
                user_id = graph.username_to_user[username].user_id
                all_user_id.add(user_id)

            completions = ranker.top_heap_ranks(all_user_id)
            if not completions:
                print("Nema preporuka za ovog korisnika.")
            else:
                print(f"Mozda ste u potrazi za:")
                for score, uid in completions:
                    print(f"\t- {graph.users[uid].username}: {score:.6f}")

        elif option == "x":
            print("\nIzlazak iz programa...")
            break