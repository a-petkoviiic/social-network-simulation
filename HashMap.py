import random

class HashMap(object):
    """
    Klasa modeluje heš mapu
    """

    def __init__(self, capacity=8):
        """
        Konstruktor

        Argumenti:
        - `capacity`: inicijalni broj mesta u lookup nizu
        - `prime`: prost broj neophodan heš funkciji
        """
        self._data = capacity * [None]
        self._capacity = capacity
        self._size = 0
        self.prime = 109345121 # veliki prost broj; sluzi da minimizuje sansu da razliciti kljucevi daju isti hash

        # konstante hesiranja
        # nasumicno izabrani brojevi pri pokretanju (tzv. universal hashing); svrha im je da, cak i ako neko namerno posalje podatke koji bi inace pravili kolizije, pri svakom novom pokretanju programa hash funkcija rasporedjuje elemente potpuno drugacije
        self._a = 1 + random.randrange(self.prime-1) # random u osegu od 0 do prime-2 i onda +1 (jer a ne sme biti 0)
        self._b = random.randrange(self.prime) # random od 0 do prime-1

    def __len__(self):
        return self._size

    def _hash(self, x):
        """
        Heš funkcija

        Izračunavanje heš koda vrši se po formuli (ax + b) mod p.

        Argument:
        - `x`: vrednost čiji se kod računa
        """

        # hash(x) je ugradjena funkcija i ona uzme npr. string "marko" i pretvori ga u neki privremeni veliki cijeli broj (xor bajtova uz trenutni sistemski seed protiv hakovanja)
        # kod onda taj broj dodatno "promesa" preko univerzalnog hesiranja (* self._a + self._b)

        hashed_value = (hash(x)*self._a + self._b) % self.prime
        compressed = hashed_value % self._capacity # nasilno smanjujemo br da bismo dobili indeks koji staj eu kapacitet mape
        return compressed

    def _resize(self, capacity):
        """
        Skaliranje broja raspoloživih slotova

        Metoda kreira niz sa unapred zadatim kapacitetom u koji
        se prepisuju vrednosti koje se trenutno nalaze u tabeli.

        Argument:
        - `capacity`: kapacitet novog niza
        """
        old_data = list(self.items())
        self._data = capacity * [None]
        self._size = 0

        # prepisivanje podataka u novu tabelu
        for (k, v) in old_data:
            self[k] = v

    def __getitem__(self, key):
        """
        Pristup elementu sa zadatim ključem

        Apstraktna metoda koja opisuje pristup elementu na osnovu
        njegovog ključa. Implementacija pristupa bucketu varira u
        zavisnosti od načina rešavanja kolizija.

        Argument:
        - `key`: ključ elementa kome se pristupa
        """
        bucket_index = self._hash(key)
        return self._bucket_getitem(bucket_index, key)

    def __setitem__(self, key, value):
        bucket_index = self._hash(key)
        self._bucket_setitem(bucket_index, key, value)

        # povećaj broj raspoloživih mesta
        current_capacity = len(self._data)
        if self._size > current_capacity // 2:
            self._resize(2*current_capacity - 1)

    def __delitem__(self, key):
        bucket_index = self._hash(key)
        self._bucket_delitem(bucket_index, key)