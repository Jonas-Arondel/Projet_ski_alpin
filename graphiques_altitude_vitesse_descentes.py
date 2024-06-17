import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelmin,argrelmax
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import numpy as np
#Importation du fichier csv
data = pd.read_csv("C:/Users/jojol/Documents/ETS/Cours/Projet 15 crédits/Projet/Données/Premier jeux de données/Synergie/Synergie/Thomas Mckinlay_GS_15.11.24/Wednesday Alpine Skiing - GS at 10-20-detail.csv")

#Graphique de l'atitude en focntion du temps
fig, ax = plt.subplots()
ax.plot(data['elevation[m]'][0:-1],"b")
ax.set_xlabel("Temps", fontsize=14)
ax.set_ylabel("Altitude", color="blue", fontsize=14)
ax2 = ax.twinx()
ax2.plot(data['speed[km/h]'][0:-1],"r", alpha=0.3)
ax2.set_ylabel("Vitesse", color="red", fontsize=14)

lines = [ax.get_lines()[0], ax2.get_lines()[0]]
plt.legend(lines, ["Altitude", "Vitesse"], loc="upper center")

#plt.plot(data['elevation[m]'][0:-1])
#plt.plot(data['speed[km/h]'][0:-1]*7)
plt.show()

#Projection mercator
import pyproj
def coordonnées_mercator(lat,long,elevation):
    transformer = pyproj.Transformer.from_crs(
    {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
    'EPSG:25835',
    )
    x ,y, z = transformer.transform(long,lat,elevation,radians = False)
    return x,y,z


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


projection_mercator=coordonnées_mercator(data['Latitude[deg]'],data['Longitude[deg]'],data['elevation[m]'])


for i in range(len(Liste_départ_arrivé_index)) :
    plt.plot(data['elevation[m]'][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]])
    plt.show()
    fig, axes = plt.subplots(subplot_kw=dict(projection='3d'))
    axes.set_xlabel("Latitude")
    axes.set_ylabel("Longitude")
    axes.set_zlabel("Altitude")
    segments = [np.column_stack([projection_mercator[0][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]][j:j+2], projection_mercator[1][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]][j:j+2],projection_mercator[2][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]][j:j+2]]) for j in range(Liste_départ_arrivé_index[i][1]-Liste_départ_arrivé_index[i][0] - 1)]
    lc = Line3DCollection(segments, cmap='viridis',array=data['speed[km/h]'][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]])
    axes.axis([projection_mercator[0][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].min(),projection_mercator[0][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].max(),projection_mercator[1][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].min(),projection_mercator[1][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].max(),projection_mercator[2][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].min(),projection_mercator[2][Liste_départ_arrivé_index[i][0]:Liste_départ_arrivé_index[i][1]].max()]) #set axis limits. This is [xlow, xhigh, ylow, yhigh]
    
    line = axes.add_collection(lc)
    plt.colorbar(line, label='Vitesse')
    plt.show()