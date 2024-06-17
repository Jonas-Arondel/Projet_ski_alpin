import seaborn as sns
from faicons import icon_svg
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelmin,argrelmax
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import numpy as np
import plotly.graph_objects as go
from shinywidgets import render_plotly
# Import data from shared.py
from shared import app_dir, df
from plotly.subplots import make_subplots
from shiny import reactive
from shiny.express import input, render, ui

#Importation du fichier csv
data = pd.read_csv("C:/Users/jojol/Documents/ETS/Cours/Projet 15 crédits/Projet/Données/Premier jeux de données/Synergie/Synergie/Thomas Mckinlay_GS_15.11.24/Wednesday Alpine Skiing - GS at 10-20-detail.csv")

## Découpage de chaque descente
#On prend l'altitude max moins un delta de x mètres pour déterminer le début de la descente et on regarde combien de fois le skieur quitte cette zone
index_min_locaux=argrelmin(data['elevation[m]'].to_numpy(), order=4000)[0]
index_max_locaux=argrelmax(data['elevation[m]'].to_numpy(), order=4000)[0]
min_locaux=np.median(np.array([data['elevation[m]'][i] for i in index_min_locaux]))
max_locaux=np.median(np.array([data['elevation[m]'][i] for i in index_max_locaux]))
alt_max_zone=max_locaux-(max_locaux-min_locaux)/4
alt_min_zone=min_locaux+(max_locaux-min_locaux)/4

data_dans_les_zones_départ_et_arrivée=data[(data['elevation[m]']>alt_max_zone) | (data['elevation[m]']<alt_min_zone)]
L=np.diff(data_dans_les_zones_départ_et_arrivée['elevation[m]'].to_numpy())
zone_de_descente_large=[data_dans_les_zones_départ_et_arrivée[i:i+2].index for i in range(len(L)) if L[i]<-10 ]
#Détection du départ et de l'arrivée
data_vitesse=data['speed[km/h]']
Liste_départ_arrivé_index=[]
#Initialisation
#detection debut
index=zone_de_descente_large[0][0]
index_debut=zone_de_descente_large[0][0]
vitesse=10
while vitesse >1 and index!=0:
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_debut=index
        index=index-1
#detection fin
index=zone_de_descente_large[0][1]
index_fin=zone_de_descente_large[0][1]
vitesse=10
while vitesse >1 and index<zone_de_descente_large[0+1][1]:
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_fin=index
        index=index+1
Liste_départ_arrivé_index.append([index_debut,index_fin])

#Recurrence
#Détéction début
for i in range(1,len(zone_de_descente_large)-1):
    vitesse=10
    index=zone_de_descente_large[i][0]
    index_debut=zone_de_descente_large[i][0]
    while vitesse >1 and index>zone_de_descente_large[i-1][1]:
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_debut=index
        index=index-1
    #detection fin
    index=zone_de_descente_large[i][1]
    index_fin=zone_de_descente_large[i][1]
    vitesse=10
    while vitesse >1 and index<zone_de_descente_large[i+1][1]:
            if data_vitesse[index]<vitesse:
                vitesse=data_vitesse[index]
                index_fin=index
            index=index+1
    Liste_départ_arrivé_index.append([index_debut,index_fin])
#fin
#Détéction début
vitesse=10
index=zone_de_descente_large[i+1][0]
index_debut=zone_de_descente_large[i+1][0]
while vitesse >1 and index>zone_de_descente_large[i][1]:
    if data_vitesse[index]<vitesse:
        vitesse=data_vitesse[index]
        index_debut=index
    index=index-1
#detection fin
index=zone_de_descente_large[i+1][1]
index_fin=zone_de_descente_large[i+1][1]
vitesse=10
while vitesse >1 and index<len(data_vitesse):
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_fin=index
        index=index+1
Liste_départ_arrivé_index.append([index_debut,index_fin])


ui.page_opts(title="Visualisation des descentes", fillable=True)
with ui.layout_columns():
    @render_plotly
    def histogram():
        fig = make_subplots(
            rows=(len(Liste_départ_arrivé_index)-1)//3+1, cols=3,specs=[[{'type': 'scatter3d'}]*3]*((len(Liste_départ_arrivé_index)-1)//3+1))
        for i in range(len(Liste_départ_arrivé_index)):
            # Read data from a csv
            données=data[['Latitude[deg]','Longitude[deg]','elevation[m]']][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].to_numpy()
            x=données[:,0]
            y=données[:,1]
            z=données[:,2]
            vitesse=data['speed[km/h]'][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]]

            fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode='markers',marker=dict(size=2,color=vitesse,colorscale='Viridis',opacity=0.8)),row=(i)//3+1, col=(i)%3+1)
        return fig

ui.include_css(app_dir / "styles.css")


