#!/usr/bin/env python3.6
# coding: utf-8

"""
Çok Satırlı yorum:
Python Guido Van Rossum tarafından 90'ların başında geliştirilmeye
başlanmıştır. 
"""

# Bu da bir tek satırlık yorum örneğidir.

###################################################################
## İlkel Veri Tipleri ve Operatörler
###################################################################

# Sayılar

1071 # => 1071

# Bir hesap makinesi olarak Python3
2 + 2   # => 4
3 - 1   # => 2
2 * 4   # => 8
36 / 6  # => 6.0
7 // 3  # => 2 # Her zaman tamsayı sonuç almak için (iki float arası bölme hariç)
5.0 / 3.0 # => 1.0
10.0 / 3  # => 3.3333333333333335

# Modül İşlemleri (Bölme İşleminden Kalan)
8 % 3 # => 2

# Üs Hesaplama
3 ** 2 # => 9

# Parentezler işlem sırasında önceliklidir sonra matematik kuralları
((4 - 1) + 2) * 3 # => 15
4 - 1 + 2 * 3     # => 9

# Mantıksal Değerler yani True ve False
# not ile karşıt değeri verir: not true değeri false ile eşdeğerdir.


# Mantıksal Operatorler
# and (Sadece iki taraf da true ise true döner
True and False # => False
True and True  # => True

# or (en az iki taraftan biri true ise true döner)
True or False  # => True
False or False # => False

# Python dilinde 0 false bir değerdir.

0 and 1982  # => 0
4 or 0      # => 4
0 == False  # True
1 == True   # True

# == Değerler eşitmi karşılaştırır
1000 == 2 * 500 # => True
100 == 50       # => False
10 == 20 // 2 # => True

# != eşit olmama durumu True döner
10 != 20 // 2 # => False
2 != 4        # => True
1 != 1 # => False

# DAHA FAZLA KARŞILAŞTIRMA
# Küçüktür
10 < 12 # => True
7 < 5   # => False

# Büyüktür
1.0 > 0.5 # => True
2 > 3     # => False

# Küçük veya Eşittir
4 <= 4 # => True
4 <= 5 # => True
6 <= 3 # => False

# Büyük veya eşittir
4 >= 4 # => True
4 >= 5 # => False
6 >= 3 # => True

# Karşılaştırmalar zincirleme olarak yapılabilir

12 < 13 > 10 # => True
2 ** 3 > 7 < 4 * 2 # => True
1 < 5 < 6 # => False

# is iki değişkenin aynı nesneye referans olup olmadığını karşılaştırır
a = [3, 5, 8]
b = a

a is b # => True

# STRING (KARAKTER KATARI)
# Bir string "" ya da '' işaretleri arasında oluşturulur.
"Ben bir garip string tipiyim."
'Sanki ben değil miyim?'

# String veri tipi birbirine eklenebilir
"Benim adım " + "Gökhan ÇAĞLAR"

# + işareti kullanmadan da birleştirmek mümkündür
"Merhaba " "Gökhan"

# Bir string değerin uzunluğunu(içerdiği karakter saıyısı) anlamak için:
len("Uzun ince bir yoldayım") # => 22

# .format bir string değeri biçimlendirmek için kullanılabilir
"{} ile {}".format("Leyla", "Mecnun")

# Yazmaktan tasarruf etmek için de tekrarlı olarak kullanılabilir.
"{0} {1} {0} {2}".format("bir", "varmış", "yokmuş")

# String interpolation yapılacak {} alanı isimlendirilebilirsiniz de
"{isim} sizi aradı ve {neden} için olduğunu söyledi".format(isim="Şakir", neden="minibüs")

# C severler için geleneksel biçimlendirme de mevcut
"%d kg çikolatada %.2f litre %s olsa keşke!" % (1, 0.4576321, "süt")

# Python dilinde None bir nesnedir.
None # => None


# == işaretini None ile karşılaştırma yapmak için kullanmayın
# is kullanmayı tercih edin.
"Erol Büyükburç" == "Saksı" # => False
"Erol Büyükburç" is None    # => False
None is None # => True

# Python ile Dünyaya merhaba diyelim
print("Merhaba Dünya") # => Merhaba Dünya # Burada print fonksiyonunu kullandık

