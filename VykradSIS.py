
import requests, re, time, lxml, cchardet, concurrent.futures, datetime 
from bs4 import BeautifulSoup

def Scraper(stev_page):
    url = "https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=1&volne=0&pocet=1000&btn_hledat=Hledat&stev_page=" + str(stev_page)

    ##Stáhne webovku 
    stranka = requests.get(url)
    ##Zpracuje přes balíček lxml rychlejí než defaultní balíček v BS4
    soup = BeautifulSoup(stranka.text, "lxml")

    ##Filtruje pouze podstatné informace o zkoušce, len(zkouska) udává počet tagů, řeší dementní design SISu
    RadkyTabulky = soup.findAll("table", class_="tab1")[1].findAll("tr", class_=re.compile("^row"))
    for zkouska in RadkyTabulky: 
            if (len(zkouska) == 32):
                    tdSeznam=zkouska.findChildren("td")
                    i = 0
                    j = 0
                    for tdDite in tdSeznam:
                        if (i == 3 or i == 4 or i == 5 or i == 7 or i == 8):
                            VsechnyZkousky[j].append(tdDite.text)
                            j+=1
                        i+=1


while True:
    ##Hlavní pole, kde se ukládají data v pořadí Typ termínu, Název předmětu, Kapacita, Den konání, Hodina
    VsechnyZkousky = [[], [], [], [], []]
    
    stev_page = 0
    
    stranka = requests.get("https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=0&volne=0&pocet=1000&btn_hledat=Hledat&stev_page=1")
    soup = BeautifulSoup(stranka.text, "lxml")
    ##Zjišťuje počet stránek se zkouškami
    VysledkyZ = soup.find("div", class_="seznam1").findAll("b")[1]
    
    ##Threading zrychlující zpracování dat
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        executor.map(Scraper, range(1, int(int(VysledkyZ.text)/1000 + 2)))

    ##Opakováno každou minutu
    time.sleep(60)
        

        
                    
    





