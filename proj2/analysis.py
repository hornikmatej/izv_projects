#!/usr/bin/env python3.9
# coding=utf-8
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

    kraje = ['HKK', 'JHC', 'JHM', 'KVK']
    df = df.loc[df['region'].isin(kraje)]
    titles = ['Dvoupruhová komunikace', 'Třípruhová komunika', 'Čtyřpruhová komunikace s dělícím pásem',
              'Čtyřpruhová komunikace s dělící čarou', 'Vícepruhová komunikace', 'Jiná komunikace']
    # nastavenie grafu
    sns.set(rc={'axes.facecolor': '#eaeaf2'})
    fig, axes = plt.subplots(2, 3, figsize=(11.69, 8.27))
    fig.suptitle("Druhy silnic")
    plt.setp(axes[:, 0], ylabel='Počet nehod')
    ax = axes.flat
    
    # vytvorenie 6 podgrafov
    for i in range(6):
        # ziskanie dat pre jednotlive druhy komunikacie
        data = df.loc[df['p21'] == i + 1].groupby('region')['p21'].count()
        if i == 5:
            # pripocitam aj data s inou komunikaciu k rychlostni komunikaci - > zobrazena ako jina komunikace
            data = data + df.loc[df['p21'] == 0].groupby('region')['p21'].count()
        sns.barplot(ax=ax[i], x=data.index, y=data.values, 
                    palette=['blue', 'orange', 'green', 'red'], ).set_title(titles[i])

    plt.tight_layout()
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
    pass

if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz", verbose=True) # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    # plot_roadtype(df, "01_road.png",show_figure=True)
    plot_animals(df, "02_animals.png", True)
    plot_conditions(df, "03_conditions.png", True)
