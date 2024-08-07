import plotly.graph_objects as go
import numpy as np

import pandas as pd
#Importation du fichier csv
data = pd.read_csv("C:/Users/jojol/Documents/ETS/Cours/Projet 15 crédits/Projet/Données/Premier jeux de données/Synergie/Synergie/Thomas Mckinlay_GS_15.11.24/Wednesday Alpine Skiing - GS at 10-20-detail.csv")
import pyproj
def coordonnées_mercator(lat,long,elevation):
    transformer = pyproj.Transformer.from_crs(
    {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
    'EPSG:25835',
    )
    x ,y, z = transformer.transform(long,lat,elevation,radians = False)
    return x,y,z

projection_mercator=coordonnées_mercator(data['Latitude[deg]'],data['Longitude[deg]'],data['elevation[m]'])

import numpy as np
from scipy.signal import argrelmin,argrelmax

index_min_locaux=argrelmin(data['elevation[m]'].to_numpy(), order=4000)[0]
index_max_locaux=argrelmax(data['elevation[m]'].to_numpy(), order=4000)[0]
min_locaux=np.median(np.array([data['elevation[m]'][i] for i in index_min_locaux]))
max_locaux=np.median(np.array([data['elevation[m]'][i] for i in index_max_locaux]))


#On prend l'altitude max moins un delta de x mètres pour déterminer le début de la descente et on regarde combien de fois le skieur quitte cette zone
alt_max_zone=max_locaux-(max_locaux-min_locaux)/4
alt_min_zone=min_locaux+(max_locaux-min_locaux)/4

data_dans_les_zones_départ_et_arrivée=data[(data['elevation[m]']>alt_max_zone) | (data['elevation[m]']<alt_min_zone)]
L=np.diff(data_dans_les_zones_départ_et_arrivée['elevation[m]'].to_numpy())
zone_de_descente_large=[data_dans_les_zones_départ_et_arrivée[i:i+2].index for i in range(len(L)) if L[i]<-10 ]
#Détection du départ et de l'arrivée
data_vitesse=data['speed[km/h]']
Liste_départ_arrivé_index=[]
vitesse_seuil_bas=9
vitesse_seuil_haut=5



#Initialisation
#detection debut
index=zone_de_descente_large[0][0]
index_debut=zone_de_descente_large[0][0]
vitesse=10
while vitesse >vitesse_seuil_haut and index!=0:
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_debut=index
        index=index-1
#detection fin
index=zone_de_descente_large[0][1]
index_fin=zone_de_descente_large[0][1]
vitesse=10
while vitesse >vitesse_seuil_bas and index<zone_de_descente_large[0+1][1]:
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
    while vitesse >vitesse_seuil_haut and index>zone_de_descente_large[i-1][1]:
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_debut=index
        index=index-1
    #detection fin
    index=zone_de_descente_large[i][1]
    index_fin=zone_de_descente_large[i][1]
    vitesse=10
    while vitesse >vitesse_seuil_bas and index<zone_de_descente_large[i+1][1]:
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
while vitesse >vitesse_seuil_haut and index>zone_de_descente_large[i][1]:
    if data_vitesse[index]<vitesse:
        vitesse=data_vitesse[index]
        index_debut=index
    index=index-1
#detection fin
index=zone_de_descente_large[i+1][1]
index_fin=zone_de_descente_large[i+1][1]
vitesse=10
while vitesse >vitesse_seuil_bas and index<len(data_vitesse):
        if data_vitesse[index]<vitesse:
            vitesse=data_vitesse[index]
            index_fin=index
        index=index+1
Liste_départ_arrivé_index.append([index_debut,index_fin])




import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import interact
from matplotlib.widgets import Button


numéro_de_la_descente=5

dict_points=[]
dict_lines=[]


global num_points
num_points=0

color='#3A4C92'


#données
X = projection_mercator[1][Liste_départ_arrivé_index[numéro_de_la_descente][0]:Liste_départ_arrivé_index[numéro_de_la_descente][1]]
Y = projection_mercator[0][Liste_départ_arrivé_index[numéro_de_la_descente][0]:Liste_départ_arrivé_index[numéro_de_la_descente][1]]
max_X=max(X)
max_Y=max(Y)
min_X=min(X)
min_Y=min(Y)


# Créer un graphique vide
fig, ax = plt.subplots()

plt.plot(X, Y)


ax.set_xlim(min_X-0.05*(max_X-min_X), max_X+0.05*(max_X-min_X))
ax.set_ylim(min_Y-0.05*(max_Y-min_Y), max_Y+0.05*(max_Y-min_Y))

# Fonction pour supprimer les checkpoints
def remove_checkpoints(b):
    global num_points
    num_points=0
    global dict_points
    dict_points=[]
    global dict_lines
    dict_lines=[]
    for line in ax.lines[1:]:
        line.remove()
    

class MoveGraphPoint(object):
    def __init__(self, ax):
        self.ax = ax
        self.figcanvas = self.ax.figure.canvas
        self.pressed = False
        self.start = False
        self.selected = False
        self.point = None
        self.figcanvas.mpl_connect('pick_event', self.pick_point)
        self.figcanvas.mpl_connect('button_press_event', self.mouse_press)
        self.figcanvas.mpl_connect('button_release_event', self.mouse_release)
        self.figcanvas.mpl_connect('motion_notify_event', self.mouse_move)

    
    # Fonction pour ajouter un point à chaque clic
    def add_point(self,event):
        # Vérifier si le clic est dans les limites du graphique
        global num_points
        self.point,=ax.plot([event.xdata], [event.ydata], 'o',picker=True,color=color)
        dict_points.append(self.point)
        num_points+=1 
        if num_points%2==0:
            dict_lines.append(ax.plot([dict_points[-2].get_xdata(),dict_points[-1].get_xdata()],[dict_points[-2].get_ydata(),dict_points[-1].get_ydata(),],color=color))
            
        fig.canvas.draw()

    def mouse_release(self, event):
        if self.ax.get_navigate_mode() != None: return
        if not event.inaxes: return
        if event.inaxes != self.ax: return
        if self.pressed:
            self.pressed = False
            self.start = False
            self.selected = False
            self.point.set_color(color)

            return

    def mouse_press(self, event):
        if self.ax.get_navigate_mode() != None: return
        if not event.inaxes: return
        if event.inaxes != self.ax: return
        if self.start: return
        if self.selected:
            self.pressed = True
        else : 
            self.add_point(event)

    def mouse_move(self, event):
        if self.ax.get_navigate_mode() != None: return
        if not event.inaxes: return
        if event.inaxes != self.ax: return
        if not self.pressed: return
        self.start = True

        self.point.set_xdata([event.xdata])
        self.point.set_ydata([event.ydata])

        indice=dict_points.index(self.point)
        if indice%2==1:
            dict_lines[indice//2][0].set_xdata([dict_points[indice-1].get_xdata(),dict_points[indice].get_xdata()])
            dict_lines[indice//2][0].set_ydata([dict_points[indice-1].get_ydata(),dict_points[indice].get_ydata()])

        elif len(dict_points)>indice+1:
            dict_lines[indice//2][0].set_xdata([dict_points[indice].get_xdata(),dict_points[indice+1].get_xdata()])
            dict_lines[indice//2][0].set_ydata([dict_points[indice].get_ydata(),dict_points[indice+1].get_ydata()])
        self.figcanvas.draw()

    def pick_point(self, event):
        if self.ax.get_navigate_mode() != None: return
        self.point=event.artist
        self.selected = True
        self.point.set_color('r')
        self.figcanvas.draw()


# Créer un bouton pour supprimer les checkpoints
axes = plt.axes([0.1, -0.02, 0.3, 0.075])
button = Button(axes,"Supprimer les checkpoints")
button.on_clicked(remove_checkpoints)

# Connecter la fonction à l'événement de clic
move_point=MoveGraphPoint(ax)

# Afficher le graphique
plt.show()