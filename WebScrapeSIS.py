import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
VsechnyZkousky = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], ['Něco navíc']]

##dictFakult = {}


##URL="https://is.cuni.cz/studium/term_st2/index.php?"
##page=requests.get(URL)
##
##soup = BeautifulSoup(page.content, "html.parser")
##
##Fakulty = soup.find("select", {"id": "fakulta"})
##Fakulta = Fakulty.findChildren()
##
##for fakultu in Fakulta:
##	dictFakult.update({fakultu.text: fakultu["value"]})
##
##print (dictFakult)


stranka = requests.get("https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=0&budouci=1&volne=0&volne=1&pocet=20&btn_hledat=Hledat")

soup = BeautifulSoup(stranka.content, "html.parser")

TabSPred = soup.findAll("table", class_="tab1")[1] 
ZahTab = soup.find("tr", class_="head1")
Prvky=ZahTab.findChildren()
Zkouska = TabSPred.findAll("tr", class_=re.compile("^row"))
i=0
for deti in Prvky:
    VsechnyZkousky[i].append(deti.text)
    i=i+1

## Smyčka, která z části zdrojového html kódu
for zkouska in Zkouska: 
    if (len(zkouska)==32):
        i=0
        tdSeznam=zkouska.findChildren("td")
        for tdDite in tdSeznam:
            VsechnyZkousky[i].append(tdDite.text)
            i=i+1
        
print(VsechnyZkousky)