# Varsayılan olarak print fonksiyonu değeri sonuna bir de yeni satır bildirimi ekler
# Elbette biz bu varsayılan davranışı değiştirebiliriz.
print("Merhaba Dünya", end="!") # => Merhaba Dünya!

print("") # => \n # new line(yeni satır)

# Peki ben pek önermesem de kullanıcıdan veri girişi almak isterseniz
kullanici_tarafindan_girilmis_string = input("Lütfen Bir Şey Yaz: ")
print("{} yazdın.".format(kullanici_tarafindan_girilmis_string))
# Küçük bir not: Python 2 sürümü raw_input kullanırdı bu gördüğünüz kod Python 3.x kodudur

# Active Typing desteklendiğinden deklerasyon yoktur (tip veya büyüklük belirtme)
# Sadece atama vardır
# degisken_adi = "değeri"
bir_degisken = 1
print(bir_degisken) # => 1

# Tanımlanmamış bir değişmene erişmek bir exception yaratır
# yani NameError isimli hatayı döndürür
# tanımlanmamis_degisken # => NameError

# Değer atarken if bir ifade gibi kullanılabilir
# Tennary operatörü misali # ileride değineceğim

yas = 18
mekan = "Alkollü"
durum = "İzin verildi!" if yas >= 18 else "yasak"

print(durum) # => İzin verildi!

# Diziler (list) bir veya daha fazla değer grubunu taşıyan değişken türüdür
# Python dilinde diziler değiştirilebilir özelliktedir.(Mutable)
liste = [] # boş bir liste

# Değer içerir biçimde de bir liste tanımlayabiliriz
baska_list = [9, 11]

# append ile listenin sonuna bir değer eklenebilir
liste.append(1) # list şimdi: [1]
liste.append(3) # list şimdi: [1,3]
liste.append(5) # list şimdi: [1,3,5]
liste.append(7) # list şimdi: [1,3,5,7]

# ve tabii ki .pop() ile sondan bir değeri silebiliriz
liste.pop() # => 7 döner ve list şimdi: [1,3,5]
liste.append(9) # => list şimdi: [1,3,5,9]

# Bir dizi(list) iteminin sıra numarası girilerek o değere erişir
# Sayılmaya 0 ile başlanır
liste[0] # => 1
baska_list[1] # => 4

liste[-1] # => 9
liste[-2] # => 5 # - ile sağdan sola doğru

# Dizinin (list) değerlerini alırken büyüklük sınırlarının dışına çıkarsanız
# bu bir exception yaratır Python 3 size IndexError hatasını döner
# list[5] # => Indexerror

# Bir diziyi dilimlere ayırabilirsiniz
liste[1:3] # => [3, 5]

# Başlangıç indeksinden dizi bitimine kadar
liste[2:]  # => [5, 9]

# Dizinin en başından belirtilen bitiş indeksine kadar
liste[:3]  # => [1, 3, 5]

# Her iki itemde bir
liste[::2] # => [1, 5]

# Listenin ters yüz edilmiş hali
liste[::-1] # => [9, 5, 3, 1]

# Bir listenin tek katmanlı tam kopyasını oluşturma
list2 = liste[:]

# Belirtilmiş bir itemi listeden silmek için
# İndeks belirterek listeden silmek
del list2[1] # => list2 şimdi: [1, 5, 9]

# Değer belirterek listeden
list2.remove(9)  # => list2 şimdi: [1, 5]

# Var olmayan bir değeri silmeye çalışırsak
# bu bir exception yaratır ve ValuError döner
# list2.remove(2) # => Valuerror

# Bir dizinin belirtilmiş bir indeksine değer eklemek mümkündür
list2.insert(1, 3) # => list2 şimdi: [1, 3, 5]
list2.insert(3, 7) # => list2 şimdi: [1, 3, 5, 7]

# Bir list iteminin list içindeki indeksini öğrenebiliriz
liste.index(9)  # => 3
list2.index(7) # => 3 

# Listeler birbirine eklenebilir
# Aşağıda list ve list2 listelerinin değeri değişmez:
bir_baska_list = liste + list2 # => [1, 3, 5, 9, 1, 3, 5, 7]

# Bir listenin içine diğer bir liste eklenebilir
list2.extend(baska_list) # => list2 şimdi: [1, 3, 5, 7, 9, 11]

