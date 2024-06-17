import plotly.graph_objects as go
import numpy as np


import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np

# Initialize figure with 4 3D subplots

# Generate data
x = np.linspace(0, 0, 2)
y = np.linspace(0, 10, 2)
xGrid, yGrid = np.meshgrid(y, x)
z = xGrid ** 1 + yGrid ** 1
print(z)
# adding surfaces to subplots.
fig=go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale='Viridis', showscale=False)])

fig.update_layout(
    title_text='3D subplots with different colorscales',
    height=800,
    width=800
)

fig.show()