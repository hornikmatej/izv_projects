#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Projekt 1 do predmetu IZV
# Autor: xhorni20@fit.vut.cz (Matej Hornik)

import zipfile
import numpy as np
import requests
import os
import sys
from bs4 import BeautifulSoup
from zipfile import ZipFile
import csv
from io import TextIOWrapper
import pickle
import gzip
from time import time

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers  -- Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions -- Dictionary s nazvy kraju : nazev csv souboru
        data_types -- Datove typy jednotlivych hlaviciek podla zoznamu headers
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    data_types = ["U12", "i1", "i4", "M8[D]", "i1", "U4", "i1", "i1", "i1", "i1", "i1", "i1", "i2", "i2", "i2", "i2", "i8", 
                "i1", "i1", "i1", "i1", "i1", "i1", "i1", "i1", "i1", "i1", "i1", "i1", "i2", "i1", "i1", "i1", "i1", "U2",
                "i1", "i1" , "i1", "i1", "i1", "i1", "i8", "i1", "i1", "i1", "f8", "f8","f8","f8","f8","f8","U32","U32",
                "U32","U32","U32","U32","U32","U32","U32","U32","U32","U32", "i1"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        """Inicializacia triedy a spracovanie vstupnych dat 

        Keyword arguments:
        url -- stranka z ktorej sa budu stahovat data (default "https://ehw.fit.vutbr.cz/izv/")
        folder -- zlozka do ktorej sa budu ukladat docasne data, nemusi existovat (default "data")
        cache_filename -- meno suboru v specifikovanej zlozke, za '{}' sa doplni kod kraja (default "data_{}.pkl.gz")
        """

        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        self.cached_regions = {
        "PHA": None,
        "STC": None,
        "JHC": None,
        "PLK": None,
        "ULK": None,
        "HKK": None,
        "JHM": None,
        "MSK": None,
        "OLK": None,
        "ZLK": None,
        "VYS": None,
        "PAK": None,
        "LBK": None,
        "KVK": None,
        }   

    def download_data(self):
        """Zo stranky sa stiahnu zip subory s datami
        """
        # ak neexistuje adresar, vytvorime ho
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}
        with requests.Session() as s:
            page = s.get(self.url, headers = headers)
            # vyhladanie linkov cez button na stranke
            result = BeautifulSoup(page.text, "html.parser")
            button_tags = result.findAll(class_='btn btn-sm btn-primary')
            last_month = button_tags[-1].get('onclick').split('\'')[1]

            for tag in button_tags:
                file_name = tag.get('onclick').split('\'')[1]
                numbers = sum(c.isdigit() for c in file_name)
                # stiahne sa len posledny mesiac v kazdom roku
                if numbers == 4 or file_name == last_month:
                    download_url = self.url + file_name
                    download_request = requests.get(download_url, stream=True)
                    # ulozenie dat do suboru
                    with open(os.path.join(self.folder, file_name.split('/')[1]), 'wb') as fd:
                        for chunk in download_request.iter_content(chunk_size=512):
                            fd.write(chunk)


    def parse_region_data(self, region):
        """Spracuju sa data do numpy poli zo zip suborov v zlozke

        Argumetns:
            region -- nazov regionu pre ktory sa spracuju data zo zip suboru
        """
        
        # kontrola spravnosti regionu
        if region not in self.regions.keys():
            print(f"ERROR: {region} nie je platna skratka regionu", file=sys.stderr)
            return
        # ak neexistuje adresar tak stiahnem data
        if not os.path.exists(self.folder):
            self.download_data()
        # ulozim si ake subory sa nachadzaju v zlozke, popripade znova stiahnem data
        onlyfiles = [f for f in os.listdir(self.folder) if os.path.isfile(os.path.join(self.folder, f))]
        zip_files = [file for file in onlyfiles if file.endswith(".zip")]
        if len(zip_files) == 0:
            self.download_data()

        np_arrays_result = [np.empty(0, dtype=self.data_types[i]) for i in range(len(self.headers))]


        # prechadzam zip subory
        for zip_file in zip_files:
            # otvorim si zip pomocou ZipFile
            with ZipFile(os.path.join(self.folder, zip_file), 'r') as zip:
                # otvorim si subor so zadanym regionom
                with zip.open(self.regions[region] + ".csv", 'r') as file:

                    reader = csv.DictReader(TextIOWrapper(file, "cp1250"), fieldnames=self.headers, delimiter=';')
                    no_rows = len(list(reader))
                    # kvoli zisteniu poctu riadok sa musim vratit na zaciatok suboru
                    file.seek(0)
                    # print(f"tento zip {zip_file} a tento subor {file.name} ma {no_rows}")
                    
                    np_arrays = [np.empty(no_rows, dtype=self.data_types[i]) for i in range(len(self.headers))]
                    for row_n, row in enumerate(reader):
                        # prechadzam kazdy stlpec v riadku
                        for col in range(len(self.headers)):
                            if row[self.headers[col]] == '' and "U" not in self.data_types[col]:
                                # chybajuce hodnoty v stlpoch
                                if "i" in self.data_types[col]:
                                    # chyba integer
                                    np_arrays[col][row_n] = -1
                                if "M" in self.data_types[col]:
                                    # chyba datum
                                    np_arrays[col][row_n] = np.datetime64("nat")
                                if "f" in self.data_types[col]:
                                    # chyba float
                                    np_arrays[col][row_n] = np.nan
                            # nastavim numpy datum
                            if "M" in self.data_types[col]:
                                np_arrays[col][row_n] = np.datetime64(row[self.headers[col]])
                            # nastavim floaty
                            elif "f" in self.data_types[col]:
                                try:
                                    np_arrays[col][row_n] = np.char.replace(row[self.headers[col]], ",", ".").astype("f")
                                except ValueError:
                                     np_arrays[col][row_n] = np.nan
                            # nastavim integere
                            else:
                                try:
                                    np_arrays[col][row_n] = row[self.headers[col]]
                                except ValueError:
                                     np_arrays[col][row_n] = -1
                    
                    # skontrolujem este duplicity
                    x = np_arrays[0].copy() #p1
                    indices, counts = np.unique(x, return_counts=True)
                    duplicates = indices[np.argwhere(counts > 1).flatten()]
                    # pre kazdu duplicitu
                    for duplic in duplicates:
                        # indexy odkial sa budu vymazavat
                        # ponecham len prvy vyskyt p1, ostatne vymazem
                        z = np.where(duplic == x)[0][1:]
                        # prejdem kazdy zoznam a vymazem duplicitne riadky
                        for i in range(len(np_arrays)):
                            np_arrays[i] = np.delete(np_arrays[i], z)

                    # naplnim finalne numpy arraye
                    for i in range(len(np_arrays_result)):
                            np_arrays_result[i] = np.append(np_arrays_result[i], np_arrays[i])
                    
        # vytvorim slovnik
        dict_data = {}
        region_array = np.full(np_arrays_result[0].size, region, dtype="U3")
        # naplnim slovnik numpy poliami
        for i in range(len(np_arrays_result)):
            dict_data[self.headers[i]] = np_arrays_result[i]
        # pridam posledny stlpec s kodom regionu
        dict_data["region"] = region_array
        
        return dict_data

    def get_dict(self, regions=None):
        """Vytvori slovnik dat pre dane regiony a ulozi data do cache pamate 
        a taktiez do cache suborov ak este neexistuju
        
        Keyword arguments:
        regions -- Pre ktore regiony sa ma vytvorit slovnik a ulozit do cache (default "None") - vsetky regiony
        """
        # ak je regions None -> nastavim vsetky regiony
        if regions is None:
            regions = self.regions.keys()
        else:
            # skontrolujem spravnost zadanych regionov
            if any(region not in self.regions.keys() for region in regions):
                print(f"ERROR: Zadany zoznam regionov obsahuje neplatny region", file=sys.stderr)
                return
        # vytvorenie slovnika a poli pre regiony
        data_dict_stacked = {}
        for i in range(len(self.headers)):
            data_dict_stacked[self.headers[i]] = np.empty(0, dtype=self.data_types[i])
        data_dict_stacked["region"] = np.empty(0, dtype="U3")
        
        for region in regions:
            # ak je region ulozeny v pamati
            if self.cached_regions[region] is not None:
                # prechadzam kazdu hlavicku a pridavam do velkeho slovniku
                for key in self.cached_regions[region].keys():
                    data_dict_stacked[key] = np.append(data_dict_stacked[key], self.cached_regions[region][key])
                continue

            # ak je v cache subore
            cache_filename = os.path.join(self.folder, self.cache_filename.replace("{}",region))
            if os.path.exists(cache_filename):
                # nacitam data z cache suboru
                with gzip.open(cache_filename, 'rb') as f_out:
                    cached_region = pickle.load(f_out)
                # ulozim si ich do vysledneho slovnika
                for key in cached_region.keys():
                        data_dict_stacked[key] = np.append(data_dict_stacked[key], cached_region[key])
                # ulozim si ich do pamate
                self.cached_regions[region] = cached_region
                continue

            # region je treba nacitat s parse_region_data
            parsed_region = self.parse_region_data(region)
            # ulozim si ich do vysledneho slovnika
            for key in parsed_region.keys():
                    data_dict_stacked[key] = np.append(data_dict_stacked[key], parsed_region[key])
            # ulozim si ich do pamate
            self.cached_regions[region] = parsed_region
            # ulozim si do cache suboru
            pickled = pickle.dumps(parsed_region)
            with gzip.open(cache_filename, 'wb', compresslevel=1) as f_out:
                f_out.write(pickled)
            
        return data_dict_stacked

    def print_colums_info(self):
        """Na standardny vystup sa vypisu informacie o jednotlivych hlavickach
        """

        colums_info = {"p1" : "IDENTIFIKAČNÍ ČÍSLO", "p36" : "DRUH POZEMNÍ KOMUNIKACE", "p37" : "ČÍSLO POZEMNÍ KOMUNIKACE",
                    "p2a" : "DÁTUM", "weekday(p2a)" : "DEŇ V TÝŽDNI", "p2b" : "ČAS", "p6" : "DRUH NEHODY", 
                    "p7" : "DRUH SRÁŽKY JEDOUCÍCH VOZIDEL", "p8" : "DRUH PEVNÉ PŘEKÁŽKY", "p9" : "CHARAKTER NEHODY",
                    "p10" : "ZAVINĚNÍ NEHODY", "p11" : "ALKOHOL U VINÍKA NEHODY PŘÍTOMEN", "p12" : "HLAVNÍ PŘÍČINY NEHODY",
                    "p13a" : "USMRCENO OSOB", "p13b" : "TĚŽCE ZRANĚNO OSOB", "p13c" : "LEHCE ZRANĚNO OSOB", 
                    "p14" : "CELKOVÁ HMOTNÁ ŠKODA", "p15" : "DRUH POVRCHU VOZOVKY", "p16" : "STAV POVRCHU VOZOVKY V DOBĚ NEHODY",
                    "p17" : "STAV KOMUNIKACE", "p18" : "POVĚTRNOSTNÍ PODMÍNKY V DOBĚ NEHODY", "p19" : "VIDITELNOST", 
                    "p20" : "ROZHLEDOVÉ POMĚRY", "p21" : "DĚLENÍ KOMUNIKACE", "p22" : "SITUOVÁNÍ NEHODY NA KOMUNIKACI",
                    "p23" : "ŘÍZENÍ PROVOZU V DOBĚ NEHODY", "p24" : "MÍSTNÍ ÚPRAVA PŘEDNOSTI V JÍZDĚ", 
                    "p27" : "SPECIFICKÁ MÍSTA A OBJEKTY V MÍSTĚ NEHODY", "p28" : "SMĚROVÉ POMĚRY", "p34" : "POČET ZÚČASTNĚNÝCH VOZIDEL", 
                    "p35" : "MÍSTO DOPRAVNÍ NEHODY", "p39" : "DRUH KŘIŽUJÍCÍ KOMUNIKACE", "p44" : "DRUH VOZIDLA", 
                    "p45a" : "VÝROBNÍ ZNAČKA MOTOROVÉHO VOZIDLA", "p47" : "ROK VÝROBY VOZIDLA", "p48a" : "CHARAKTERISTIKA VOZIDLA ", 
                    "p49" : "SMYK", "p50a" : "VOZIDLO PO NEHODĚ", "p50b" : "ÚNIK PROVOZNÍCH, PŘEPRAVOVANÝCH HMOT", 
                    "p51" : "ZPŮSOB VYPROŠTĚNÍ OSOB Z VOZIDLA", "p52" : "SMĚR JÍZDY NEBO POSTAVENÍ VOZIDLA", "p53" : "ŠKODA NA VOZIDLE", 
                    "p55a" : "KATEGORIE ŘIDIČE", "p57" : "STAV ŘIDIČE", "p58" : "VNĚJŠÍ OVLIVNĚNÍ ŘIDIČE", "p5a" : "LOKALITA NEHODY",
                    "d" : "GPS souřadnice X", "e" : "GPS souřadnice Y", "a, b, f, g, h, i, j, k, l, n, o, p, q, r, s, t" : "ĎALŠIE INFORMÁCIE"}
        print("Informacie o polozkach v stlpcoch:\n")
        for k, v in colums_info.items():
            print(f"{k}\t - {v}")

# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)

if __name__ == "__main__":

    # vypisanie zakladnych informacii na vystup pri spusteni
    regions3 = ["PAK", "LBK", "KVK"]
    dict_info = DataDownloader().get_dict(regions3)
    pocet_zaznamov = dict_info["region"].size
    DataDownloader().print_colums_info()
    print(f"Zakladne informacie o 3 regionoch ->")
    print(f"Pocet zaznamov v ukazkovych datach = {pocet_zaznamov}")
    print(f"Regiony v ukazkovych datach = {regions3}")
    print(f"PAK -> Pardubicky kraj, LBK -> Liberecky kraj, KVK -> Karlovarsky kraj")


