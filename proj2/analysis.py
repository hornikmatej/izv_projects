#!/usr/bin/env python3.9
# coding=utf-8
from datetime import date
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import sys

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B. 
"""


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """Nacita data a prekonvertuje vhodne stlpce na kategorovy typ
    
    Arguments:
    filename -- nazov suboru s datami

    Keyword arguments:
    verbose -- Na standardny vystup vypise informacie o velkosti ramcu pred a po uprave typov (default False)

    Returns:
    df -- pandas DataFrame s upravenymi typmi dat v urcitych stlpoch a pridanim stlpcom s datumom
    """
    df = pd.read_pickle(filename)

    orig_size = df.memory_usage(deep=True).sum() / 1048576
    # pridanie noveho stlpca s datumom
    df['date'] = pd.to_datetime(df['p2a'])
    # zmenim typy len urcitym stlcpov
    for col in df:
        if col not in ['date', 'region', 'p2a', 'p13a', 'p13b', 'p13c', 'p53', 'p14', 'a', 'b', 'd', 'f', 'g', 'j', 'r', 's']:
            df[col] = df[col].astype('category')

    if verbose:
        # vypis informacie o velkosti pred a po konvertovani typov
        new_size = df.memory_usage(deep=True).sum() / 1048576
        print(f"orig_size={orig_size:.1f} MB\nnew_size={new_size:.1f} MB")
    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic

def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    """Funkcia vytvori graf so 6 podgrafmi s nehodami v 4 krajoch podla typu silnicnej komunikacie
    V pripade zadaneho argumentu fig_location, sa graf ulozi do suboru. 
    V pripade zadaneho argumentu show_figure, sa graf zobrazi 

    Arguments:
    df -- Pandas DataFrame, data z ktoreho sa vytvoria grafy

    Keyword Arguments:
    fig_location -- Nazov suboru, do ktoreho sa ulozi vysledny graf(default None)
    show_figure -- Graf sa zobrazi na obrazovke pri hodnote True(default False)
    """

    kraje = ['HKK', 'JHC', 'JHM', 'KVK']
    df = df.loc[df['region'].isin(kraje)]
    titles = ['Dvoupruhová komunikace', 'Třípruhová komunika', 'Čtyřpruhová komunikace',
              'Vícepruhová komunikace', 'Rychlostní komunikace', 'Jiná komunikace']
    # nastavenie grafu
    sns.set(rc={'axes.facecolor': '#eaeaf2'})
    fig, axes = plt.subplots(2, 3, figsize=(11.69, 8.27))
    fig.suptitle("Druhy silnic")
    
    ax = axes.flat
    
    # vytvorenie 6 podgrafov
    index = 1 # index pre typy komunikacii
    for i in range(6):
        # ziskanie dat pre jednotlive druhy komunikacie
        index = 0 if index == 7 else index # ak sa jedna o posledny graf tak to je 0 v stlpci p21
        data = df.loc[df['p21'] == index].groupby('region')['p21'].count()
        if index == 3:
            # ctyrpruhova komunikace je v 2 stlpoch tak ich spocitam spolu
            data = data + df.loc[df['p21'] == index + 1].groupby('region')['p21'].count()
            index += 1
        
        sns.barplot(ax=ax[i], x=data.index, y=data.values, 
                    palette=['blue', 'orange', 'green', 'red'], ).set_title(titles[i])
        index += 1

    plt.subplots_adjust(hspace=0.4) 
    plt.setp(axes[:, 0], ylabel='Počet nehod')
    plt.setp(axes, xlabel='Kraj')
    # ulozenie grafu do suboru
    if (fig_location):
        plt.savefig(fig_location)
    # zobrazenie grafu
    if (show_figure):
        plt.show()
    plt.close(fig)

# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """Funkcia vytvori graf so 4 podgrafmi, ktore zobrazia pocet nehod v jednotlivych mesiacoch rozdelenych 
    podla typu zavinenia (zveri, ridicem, jine). 4 podgrafy pre 4 rozne kraje.
    V pripade zadaneho argumentu fig_location, sa graf ulozi do suboru. 
    V pripade zadaneho argumentu show_figure, sa graf zobrazi 

    Arguments:
    df -- Pandas DataFrame, data z ktoreho sa vytvoria grafy

    Keyword Arguments:
    fig_location -- Nazov suboru, do ktoreho sa ulozi vysledny graf(default None)
    show_figure -- Graf sa zobrazi na obrazovke pri hodnote True(default False)
    """

    kraje = ['HKK', 'JHC', 'JHM', 'KVK']
    df = df.loc[df['region'].isin(kraje)]
    # nastavenie grafu
    sns.set(rc={'axes.facecolor': '#eaeaf2'})
    fig, axes = plt.subplots(2, 2, figsize=(11.69, 8.27))
    fig.suptitle("Nehody v mesiacoch")    
    ax = axes.flat
    pd.options.mode.chained_assignment = None

    # konvertovanie stlpca p10 na retazce 
    df['p10'] = pd.cut(df['p10'], bins=[0, 1, 3, 4, 5, 9], labels=["jiné", "řidičem", "jiné", "zvěří", "jiné"], 
                       right=False, ordered=False)
    # odfiltrovanie roku 2021 a ziskanie mesiacov 
    df = df[df['date'].dt.year != 2021]
    df['Měsíc'] = df['date'].dt.month
    # vytvorenie 4 podgrafov
    for i in range(4):
        axplt = sns.countplot(x="Měsíc", hue="p10", data=df.loc[df['region'] == kraje[i]], ax=ax[i])
        axplt.legend_.remove()
        axplt.set_title(f"Kraj: {kraje[i]}")
    
    # nastavenie legendy a celeho grafu podla zadania
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc='right', bbox_to_anchor=(1.0, 0.5), title='Zavinění', frameon=False)
    plt.subplots_adjust(right=0.85, hspace=0.4) 

    plt.setp(ax, ylabel='Počet nehod')
    # ulozenie grafu do suboru
    if (fig_location):
        plt.savefig(fig_location)
    # zobrazenie grafu
    if (show_figure):
        plt.show()
    plt.close(fig)

# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    """Funkcia vytvori graf so 4 podgrafmi, ktore zobrazia pocet nehod v od zaciatku 2016 do konca 2020.
    Pocty nehod rozdeli podla podmienok pocasia
    V pripade zadaneho argumentu fig_location, sa graf ulozi do suboru. 
    V pripade zadaneho argumentu show_figure, sa graf zobrazi 

    Arguments:
    df -- Pandas DataFrame, data z ktoreho sa vytvoria grafy

    Keyword Arguments:
    fig_location -- Nazov suboru, do ktoreho sa ulozi vysledny graf(default None)
    show_figure -- Graf sa zobrazi na obrazovke pri hodnote True(default False)
    """
    # vybrate kraje, pre ktore sa zobrazia data
    kraje = ['HKK', 'JHC', 'JHM', 'KVK']
    df = df.loc[df['region'].isin(kraje)]
    
    # nastavenie grafu
    sns.set(rc={'axes.facecolor': '#eaeaf2'})
    fig, axes = plt.subplots(2, 2, figsize=(11.69, 8.27))
    fig.suptitle("Povětrnostní podmínky")
    ax = axes.flat

    # odmazanie dat ktore mali stlpec p18 v 0
    df = df.loc[df['p18'] != 0]
    # nastavenie retazcom za hodnoty v stlpci p18
    labels = ["neztížené", "mlha", "na počátku deště", "déšť", "sněžení", "náledí", "nárazový vítr"]
    df['p18'] = pd.cut(df['p18'], bins=[1, 2, 3, 4, 5, 6, 7, 8], labels=labels, 
                       right=False)
    # v pre kazdy den a kraj v stlpci pocet nehod pre rozne podmienky
    df_pivot = pd.pivot_table(df, columns="p18", values="p1", index=["region", "date"], aggfunc="count").reset_index()

    for i in range(4):
        # vyberem data len pre 1 region a podvzorkujem data na uroven mesiacov
        data = (df_pivot.loc[df_pivot['region'] == kraje[i]]).groupby('date').agg('sum').resample('M').sum().reset_index()
        # dam prec data z roku 2021 
        data = data.loc[data['date'].dt.year != 2021]
        # vytvorenie grafu
        axplt = sns.lineplot(x ="date", y="value", hue="p18", data=data.melt(id_vars="date"), ax=ax[i])
        axplt.legend_.remove()
        axplt.set_title(f"Kraj: {kraje[i]}") 
    
    # nastavenie legendy a celeho grafu podla zadania
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc='right', bbox_to_anchor=(1.0, 0.5), title='Podmínky', frameon=False)
    plt.subplots_adjust(right=0.85, hspace=0.4) 

    plt.setp(ax, ylabel='Počet nehod', xlabel='Dátum')
    # ulozenie grafu so suboru
    if (fig_location):
        plt.savefig(fig_location)
    # zobrazenie grafu
    if (show_figure):
        plt.show()
    plt.close(fig)

if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("data/accidents.pkl.gz", verbose=True) # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    plot_roadtype(df, "data/01_road.png",show_figure=True)
    # plot_animals(df, "data/02_animals.png", True)
    # plot_conditions(df, "data/03_conditions.png", True)
