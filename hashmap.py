import random

from map import Map

class HashMap(object):
    # klasa modeluje heš mapu

    def __init__(self, capacity=8):
        self._data = capacity * [None]
        self._capacity = capacity
        self._size = 0 # velicina je 0 na pocetku, pa je ovecavamo kako dodajemo elemente
        self.prime = 109345121 # veliki prost broj; sluzi da minimizuje sansu da razliciti kljucevi daju isti hash

        # konstante hesiranja
        # nasumicno izabrani brojevi pri pokretanju (tzv. universal hashing); svrha im je da, cak i ako neko namerno posalje podatke koji bi inace pravili kolizije, pri svakom novom pokretanju programa hash funkcija rasporedjuje elemente potpuno drugacije
        self._a = 1 + random.randrange(self.prime-1) # random u osegu od 0 do prime-2 i onda +1 (jer a ne sme biti 0)
        self._b = random.randrange(self.prime) # random od 0 do prime-1

    def __len__(self):
        return self._size

    def _hash(self, x):
        # hash funkcija

        # hash(x) je ugradjena funkcija i ona uzme npr. string "marko" i pretvori ga u neki privremeni veliki cijeli broj (xor bajtova uz trenutni sistemski seed protiv hakovanja)
        # kod onda taj broj dodatno "promesa" preko univerzalnog hesiranja (* self._a + self._b)

        hashed_value = (hash(x)*self._a + self._b) % self.prime
        compressed = hashed_value % self._capacity # nasilno smanjujemo br da bismo dobili indeks koji staj eu kapacitet mape
        return compressed

    def _resize(self, capacity):
        # prosirivanje mape ako je potrebno jos mesta

        old_data = list(self.items())
        self._data = capacity * [None]
        self._capacity = capacity
        self._size = 0

        # prepisivanje podataka u novu tabelu
        for (k, v) in old_data:
            self[k] = v

    def __getitem__(self, key):
        # pristup elementu sa zadatim kljucem

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


class ChainedHashMap(HashMap):
    # hash mapa koja koliziju resava ulancavanjem

    def _bucket_getitem(self, i, key):
        # pristup elementu sa kljucem key u okviru bucketa na indeksu i

        bucket = self._data[i]
        if bucket is None:
            raise KeyError('This element does not exist')
        return bucket[key]

    def _bucket_setitem(self, i, key, value):
        # postavljanje elementa (key, value) u bucket na indeksu i

        bucket = self._data[i]
        if bucket is None:
            self._data[i] = Map()

        curr_size = len(self._data[i])
        self._data[i][key] = value
        if len(self._data[i]) > curr_size:
            self._size += 1

    def _bucket_delitem(self, i, key):
        # brisanje elementa sa kljucem key na bucketu indkesa i

        bucket = self._data[i]
        if bucket is None:
            raise KeyError('This element does not exist')

        del bucket[key]
        self._size -= 1

    def __iter__(self):
        bucket: Map
        for bucket in self._data:
            if bucket is not None:
                for key in bucket:
                    yield key

    def items(self):
        bucket: Map
        for bucket in self._data:
            if bucket is not None:
                for key, value in bucket.items():
                    yield key, value