# Bir değerin listede olup olmadığını kontrol edebiliriz
11 in list2 # => True

# len() bize listelerin uzunluğunu da gösterir
print(len(list2)) # => 6

# TUPLE Veri Tipi Yani Değiştirlemez (immutable) Listeler
bir_tuple = (1, 2, 3, 4)

liste[3] = 7 # => list şimdi [1, 3, 5, 7] # listeler değiştirlebilir

# bir_tuple[1] = 4 $ => TypeError # Tuple listeler değiştirilemez

# Bir tuple tanımlamak için tek item içeriyorsa sonrasında virgul olmalıdır eğer boş bir tuple değilse
# type bize bir değişken ya da ifadenin türünü döner
type((5)) # => <class 'int'>
type((5,)) # => <class 'tuple'>
type(()) # => <class 'tuple'>

# Değer değiştirmeyen dizi işlemleri bir tuple üzerinde uygulanabilir
len(bir_tuple) # => 4
yeni_tuple = bir_tuple + (5, 6, 7, 8) # => (1, 2, 3, 4, 5, 6, 7, 8)
yeni_tuple[:5] # => (1, 2, 3, 4, 5)
8 in yeni_tuple # => True

# Tuple ya da list değerlerini değişkenlere dağıtabilirsiniz
a, b, c, d = bir_tuple

print("a: {}".format(a)) # => a: 1
print("b: {}".format(b)) # => b: 2
print("c: {}".format(c)) # => c: 3
print("d: {}".format(d)) # => d: 4

x, *y, z = (1, 2, 3, 4, 5, 6, 7, 8)

print("x: {}".format(x)) # => x: 1
print("y: {}".format(y)) # => y: [2, 3, 4, 5, 6, 7]
print("z: {}".format(z)) # => z: 8

d, e = (5, 6)

# Python dilinde iki değişkenin değerini birbiri ile takas etmek çok kolaydır
e, d = d, e # => şimdi d = 6 ve e = 5

# SÖZLÜKLER (Dictionaries)
# Sözlükler birer anahtar ve değer eşleştirmesidir en basıt anlatımıyla
bos_sozluk = {}

# Örnek Sözlük
kimlik = {"tc": 11111111111, "isim": "Gökhan", "soyisim": "Çağlar", "yaş": 35}
rastgele = {"bir": 1, "iki": 2, "on": 10, "yirmi": 20}

# Sözlüklürde anahtar olarak belirlediğiniz değerlerin değiştrilemez (immutable) olmasına
# özen gösterin. Değiştirlemez tipler: int, float, string, tuple
# boyle_sozluk_olmaz = {[3, 5, 8]: "358"}
dogru_ornek = {(3,5,8): [3, 5, 8]}

# Değerler listlerdeki gibi [] ile alınır ancak içine index değil anahtar yazarız
kimlik["isim"] # => Gökhan

# .keys ile bir sözlüğün tüm değerleri döndürülebilir.
# Aynı şekilde tüm değerleri döndürmek için: .values
# Bu değerleri list içinde tutabiliriz
list(kimlik.keys())
list(kimlik.values())

# in ile bir anahtarı içerip içermediğini kontrol edebiliriz
"isim" in kimlik # => True
"adres" in kimlik # => False

# Var olmayan bir anahtarın değerine erişmeye çalışmak hata döndürür
# kimlik["adres"] $ => KeyError

# Hatadan kaçınmak için get() kullanılır
kimlik.get("yaş") # => 35
kimlik.get("adres") # => None

# get() ile değer bulanamazsa varsayılan bir değer döndürlmesini belirtebilirsiniz
kimlik.get("adres", "İstanbul") # => İstanbul
kimlik.get("doğumyılı", 1982) # => 1982

# setdefault() ile verilen key bulunamazsa belirttiğiniz değerle eklenmesini sağlayabilirsiniz
kimlik.setdefault("doğumyılı", 1982) # => sözlüğe "doğumyılı": 1982 ekledi

# Bir sözlüğe item eklemek
kimlik.update({"adres":"İstanbul"}) # => adres: İstanbul eşleştirmesini ekledi
kimlik["eğitim"] = "Üniversite" # Diğer yol # => eğitim: Üniversite eşleştirmesini ekledi

# Sözlükten Item Silmek
del kimlik["eğitim"] # => eğitim keyini sözlükten sildi

