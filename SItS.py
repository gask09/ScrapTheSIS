
import requests, re, schedule, time, lxml, cchardet
from bs4 import BeautifulSoup


def HlavniFunkce():

    VsechnyZkousky = [[], [], [], [], []]
    HlavaTabulky = []
    Predmety = []
    dalsi = True
    stev_page = 0
    AsiNovejTermin = []
        
    ## Smyčka, která iteruje všechny vypsané termíny přes x stran, dokud existuje tlačítko "další"
    while (dalsi == True):
        ## Každé kolo stanovuje novou URL a tak umožňuje projít všech x stran
        stev_page=stev_page+1
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
                                
        ## Na stránce hledá anchor tag třídy link1, který obsahuje text "další". Existuje-li, stránka není poslední a smyčka pokračuje
        PostupDale = soup.findAll("a", class_="link1", text = "další")
        if (PostupDale):
            dalsi = True
        else:
            dalsi = False
    ## Konec smyčky

    ## Smyčka, která pro všechny zkoušky/zápočty rozdělí kapacity termínů ze stylu xx/yy do listu [xx, yy], pak je zapíše do hlavní tabulky
    for i in range(len(VsechnyZkousky[0])):
        RozdeleneKapacity=[]
        Kapacita=""
        for znak in VsechnyZkousky[0][i]:
            if znak.isdigit():
                Kapacita=str(Kapacita)+znak
            elif (znak=="/"):
                RozdeleneKapacity.append(int(Kapacita))
                Kapacita=""
                
        RozdeleneKapacity.append(int(Kapacita))
        VsechnyZkousky[0][i] = RozdeleneKapacity
        
    #Vytvoří množinu všech předmětů, na které se vypisuje zkouška, bez duplikátů, pak je uspořádá podle abecedy. Vytvoří kopii pro pozdější využití
    Predmety = set(VsechnyZkousky[1])
    Predmety = sorted(Predmety)
    #Vyváří duplikát pro další práci

    poradi = dict.fromkeys(Predmety)
    for predmet in Predmety:
        poradi[predmet] =  []

    for a in range(len(VsechnyZkousky[1])):
        poradi[VsechnyZkousky[1][a]].append(a)

    
    ##Blok kódu, který slouží jako kontrola informací získaných z webu, kontrolováno proti naposled uloženým informacím v textovém dokumentu - výhodnější než ukládat v RAM. 
    Soubor = open("ZkAZZWebu.txt", "r")

    ## Z textového dokumentu načte postupně všechny řádky. Pak načítá uložené informace podle toho, jaké klíčové znaky obsahují: >> pro nový předmět, zk:/zp: pak pro kontrolu.
    for line in Soubor.readlines():
        ##Při každém novém >> se vynulují všechny proměnné, načte se nový název předmětu, vypočte se počet celkový počet vypsaných míst a počet vypsaných termínů. Ty pak porovnává s tím, co je v dokumentu, ne však jako čísla, ale stringy 
        if ">>" in line:
            pocetzkousek = 0
            pocetzapoctu = 0
            zkousky = 0
            zapocty = 0
            radky = []
            ##Upraví text tak, aby se zbavil ">>" na uačátku, a "\n" na konci řádku.
            NazevPredmetu = line[2:-1]
            for CisloRadku in poradi[NazevPredmetu]:
                
                if (VsechnyZkousky[2][CisloRadku] == "zkouška"):
                    zkousky+=VsechnyZkousky[0][CisloRadku][1]
                    pocetzkousek+=1
                    
                elif (VsechnyZkousky[2][CisloRadku] == "zápočet/kolokvium"):
                    zapocty+=VsechnyZkousky[0][CisloRadku][1]
                    pocetzapoctu+=1
                    
            

        
        test = str(pocetzkousek) + "/" + str(zkousky)
        test2 = str(pocetzapoctu) + "/" + str(zapocty)
        if "zk:" in line:
            if line[3:-1] != test:
                AsiNovejTermin.append(NazevPredmetu)
                
        if "zp:" in line:
            if line[3:-1] != test2:
                AsiNovejTermin.append(NazevPredmetu)

    Soubor.close()
    

    if (len(AsiNovejTermin)>0):
        Soubor = open("ZkAZZWebu.txt", "w")
        
        for predmet in Predmety:
            Soubor.write(">>")
            Soubor.write(predmet)
            Soubor.write("\n")
            zkousky = 0
            zapocty = 0
            pocetzkousek = 0
            pocetzapoctu = 0
            
            for CisloRadku in poradi[predmet]:
                if (VsechnyZkousky[2][CisloRadku] == "zkouška"):
                    Soubor.write("zkouška: ")
                    zkousky+=VsechnyZkousky[0][CisloRadku][1]
                    pocetzkousek+=1
                    
                elif (VsechnyZkousky[2][CisloRadku] == "zápočet/kolokvium"):
                    Soubor.write("zápočet: ")
                    zapocty+=VsechnyZkousky[0][CisloRadku][1]
                    pocetzapoctu+=1
                    
                Soubor.write(str(VsechnyZkousky[0][CisloRadku][1]) + ", " + VsechnyZkousky[3][CisloRadku] + ", " + VsechnyZkousky[4][CisloRadku])
                Soubor.write("\n")
            if zkousky != 0:
                Soubor.write("zk:" + str(pocetzkousek) + "/" + str(zkousky) + "\n")

            if zapocty != 0:
                Soubor.write("zp:" + str(pocetzapoctu) + "/" + str(zapocty) + "\n")
                
        Soubor.close()



    print(AsiNovejTermin)
    print("Čas: ", end = "")
    print("")
    print(time.ctime())

    
schedule.every(1).minutes.do(HlavniFunkce)

while True:
    schedule.run_pending()
    time.sleep(1)


   
        
        

        
                    
    



