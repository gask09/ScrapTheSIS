
import requests, re, time, lxml, concurrent.futures, datetime 

from bs4 import BeautifulSoup

VsechnyZkousky = [[], [], [], [], []]

termin = []
DatumDnes = datetime.datetime.today()
def Scraper(stev_page):
    url = "https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=1&volne=0&pocet=1000&btn_hledat=Hledat&stev_page=" + str(stev_page)

    stranka = requests.get(url)
    ##Zdrojový kód je zpracován přes balíček psaný v C - lxml
    soup = BeautifulSoup(stranka.text, "lxml")

    ## Najde všechny řádky tabulky, načte dále ale pouze ty, které obsahují pouze informace o zkoušce (všechny mají 16 párů tagů = 32). Už zde probíhá výběr potřebných dat - níže napsáno
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
    Predmety = []
    stev_page = 0
    StareZkousky = []
    NoveZkousky = []
    Zmena = False
    
    
    ##Získáván zdrojový kód stránky
    stranka = requests.get("https://is.cuni.cz/studium/term_st2/index.php?do=zapsat&fakulta=11310&ustav=&budouci=0&volne=0&pocet=1000&btn_hledat=Hledat&stev_page=1")
    soup = BeautifulSoup(stranka.text, "lxml")
    ##Získáván počet zkoušek, slouží pro rychlejší prohledávání přes následující řádky kódu
    VysledkyZ = soup.find("div", class_="seznam1").findAll("b")[1]
    
    ##Concurrent je balíček pro threading - Významně urychluje práci s BeautifulSoup, dvojnásobné zrychlení bez balíčku. Uplatňuje se spíše při více stránkách
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        executor.map(Scraper, range(1, int(int(VysledkyZ.text)/1000 + 2)))


    ##Smyčka, která pro všechny zkoušky/zápočty rozdělí kapacity termínů ze stylu xx/yy do listu [xx, yy], pak je zapíše do hlavní tabulky, upraví se bordel v datumech a u zkoušek bez časů
    for CisloRadku in range(len(VsechnyZkousky[0])):
        VsechnyZkousky[0][CisloRadku] = VsechnyZkousky[0][CisloRadku].split("/")
        if VsechnyZkousky[4][CisloRadku] == "":
            VsechnyZkousky[4][CisloRadku] = "SZ"
            VsechnyZkousky[3][CisloRadku] = VsechnyZkousky[3][CisloRadku].split(" - ")[1]
        else:
            VsechnyZkousky[3][CisloRadku] = VsechnyZkousky[3][CisloRadku].split(" - ")[0]
        
    with open("ZkAZZWebu.txt", "r", encoding = "UTF-8") as Soubor:
    
    ## Z textového dokumentu načte postupně všechny řádky. Pak načítá uložené informace podle toho, jaké klíčové znaky obsahují: >> pro nový předmět, bez ostatních symbolů přímo termíny odděleny středníkem
        for line in Soubor.readlines(): 
            if ">>" in line:
                ##Třeba osekat řádek: Na začátku >> a na konci je konec řádku
                NazevPredmetu = line[2:-1]
                NoveZkousky = []
            else:
                line = line[:-3]
                StareZkousky = line.split("; ")
                for CisloRadku in range (0, len(VsechnyZkousky[0])):
                    if NazevPredmetu == VsechnyZkousky[1][CisloRadku]:
                        NoveZkousky.append(VsechnyZkousky[2][CisloRadku] + ", " + str(VsechnyZkousky[0][CisloRadku][1]) + ", " + VsechnyZkousky[3][CisloRadku] + ", " + VsechnyZkousky[4][CisloRadku])
                
                
                ##Tento blok kódu funguje tak, že porovnává oba listy, vymaže co mají společné, a pak zůstanou NoveZkousky, které jsou nově vypsané, a StareZkousky, které se už na internetu nenachází
                for i in range (0, len(NoveZkousky)):
                    for j in range(0, len(StareZkousky)):
                        if NoveZkousky[i] == StareZkousky[j]:
                            NoveZkousky[i] = ""
                            StareZkousky[j] = ""
                ##Odstranění uvozovek, předpokládá, že se nebudou vypisovat termíny s úplně stejnými datumy 
                NoveZkousky = list(set(NoveZkousky))
                StareZkousky = list(set(StareZkousky))

                if '' in StareZkousky:
                    StareZkousky.remove('')
                if '' in NoveZkousky:
                    NoveZkousky.remove('')
                    
                    
                ##Formátuje a vypisuje všechny nově zjištěné zkoušky zkoušky 
                if len(NoveZkousky) > 0:
                    print(NazevPredmetu)
                    
                    Zmena = True
                    
                    for termin in NoveZkousky:
                        termin = termin.split(", ")
                        print("Byl přidán nový termín dne: " + termin[2] + " v " + termin[3])
                ##Formátuje výstup pro staré zkoušky, a jestli jsou zrušené zkoušky opravdu zrušené, nebo už proběhly
                if len(StareZkousky) > 0:
                    print(NazevPredmetu)
                    Zmena = True
                    
                    ##Proměnná Tisk slouží pro zmenšení kódu, jestliže je True, program vypíše daný termin z StareZkousky jako smazaný termín
                    for termin in StareZkousky:
                        Tisk = False
                        termin = termin.split(", ")
                        DatumZkousky = termin[2].split(".")
                        DatumZkousky[2] = DatumZkousky[2].split(" - ")[0]
                        if int(DatumZkousky[2]) > DatumDnes.year:
                            Tisk = True
                        elif int(DatumZkousky[2]) == DatumDnes.year:
                            if int(DatumZkousky[1]) > DatumDnes.month:
                                Tisk = True
                            elif int(DatumZkousky[1]) == DatumDnes.month:
                                if int(DatumZkousky[0]) > DatumDnes.day:
                                    Tisk = True
                            
                        if Tisk:
                            print("Byl zrušen termín dne: " + termin[2] + " v " + termin[3])
                        

           
    ##Jestliže došlo ke změně v jakýchkoliv termínech, ubyl, přibyl, bude změna zapsána přepsáním souboru. Je třeba podmiňovat, jinak bych došlo k opotřebení disku. 
    if Zmena: 
        with open("ZkAZZWebu.txt", "w+", encoding = "UTF-8") as Soubor:
            
            ##Asi nějvětší prozatím se vyskytjící chyba, program není schopen registorovat nové předměty, respektive první vydaný termín, protože se v množine Předměty vyskytuje předmět tehdy, kdy má na SISu jednu novou zkoušku
            Predmety = set(VsechnyZkousky[1])
            Predmety = sorted(Predmety)
            
            for predmet in Predmety:
                Soubor.write(">>")
                Soubor.write(predmet)
                Soubor.write("\n")
                ##Najde všechny termíny pro daný předmět a zapíše je ve formátu: Typ termínu, Kapacita, Den konání, Hodina; 
                for CisloRadku in range (0, len(VsechnyZkousky[0])):
                    if predmet == VsechnyZkousky[1][CisloRadku]:  
                        Soubor.write(VsechnyZkousky[2][CisloRadku] + ", " + str(VsechnyZkousky[0][CisloRadku][1]) + ", " + VsechnyZkousky[3][CisloRadku] + ", " + VsechnyZkousky[4][CisloRadku] + "; ")
                Soubor.write("\n")

                
    ##Slouží pro kontrolu, že někde nelítají čísla, což se taky stávalo vinou SISu
    print("Počet zbývajících termínů", end=": ")
    print(len(VsechnyZkousky[1]))
    
    time.sleep(60)
