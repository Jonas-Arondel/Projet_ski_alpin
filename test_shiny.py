from shiny import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelmin,argrelmax
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import numpy as np

from shiny.express import input, render, ui

ui.input_slider("val", "Slider label", min=0, max=100, value=50)

@render.text
def slider_val():
    return f"Slider value: {input.val()}"