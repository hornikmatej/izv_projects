#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Projekt 1 do predmetu IZV
# Autor: xhorni20@fit.vut.cz (Matej Hornik)

import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from matplotlib.colors import LogNorm
import os
from download import DataDownloader


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    """Funkcia vytvori graf pre 24 stlpec dat  
    
    Arguments:
        data_srouce -- data z ktorych sa bude vykreslovat graf
    Keyword arguments:
        fig_location -- cesta a nazov suboru kam sa ulozi vytvoreny graf (default "None")
        show_figure -- ak zadane, zobrazi sa graf na displeji (default "False")
    """
    # ziskanie regionov v datach 
    regions = np.unique(data["region"])
    # prazdna matica pre vysledok
    absolut = np.empty(shape=(len(regions), 6) ,dtype = 'f')

    for i, region in enumerate(regions):
        # prechadzam kazdy region a naplnim vyslednu maticu
        indexes = np.where(data["region"] == region)
        sums = [
                np.sum(data["p24"][indexes] == 1),
                np.sum(data["p24"][indexes] == 2),
                np.sum(data["p24"][indexes] == 3),
                np.sum(data["p24"][indexes] == 4),
                np.sum(data["p24"][indexes] == 5),
                np.sum(data["p24"][indexes] == 0)
            ]
        absolut[i] = sums
    # uprava finalnych dat pre grafy
    absolut = np.transpose(absolut)
    relative = absolut.copy()
    absolut[absolut == 0] = np.nan
    relative = np.transpose(np.transpose(relative) / np.transpose(np.sum(relative, axis=1))) * 100
    relative[relative == 0] = np.nan

    fig = plt.figure(figsize=(11.69, 8.27)) # A4 v palcoch
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    # prvy graf
    ax1.set_title("Absolutně")
    ax1.xaxis.set_ticks(range(0,len(regions)))
    ax1.xaxis.set_ticklabels(regions)
    ax1.yaxis.set_ticks(range(0,6))
    ax1.yaxis.set_ticklabels([
        "Přerušovaná žlutá",
        "Semafor mimo provoz",
        "Dopravní značky",
        "Přenosné dopravní značky",
        "Nevyznačená",
        "Žádna úprava",
    ])

    ai1 = ax1.imshow(absolut, norm=LogNorm(1,1e5))
    cbar = fig.colorbar(ai1, ax=ax1)
    cbar.set_label("Počet nehod")
    
    # druhy graf
    ax2.set_title("Relativně voči příčině")
    ax2.xaxis.set_ticks(range(0,len(regions)))
    ax2.xaxis.set_ticklabels(regions)
    ax2.yaxis.set_ticks(range(0,6))
    ax2.yaxis.set_ticklabels([
        "Přerušovaná žlutá",
        "Semafor mimo provoz",
        "Dopravní značky",
        "Přenosné dopravní značky",
        "Nevyznačená",
        "Žádna úprava",
    ])

    ai2 = ax2.imshow(relative, cmap="plasma")
    cbar = fig.colorbar(ai2, ax=ax2)
    cbar.set_label("Podíl nehod pro danou příčinu [%]")

    if show_figure:
        ax1.plot()
        ax2.plot()
        plt.show()
    if fig_location:
        if not os.path.exists(os.path.dirname(fig_location)):
            os.makedirs(os.path.dirname(fig_location))
        fig.savefig(fig_location)
    plt.close(fig)



# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    # spracovanie argumentov pomocou ArgumentParser()
    parser = ArgumentParser()
    parser.add_argument("--fig_location",
                        help="Ak zadany, tak sa ulozi obrazok do zadanej cesty")
    parser.add_argument("--show_figure", help="Ak zadany, tak sa zobrazi graf",
                        action="store_true", default=False)
    args = parser.parse_args()
    
    # ak nieje zadane fig location alebo 
    if args.fig_location is not None or args.show_figure is True:
        data = DataDownloader().get_dict()
        plot_stat(data, args.fig_location, args.show_figure)
