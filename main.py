from social_graph import SocialGraph
from ranker import Ranker
from user_search import UserSearch

if __name__ == "__main__":
    graph = SocialGraph()
    ranker = Ranker(graph)
    search = UserSearch(graph, ranker)

    graph.load_all() # podaci iz fajlova
    search.build_inverted_index() # reci iz biografije se pune u inverted index

    ranker.calculate_page_rank()

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
            search = search.search_users(username, bio, int(top_num))

            if search:
                print("Pronadjeni: ")
                for rank, user_id in search:
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