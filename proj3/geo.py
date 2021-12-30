#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily
import sklearn.cluster
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
# muzete pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani

    Arguments:
    df -- pandas DataFrame, data pre vytvorenie geo dataframu

    Returns:
    gdf -- GeoDataFrame, konvertovani dataframu s odstranenymi chybnymi datami
    """

    pd.options.mode.chained_assignment = None

    # odstranenie nevalidnych dat
    df = df.loc[~(np.isnan(df.d) | np.isnan(df.e))]
    # pridanie noveho stlpca s datumom
    df['date'] = pd.to_datetime(df['p2a'])
    # konvertovania dat do geodataframe
    gdf = geopandas.GeoDataFrame(df,
                                 geometry=geopandas.points_from_xy(df['d'], df['e']),
                                 crs="EPSG:5514",)
    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody
     (dalnice vs prvni trida) pro roky 2018-2020

    Arguments:
    gdf -- GeoDataFrame, data z ktoreho sa vytvoria grafy

    Keyword Arguments:
    fig_location -- Nazov suboru, pre ulozenie vysledneho grafu(default None)
    show_figure -- Graf sa zobrazi na obrazovke pri hodnote True(default False)
    """

    # vyfiltrovanie dat pre 1 kraj
    kraj = "JHM"
    gdf = gdf[gdf["region"] == kraj]
    # nastavenie grafu
    fig, axes = plt.subplots(3, 2, figsize=(15, 20))
    ax = axes.flat
    years = [2018, 2019, 2020]
    colors = ["green", "red"]

    # generovanie grafov
    for i in range(3):
        # ziskanie dat v danom roku a typ cesty
        gdf_tmp = gdf[gdf['date'].dt.year == years[i]]
        gdf_dalnice = gdf_tmp[gdf_tmp["p36"] == 0]
        gdf_silnice = gdf_tmp[gdf_tmp["p36"] == 1]
        ax_dalnice = ax[i*2]
        ax_silnice = ax[i*2 + 1]

        # graf pre dialnice v danom roku
        gdf_dalnice.plot(ax=ax_dalnice, markersize=2, color=colors[0])
        contextily.add_basemap(ax_dalnice, crs=gdf_dalnice.crs,
                               source=contextily.providers.Stamen.TonerLite)
        ax_dalnice.set_title(f"{kraj} kraj: dálnice ({years[i]})")
        ax_dalnice.axis("off")
        ax_dalnice.set_aspect("auto")

        # graf pre silnice v danom roku
        gdf_silnice.plot(ax=ax_silnice, markersize=2, color=colors[1])
        contextily.add_basemap(ax_silnice, crs=gdf_silnice.crs,
                               source=contextily.providers.Stamen.TonerLite)
        ax_silnice.set_title(f"{kraj} kraj: silnice první třídy ({years[i]})")
        ax_silnice.axis("off")
        ax_silnice.set_aspect("auto")

    # ulozenie grafu do suboru
    if fig_location:
        plt.savefig(fig_location)
    # zobrazenie grafu
    if show_figure:
        plt.show()

    plt.close(fig)


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru

    Arguments:
    gdf -- GeoDataFrame, data z ktoreho sa vytvoria grafy

    Keyword Arguments:
    fig_location -- Nazov suboru, pre ulozenie vysledneho grafu(default None)
    show_figure -- Graf sa zobrazi na obrazovke pri hodnote True(default False)
    """

    # vyfiltrovanie dat pre 1 kraj a silnice 1. triedy
    kraj = "JHM"
    gdf = gdf[gdf["region"] == kraj]
    gdf = gdf[gdf["p36"] == 1]

    plt.figure(figsize=(15, 20))
    ax = plt.gca()
    ax.set_title(f"Nehody v {kraj} kraji na silnicíh 1. třídy")
    ax.axis('off')

    # vytvorenie clusteru
    coords = np.dstack([gdf.geometry.x, gdf.geometry.y]).reshape(-1, 2)
    # pouzitych 25 clusterov TODO
    db = sklearn.cluster.MiniBatchKMeans(n_clusters=25).fit(coords)

    cluster_gdf = gdf.copy()
    cluster_gdf["cluster"] = db.labels_
    # spojim data do jednotlivych clusterov a z multipointu
    # spravim single pointy pre kazdy cluster
    cluster_gdf = cluster_gdf.dissolve(by="cluster", aggfunc={"p1": "count"})
    cluster_gdf = cluster_gdf.rename(columns=dict(p1="cnt")).explode()

    # pridanie legendy pod mapu
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # zobrazenie dat, farba poctu nehod v danom clusteri
    cluster_gdf.plot(ax=ax, markersize=10, column="cnt", legend=True, cax=cax,
                     legend_kwds={'label': "Počet nehod v úseku", 'orientation': "horizontal"})

    contextily.add_basemap(ax, crs=gdf.crs,
                           source=contextily.providers.Stamen.TonerLite)

    # ulozenie grafu do suboru
    if fig_location:
        plt.savefig(fig_location)
    # zobrazenie grafu
    if show_figure:
        plt.show()

    plt.close()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)