# Python 3.5 Sürümünden bu yana tamamlayıcı motodlar kullanılabilir
{'a': 1, **{'b': 2}}  # => {'a': 1, 'b': 2}
{'a': 1, **{'a': 2}}  # => {'a': 2}

# Setler (Matematikteki kümeler gibi)
# set()
bos_set = set()
# Bir sürü değer ile bir set oluşturmak biraz sözlük oluşturmaya benzer
bir_set = {1, 2, 3, 4}

# Sözlüklerin anahtalarında olduğu gibi setlerin itemleri değiştirilemez olmalıdır
# hatali_set = {[1], 1}
set_gibi_set = {(1,), 1}

# Bir sete item eklemek için
bir_set.add(5) # => {1, 2, 3, 4, 5}

# İki setin kesişimini almak için
baska_bir_set = {3, 4, 5, 6}
bir_set & baska_bir_set # => {3, 4, 5}

# İki setin birleşimini almak için
bir_set | baska_bir_set # => {1, 2, 3, 4, 5, 6}

# İki setin birbirinden farkını almak için -
{1, 2, 3, 4} - {2, 3, 5} # => {1, 4}

# İki setin birbirinden simetrik farkını almak için ^
{1, 2, 3, 4} ^ {2, 3, 5}  # => {1, 4, 5}

# Bir set diğer setin kapsayını mı?(superset) Matematikteki üst küme mantığı
{1, 2} >= {1, 2, 3} # => False

# Bir set diğer setin kapsananı/alt seti mi?(subset) Matematikteki alt küme mantığı
{1, 2} <= {1, 2, 3} # => True

# Bir item set içinde mevcut mu diye kontrol etmek için
1 in bir_set # => True
7 in bir_set # => False


####################################################
## Akış Kontrolü ve Döngüler
####################################################

# Bir değişken oluşturulalım
bir_degisken2 = 2

# Python dilinde if değiminin girintileri büyük önem taşır
# Aynı hizdaki girinti aynı kod bloğu içerisinde kabul edilir.
# Aşağıdaki örnek "Ondan Küçük Bir Sayı." yazar ekrana
if bir_degisken2 > 10:
    print("Ondan Büyük Bir Sayı.")
elif bir_degisken2 < 10:
    print("Ondan Küçük Bir Sayı.")
else:
    print("Ona Eşit Bir Sayı.")


"""
For döngüsü listeler üzerinde iterasyon yapar
Aşağıdaki Örnek Ekrana Yazdırır:
    Köpek bir memeli hayvandır.
    Kedi bir memeli hayvandır.
    Fare bir memeli hayvandır.
"""
for hayvan in ["Köpek", "Kedi", "Fare"]:
    print("{} bir memeli hayvandır.".format(hayvan))

"""
"range(sayı)" bir sayı döngüsü döndürür.
Aşağıdaki Örnek Ekrana Yazdırır:
0
1
2
3
"""
for i in range(4):
    print(i)

"""
"range(alt sınır, üst sınır)" alt sınırdan üst sınıra kadar olan sayıları döndürür
Aşağıdaki Örnek Ekrana Yazdırır:
4
5
6
7
"""
for i in range(4, 8):
    print(i)

"""
"range(alt sınır, üst sınır, adım)" alt sınırdan üst sınıra kadar olan sayıları adım kadar
atlayıp da döndürür.
Aşağıdaki Örnek Ekrana Yazdırır:
4
6
"""
for i in range(4, 8, 2):
    print(i)

"""
while döngüleri verilen koşul karşılanmayıncaya kadar döner.
Aşağıdaki Örnek Ekrana Yazdırır:
0
1
2
3
"""
sayac = 0
while sayac < 4:
    print(sayac)
    sayac += 1  # Kısaltılmış olarak: x = x + 1

# Hataları yakalamak için try/except blokları kullanılabilir
# try:
#    # Bir hata döndürmek istersek 'raise' ifadesini kullanırız
#    raise IndexError("Bu bir Indeks Hatası")
#    pass
# except (TypeError, NameError):
#    pass # Birden fazla exception kullanıcaksa kullanımı şart
# else:
#    print("Her şey yolunda!") # Try içerisindeki kod hiç exception dönmezse çalıştırılacak
# finally:
#    print("Burada kaynakları temizliyoruz.")

