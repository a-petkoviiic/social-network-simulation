class SocialGraph(object):

    def __init__(self):

        # self.users = [] - hash mapa
        self.following = {} # recnik korisnik : br izlaznih veza (svi koje on prati)
        self.followers = {} # recnik korisnik : br ulaznih veza (svi koji njega prate)