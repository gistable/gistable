from pyquery import PyQuery as S
import urllib
from json import loads, dumps
from os import path, makedirs
"""
Admire the doc made by these fucking twats
http://www.bnf.fr/fr/professionnels/donnees_bnf_recuperables/a.donnees_rdf.html#SHDC__Attribute_BlocArticle7BnF

INPUT CHANGE YEAR RANGE L20 This magazine was discontinued
"""
ROOT_DIR=path.join( path.expanduser("~"), "Docs","Assiette_au_Beurre")
### list the review of the year
try:
    makedirs(ROOT_DIR)
except Exception as e:
    print repr(e)
    pass

from time import sleep
for year in range(1902, 1910):
    list_year = """http://gallica.bnf.fr/ark:/12148/cb327033728/date%s.liste.json""" % year
    ###What THE FUCKING FUCK a json in a <html><body><p> DIE!!! You fucking PIG
    grrr= lambda b_url: loads( S(S("body > P ", S(b_url).html())).html() ) 
    data= grrr( list_year)
    ### etract ALL the review  in a year
    #### OMGWTFBBQ English & french mixed up and relevant data at level 9 !!!!!!!!
    #### 8Mb to extract 1ko of information, YOU ARE MAD!!!!
    list_link = data["PeriodicalPageFragment"]["contenu"]["SearchResultsFragment"]["contenu"]["ResultsFragment"]["contenu"][1:]
    url = lambda cont: cont["title"]["url"]
    desc= lambda cont:cont["title"]["description"]
    target= [ (desc(c), url(c).replace("?",".json?")) for c in list_link ]
    for alb_ind, (album, base_url) in enumerate(target):
    ##Getting the first review
        print album
        print base_url
        sanit=lambda _str: _str.replace("/","_").replace(".","").replace(" ","_")
        alb_dir=sanit("%03d_%s" % (alb_ind, album))
        print "ALBDIR %s" % alb_dir
        im_page=grrr(base_url)
        #### And now a level 4 indirection?!
        im_list = im_page["ViewerFragment"]["contenu"]["PaginationViewerModel"]["url"]
        #### And avoiding a broken bloated linked list schema by using an ajax URL // serendipity
        list_image = grrr(im_list[:-len("image")] + "vertical.json")
        #### I have to fucking retranslate in a picture URL without a correct name?!!!
        reformat = lambda str: str.replace("services/ajax/pagination/page/SINGLE/", "")[:-len("vertical")]+"highres"
        for index,im_url in enumerate([ reformat(el["url"])  for el in list_image["fragment"]["contenu"] ]):
            print "getting %s" % im_url
            try:
                base_dir=path.join(ROOT_DIR,str(year), alb_dir)
                makedirs(base_dir)
            except OSError:
                pass
            dst= path.join(ROOT_DIR, base_dir, "%03d_%s.jpeg" % (index, alb_dir))
            print dst
            if not path.exists(dst):
                with open(dst,"w") as f:
                    f.write(urllib.urlopen(im_url).read())
                sleep(.5)
        ### If you code in this fucking place, I will throw all the universal encyclopedia in your face, motherfucker 