# Kaynakları temizlemek için try/finally yerine bir statement da kullanabilirsiniz
# with open("dosyam.txt") as d:
#     for satir in d:
#         print(satir)

# Python size Itarable özelliğini sunar
# Itarable ardıllık için kullanılabilen bir nesnedir.
# range ile döndürülen sayılar da Iterable nesnesidir.
iterasyon_icin_sozluk = {"bir": 1, "iki": 2, "üç": 3}
iterable_nesne = iterasyon_icin_sozluk.keys()
print(iterable_nesne) # => dict_keys(['bir', 'iki', 'üç']) # bu bir itarable nesnedir

# O halde üzerinde döngü oluşturailmeliyiz
for i in iterable_nesne:
    print(i) # bir, iki, üç yazdıracak

yeni_iterator = iter(iterable_nesne) 

# Iterator nesnemiz üzerinde hangi konuma vardığımızı tutabilir
next(yeni_iterator) # => bir

# devam edelim
next(yeni_iterator) # => iki
next(yeni_iterator) # => üç

# Eğer tüm verilerini döndürdükten sonra veri çekmeye çalışırsak
# next(iterable_nesne) # => StopIteration hatasını döner
# list ile bir iterator nesnesinin tüm elemanlarını tutabilirsiniz
list(iterasyon_icin_sozluk.keys())

####################################################
## Fonksiyonlar
####################################################

# Bir fonksiyon tanımlamak için def ifadesini kullanırız
def topla(x, y):
    print("x {} sayısıdır, y de {} sayısıdır.".format(x, y))
    return x + y

# Bir fonksiyonu parametreler ile çağırmak
topla(5, 4) # => 9

# Anahtar sözcük argümanıyla da fonksiyon çağrılabilir
topla(y=2, x=1) # => 3

# Değişen sayıdaki argümanları da bir fonksiyna parametre alabilirsiniz.
def birsuruarguman(*args):
    return args

birsuruarguman(1, 3, 5) # => (1, 3, 5)

# Değişken sayıda anahtar sözcük argümanı da alınabilir
def birsurukeyword_args(**kwargs):
    return kwargs

# Hadi fonksiyonumuzu çağıralım
birsurukeyword_args(**{"tuz": "gölü", "marmara": "denizi"}) # => {"tuz": "gölü", "marmara": "denizi"}

# İkisi bir arada da mümkün
def hep_beraber(*args, **kwargs):
    print(args)
    print(kwargs)

hep_beraber(1, 2, 3, {"tuz": "gölü", "marmara": "denizi"})

"""
(1, 2, 3)
{"tuz": "gölü", "marmara": "denizi"}
"""
# Bir dizi değişkenini *args parametresine vermek için değişken adının başına * işareti eklenir
# Bir sözlük değişkenini *kwargs parametresine vermek için değişken adının başına ** işareti eklenir
args = [1, 2, 3, 4, 5, 6]
kwargs = {"bir": 1, "iki": 2, "on": 10, "yirmi": 20}
hep_beraber(*args, **kwargs)

# Bir fonksiyonla birden fazla değer return edersek tuple içersinde dönerler
def cevir(x, y):
    return y, x # (y, x) döner

cevrilecek_x = 1
cevrilecek_y = 2

cevrilecek_x, cevrilecek_y = cevir(cevrilecek_x, cevrilecek_y)

# ÖNEMLİ NOT: BİR FONKSİYONUN İÇİNDE TANIMLANAN BİR DEĞİŞKEN SADECE O FONKSİYONUN İÇİNDE ERİŞİLEBİLİRDİR.
# global ÖN TAKISI İLE BİR DEĞİŞKEN YARATIRSANIZ HER YERDEN ERİŞİLEBİLİR OLUR ANCAK ÖZEL DURUMLAR HARİCİNDE
# KESİNLİKLE ÖNERİLMEZ

# Python birinci sınıf fonksiyonlara da sahiptir (bkz. fonksiyonel programlama)
def ekleyici_yap(x):
    def ekleyici(y):
        return x + y
    return ekleyici

iki_ekleyici = ekleyici_yap(2)
iki_ekleyici(1) # => 3

# Aynı zamanda isimsiz fonksiyonları da destekler
(lambda x: x > 2)(3) # => True
(lambda x, y: x ** 2 + y ** 2)(2, 3) # => 13

