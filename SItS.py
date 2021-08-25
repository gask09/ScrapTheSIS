
import requests, re, schedule, time, lxml, cchardet, concurrent.futures
from bs4 import BeautifulSoup


def HlavniFunkce():

    VsechnyZkousky = [[], [], [], [], []]
    HlavaTabulky = []
    Predmety = []
    dalsi = True
    stev_page = 0
    NoveVypsaneTerminy = {}
    StareZkousky = []
    NoveZkousky = []
    poradi = {}

    def Scraper(stev_page):
    ## Každé kolo stanovuje novou URL a tak umožňuje projít všech x stran
    
        url = "https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=0&volne=0&pocet=1000&btn_hledat=Hledat&stev_page=" + str(stev_page)

        ## Přes balíček requests a BeautifulSoup je stažen a načten zdrojový html kód pro danou URL
        sezeni = requests.Session()
        stranka = sezeni.get(url)
        soup = BeautifulSoup(stranka.text, "lxml")

        ## Najde všechny řádky tabulky, načte dále ale pouze ty, které obsahují pouze informace o zkoušce (všechny mají 16 párů tagů = 32). Pak všechny informace zapisuje do příslušných listů v VsechnyZkousky
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
    stranka = requests.get("https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=0&volne=0&pocet=1000&btn_hledat=Hledat&stev_page=1")
    soup = BeautifulSoup(stranka.text, "lxml")
    VysledkyZ = soup.find("div", class_="seznam1").findAll("b")[1]
    
                    
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        executor.map(Scraper, range(1, int(int(VysledkyZ.text)/1000 + 2)))

    ## Smyčka, která pro všechny zkoušky/zápočty rozdělí kapacity termínů ze stylu xx/yy do listu [xx, yy], pak je zapíše do hlavní tabulky
    for i in range(len(VsechnyZkousky[0])):
        VsechnyZkousky[0][i] = VsechnyZkousky[0][i].split("/")
        
    #Vytvoří množinu všech předmětů, na které se vypisuje zkouška, bez duplikátů, pak je uspořádá podle abecedy.
    Predmety = set(VsechnyZkousky[1])
    Predmety = sorted(Predmety)
    
    #Vytváří dictionary pro práci s předměty: Každému předmětu přiřazuje čísla řádku, na kterém se vyskytují informace o zkoušce/zápočtu 
    for predmet in Predmety:
        poradi[predmet] =  []

    for a in range(len(VsechnyZkousky[1])):
        poradi[VsechnyZkousky[1][a]].append(a)

    
    ##Blok kódu, který slouží jako kontrola informací získaných z webu, kontrolováno proti naposled uloženým informacím v textovém dokumentu. 
    Soubor = open("ZkAZZWebu.txt", "r")

    ## Z textového dokumentu načte postupně všechny řádky. Pak načítá uložené informace podle toho, jaké klíčové znaky obsahují: >> pro nový předmět, bez ostatních symbolů přímo termíny.
    for line in Soubor.readlines(): 
        if ">>" in line:
            NazevPredmetu = line[2:-1]
            NoveZkousky = []
        else:
            StareZkousky = line[:-3].split("; ")
            for CisloRadku in poradi[NazevPredmetu]:
                NoveZkousky.append(VsechnyZkousky[2][CisloRadku] + ": " + str(VsechnyZkousky[0][CisloRadku][1]) + ", " + VsechnyZkousky[3][CisloRadku] + ", " + VsechnyZkousky[4][CisloRadku])
            if len(StareZkousky) != len(NoveZkousky):
                difference = set(NoveZkousky).symmetric_difference(set(StareZkousky))
                NoveVypsaneTerminy[NazevPredmetu] = difference
                
    Soubor.close()

    if NoveVypsaneTerminy:
        
        Soubor = open("ZkAZZWebu.txt", "w+")
        
        for predmet in Predmety:
            Soubor.write(">>")
            Soubor.write(predmet)
            Soubor.write("\n")
            
            for CisloRadku in poradi[predmet]:  
                Soubor.write(VsechnyZkousky[2][CisloRadku] + ": " + str(VsechnyZkousky[0][CisloRadku][1]) + ", " + VsechnyZkousky[3][CisloRadku] + ", " + VsechnyZkousky[4][CisloRadku] + "; ")
            Soubor.write("\n")
        Soubor.close()



    print(NoveVypsaneTerminy)
    print("Čas: ", end = "")
    print(time.ctime())

    
schedule.every(1).minutes.do(HlavniFunkce)

while True:
    schedule.run_pending()
    time.sleep(1)

        

        
                    
    



