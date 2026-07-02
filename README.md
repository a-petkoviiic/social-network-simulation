# Simulacija rada društvene mreže

Konzolna aplikacija koja simulira deo funkcionalnosti društvene mreže:
- Usmeren graf praćenja - dodavanje nove veze, prikaz istorije dodavanja u trenutnoj sesiji
- Usmeren graf blokiranja 
- PageRank rangiranje korisnika sistema 
- BFS algoritam za prikaz direktnih i indirektnih konekcija 
- Preporuke na osnovu personalized PageRank-a i Jaccard sličnosti biografija 
- Autocomplete pomoću Trie strukture


## Pokretanje i ulazni podaci

Za pokretanje programa, uneti komandu python main.py. Dodatne instalacije 
nisu potrebne.

Putanje do ulaznih fajlova su hardkodovane u kodu.
Za rad sa drugim skupom podataka potrebno je ručno izmeniti 
putanje u social_graph.py u metodama load_users(), load_connections() i
load_blocked() jednostavnom izmenom poslednje reči u putanji
(small/medium/full).

Svi fajlovi se nalaze u folderu dataset/<small|medium|full>/ i koriste "|"
kao separator polja.

### users.txt

Struktura linije: id|username|bio

id — jedinstveni identifikator korisnika (čuva se kao string)
username — korisničko ime
bio — kratak opis korisnika (koristi se za pretragu po
biografiji i za preporuke na osnovu sličnosti biografija)

Primer:

> 1|guimanja|akamikeb badaza blumspew bringbacktoonai bringbacktoonami brinstar cantwait demandprogress elixabethclaire eszettlion eufanday felladin guildwars guildwars2 gw2 gw2beta gw2fanart inspired_ones john_j_ryan jonny10gw killtenrats ktr_ravious ladyverene lifeisgood loremasterkaae newbienice peter_fries sharn_vendeta thatshortguy woodenpotatoes

### connections.txt

Struktura linije: follower_id|following_id

Primer:

> 1|127

### blocked.txt

Struktura linije: blocker_id|blocked_id

Primer:

> 29|644

## Merenje

Merenja su izvršena nad **full** skupom podataka (~82.000 korisnika).
 
- Vreme učitavanja (učitavanje fajlova + izgradnja inverted index-a i Trie
  strukture): **~4.3 s**
- Vreme izvršavanja PageRank algoritma (globalni, prvo računanje, bez warm
  start-a): **~90 s**
PageRank je najskuplja operacija u sistemu, jer se računa iterativno do
konvergencije (`epsilon = 1e-6`), prolazeći kroz sve korisnike i sve njihove
pratioce u svakoj rundi. Na full skupu ovo zahteva
veći broj rundi, pa je vreme izvršavanja znatno veće nego kod učitavanja
podataka. Naknadna računanja (npr. nakon dodavanja nove veze praćenja)
koriste warm start (kreću iz prethodno izračunatih vrednosti), pa su brža
jer ne počinju od nule.

## Funkcionalnosti (meni) i primeri korišćenja

### Pretraga korisnika (opcija 1)

- Substring pretraga po username-u i/ili biografiji, rangirana 
i ograničena na top N rezultata.

Primer:

```
Unesite broj ispred željene opcije: 1
Username: mar
Bio:
Top num: 5

Pronadjeni: 
	- brandxmary: 0.003470
	- maretasand: 0.001377
	- jmarkwilliams: 0.001369
	- markohulyo: 0.001119
	- kristel_marie: 0.001080
```

### Top 5 najuticajnijih korisnika (opcija 2)

- Globalni PageRank nad celom mrežom, prikaz 5 korisnika 
sa najvišom vrednošću.

Primer:

```
Unesite broj ispred željene opcije: 2
Top 5 najuticajnijih korisnika: 
	- GyhRodriigues: 0.030365
	- LuiizP: 0.016570
	- LuvSizzle: 0.014917
	- Dr_Arrogant: 0.013955
	- grupoubr: 0.013587
```

### Dodavanje nove veze praćenja (opcija 3)

- Dodaje vezu praćenja uz provveru postojanja korisnika, duplikata i blokade 
(u oba smera); nakon uspeha ponovo se računa PageRank.