# Yerleşik olarak high-order fonksiyon desteği vardır
list(map(iki_ekleyici, [1, 2, 3]))          # => [11, 12, 13]
list(map(max, [1, 2, 3], [4, 2, 1]))  # => [4, 2, 3]

list(filter(lambda x: x > 5, [3, 4, 5, 6, 7]))  # => [6, 7]

# Liste gösterimini daha güzel görünen map ve filter uygulamaları için de kullanabilirsiniz
[iki_ekleyici(i) for i in [1, 2, 3]]         # => [11, 12, 13]
[x for x in [3, 4, 5, 6, 7] if x > 5]  # => [6, 7]

# set ve sözlük içiçe geçişleri de mümkün elbet
{x for x in 'abcddeef' if x not in 'abc'}  # => {'d', 'e', 'f'}
{x: x**2 for x in range(5)}  # => {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

####################################################
## Modüller
####################################################

# Modülleri import edebiliriz
import math
print(math.sqrt(16))  # => 4.0

# Bir modülden tüm fonksiyonları import etmek için *
# from math import *
# Bir modülden belli fonksyonları da tercihimize göre alabiliriz
from math import ceil, floor
print(ceil(3.7))   # => 4.0
print(floor(3.7))  # => 3.0

# Modül adlarını kısaltabiliriz
# import math as m
# math.sqrt(16) == m.sqrt(16)  # => True

# Python modüllerinde esasında bildiğimiz Pyton betikleridir.
# Yani kendi kodlarınızı da betik olarak içe aktarabilirsiniz.
# Modül adı dosya adı ile aynı olmalıdır.

# Bir Modülün davranış ve niteliklerini görmek için
# dir(math)


####################################################
## Sınıflar
####################################################

# Bir sınıf tanımlamak için "class" ifadesini kullanırız
    # Bir sınıf niteliği yani orjinal ifadesi ile attribute 
    # sınıfın tüm örneklerince (instance) paylaşılır.
    # Temel bir initializer (nesne için inşa edici) sınıf örneklediğinde
    # çağrılır. Unutmayın ki, başlangıç ve sonda yer alan çift _ işareti
    # nesneleri ya da Python tarafindan kullanılan attributeleri ya da
    # kullanıcı kontrolündeki Namespace ve methodları işaret eder: __init__,
    # __str__, __repr__ vs. özel methodlardır.
    
class Insan:
    tur = "Homo Sapiens"

    def __init__(self, isim):
        # Bir argümanı nesnenin isim niteliğine atayacağız
        self.isim = isim
        self._yas = 0

    # Instance Method 
    def der_ki(self, mesaj):
        print("{isim}: {msj}".format(isim = self.isim, msj = mesaj))

    # Başka bir instance method
    def sarki_soyle(self):
        return 'Akdeniz Akşamları'

    # Bir sınıf methodu tüm örneklerce(bu sınıd ile oluşturulan nesneler) paylaşılır
    @classmethod
    def turu_ogren(cls):
        return cls.tur

    # Bir static method sınıf ya da instance referansı olmadan çağrılabilir
    @staticmethod
    def homurdan():
        return "Homurtu"

    # Bir getter @property eklenerek nitelik değerini salt okunur olarak almanızı sağlar
    @property
    def yas(self):
        return self._yas

    # Bir setter niteliğin değerini değiştirmenizi sağlar
    @yas.setter
    def yas(self, yas):
        self._yas = yas

    # Deleter ile niteliği silebiliriz
    @yas.deleter
    def yas(self):
        del self._yas


# Bir python yorumlayıcısı kaynak dosyayı okur ve tüm kodu çalıştırır.
# __name__ ile programın doğrudan çalıştırıldığında çalışmasını sağlarız
# böylece import edilince otomatik çalışmamış olur.
if __name__  == '__main__':
    # Bir nesne inşa edelim
    g = Insan("George")
    j = Insan("John")
    
    g.der_ki("Merhaba!")
    j.der_ki("Hello!")

    # Sınıf methodu çağrısı
    g.der_ki(g.turu_ogren())
    j.der_ki(j.turu_ogren())

    # Tüm nesnelerce paylaşılacak niteliği değiş
    Insan.tur = "Homo neanderthalensis"
    
    # Paylaşılan nitelik değiştikten sonra
    g.der_ki(g.turu_ogren())
    j.der_ki(j.turu_ogren())

    # Static method çağrısı
    print(Insan.homurdan())

    # Static method oluşturulmuş nesne örneği üzerinden çağrılmaz
    # print(g.homurdan()) # TypeError döndürür

    # Nitelikleri güncelleyelim
    g.yas = 35

    # Niteliği alalım
    g.der_ki(g.yas)

    # Niteliği silelim
    del g.yas


####################################################
## Çoklu Kalıtım
####################################################
class Yarasa:

    tur = 'Memeli'

    def __init__(self, ucabilir=True):
        self.uc = ucabilir

    def der_ki(self, msj):
        msj = 'Yarasa Sesi'
        return msj

    def sonar(self):
        return ')))...((('
if __name__ == '__main__':
    y = Yarasa()
    y.der_ki('Merhaba!')
    print(y.uc)

# Eğer ayrı bir dosyada olsa idi sınıfflarımız misal yarasa.py ve insan.py
# from insan import Insan
# from yarasa import Yarasa

# Batman yarasa ve insan nıflarından miras alır
class Batman(Insan, Yarasa):

    tur = 'Süper Kahraman'

    def __init__(self, *args, **kwargs):
        # Genel olarak nitelikleri almak için super kullanılır:
        # super(Batman, self).__init__(*args, **kwargs)
        # Burada çoklu kalıtım kullanıyoruz ve super() yalnızca
        # aşağıda yer alan MRO sıfında kullanılabilir.
        # Bu yüzden tüm miras bıraknlar için __init__ çağırmaktansa
        # *args ve **kwargs kullanımı argüman geçmenin en temiz yoludur.
        Insan.__init__(self, 'isimsiz', *args, **kwargs)
        Yarasa.__init__(self, *args, ucabilir=False,**kwargs)
        # isim degerinin üzerine yazalım
        self.isim = 'Bruce Wayne'

    def sarki_soyle(self):
        return 'nan nan nan nan nan batman!'

if __name__ == '__main__':

    sup = Batman()
    
    if isinstance(sup, Insan):
        print('Ben bir insanım!')
    if isinstance(sup, Yarasa):
        print('Ben bir yarasayım!')
    if type(sup) is Batman:
        print('I am Batman')

    # Bu attribute dinamiktir ve güncellenebilir
    print(Batman.__mro__)       # => (<class '__main__.Batman'>, <class 'human.Human'>, <class 'bat.Bat'>, <class 'object'>)
    # Ebeveyn methodu çağırmak kendi sınıf niteliğini(attribute) döndürür
    print(sup.turu_ogren())

    # Üzerine yazdığımız methodu çağıralım
    print(sup.sarki_soyle())

    # Insan için olan bir methodu çağıralım
    sup.der_ki('Kabul ediyorum.')

    # 2. ebeveynin sahip olduğu methodu çağıralım
    print(sup.sonar())

    # Miras alınmış sınıf niteliği
    sup.yas = 100
    print(sup.yas)

####################################################
## Detaylar
####################################################

# Genarator kullanımı
def numarayi_katmerle(iterable):
    for i in iterable:
        yield i + i

# Genaratorler bellek tasarrufu sağlar çünkü veriyi sadece ihtiyaç duyulduğunda yüklerler
for i in numarayi_katmerle(range(1, 50000)): # range bir genarator
    print(i)
    if i >= 40:
        break

# Bir genarator list gosterimi ile de oluşturulabilir
degerler = (-x for x in [1,2,3,4,5,6])
for x in degerler:
    print(x)

# Dekoratörler
# Bu örnekte 'dilen' 'soyle'yi sarmalar. Eğer lutfen_de True ise
# dönen mesaj değişecek
from functools import wraps

def dilen(hedef_fonksiyon):
    @wraps(hedef_fonksiyon)
    def wrapper(*args, **kwargs):
        msj, lutfen_de = hedef_fonksiyon(*args, **kwargs)
        if lutfen_de:
            return "{} {}".format(msj, "Lütfen çok fakirim!")
        return msj
    return wrapper

@dilen
def soyle(lutfen_de=False):
    msj = 'Bana bir bira ısmarlar mısın?'
    return msj, lutfen_de

print(soyle())
print(soyle(lutfen_de=True))
##################################SON##################################