Primer 1:

```
Unesite broj ispred željene opcije: 3
Unesite novu vezu u formatu follower_id->following_id: 22->23
Veza vec postoji.
```

Primer 2:

```
Unesite broj ispred željene opcije: 3
Unesite novu vezu u formatu follower_id->following_id: 22->113
Bollywoodxox je zapratio kratos3681!
```

### Dodavanje novog korisnika (opcija 4)

- Dodaje novog korisnika, uz proveru da li je traženi username dostupan;
nakon uspeha ponovo se računa PageRank, novi username se dodaje u Trie strukturu i 
dopunjava se inverted index sa rečima iy biografije novog korisnika.

Primer:

```
Unesite broj ispred željene opcije: 4
Novi username: testUser
Biografija novog korisnika: test new words
Korisnik testUser uspešno dodat!
```

### Prikaz istorije praćenja (opcija 5)

- Hronološki prikaz korisnika koje je dati korisnik 
zapratio tokom trenutne sesije.

Primer:

```
Unesite broj ispred željene opcije: 5
Unesite username korisnika ciju istoriju zelite da pregledate: Bollywoodxo
Did you mean?
1) bollywoodxox
2) lovelywoodford
Unesite broj korisnika kog ste hteli (ili Enter za odustajanje): 1
Hronoloski koga je zapratio korisnik Bollywoodxox:
	- kratos3681
```

### Prikaz direktnih i indirektnih konekcija (opcija 6)

- BFS od datog korisnika do N nivoa, prikaz po nivoima.

Primer 1: 

```
Unesite broj ispred željene opcije: 6
Unesite username korisnika cije konekcije zelite da pregledate: cubbybear9
Unesite level: 2
Ovaj korisnik nema konekcija.
```

Primer 2: 

```
Unesite broj ispred željene opcije: 6
Unesite username korisnika cije konekcije zelite da pregledate: guimanja
Unesite level: 1
Level 1:
	- GyhRodriigues
	- LuiizP
```

### Prikaz preporuka za datog korisnika (opcija 7)

- Hibridne preporuke: alpha * PPR + (1 - alpha) * Jaccard sličnost biografije, 
sa filterom (sam korisnik, već zapraćeni, blokirani u oba smera).

Primer: 

```
Unesite broj ispred željene opcije: 7
Unesite username korisnika cije konekcije zelite da pregledate: faya0
Did you mean?
1) faza01
Unesite broj korisnika kog ste hteli (ili Enter za odustajanje): 1
Unesite alpha (0 do 1): 0.5

Preporuke za faza01:
	- erhanakhan: 0.170810
	- akgoelaIndia: 0.163985
	- LuiizP: 0.148954
	- Dr_Arrogant: 0.131552
	- ttlrere: 0.125165
```

### Autocomplete pretraga po prefiksu (opcija 8)

- Pretraga korisničkih imena koja počinju datim prefiksom (case-insensitive), pomoću 
sopstvene Trie implementacije; rezultati sortirani po PageRank vrednosti.

Primer: 

```
Unesite broj ispred željene opcije: 8
Unesite username: le
Mozda ste u potrazi za:
	- Lei_Wifey: 0.001875
	- LeahAnderson13: 0.001329
	- leroymo: 0.001065
	- leonittaa: 0.000404
	- Leandrocdznet: 0.000310
```

### x za izlaz iz programa

- Završava rad programa.

## Napomene o implementaciji

- Svi ID-jevi korisnika čuvaju se kao stringovi (rezultat line.split("|")),
ne kao brojevi.
- PageRank koristi damping faktor 0.85 i prag konvergencije 1e-6.
- Personal PageRank (PPR) koristi teleportaciju isključivo na izvorni čvor
(cold start); korisnik koji ne prati nikoga će imati PPR = 0 za sve ostale
korisnike — preporuke se u tom slučaju oslanjaju na sličnost biografije.
- Sličnost biografije računa se Jaccard koeficijentom nad skupom reči iz bio
polja (lowercase, uklonjena interpunkcija).
- Trie struktura je sopstvena implementacija (bez korišćenja
gotovih biblioteka), gradi se jednom pri pokretanju programa nad svim
username-ovima (lowercase, za case-insensitive pretragu).