import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import ipywidgets as ipy
plt.style.use('dark_background')

solar_system = [
    { "name": "Mercury", "a": 0.3871, "e": 0.206, "inc": 7.00, "varpi": 29.124, "color": "gray" },
    { "name": "Venus", "a": 0.7233, "e": 0.007, "inc": 3.39, "varpi": 54.884, "color": "gold" },
    { "name": "Earth", "a": 1, "e": 0.017, "inc": 0.00, "varpi": 114.207, "color": "green" },
    { "name": "Mars", "a": 1.5273, "e": 0.093, "inc": 1.85, "varpi": 286.5, "color": "red" },
    { "name": "Jupiter", "a": 5.2028, "e": 0.048, "inc": 1.31, "varpi": 273.867, "color": "orange" },
    { "name": "Saturn", "a": 9.5388, "e": 0.056, "inc": 2.49, "varpi": 339.392, "color": "yellow" },
    { "name": "Uranus", "a": 19.1914, "e": 0.046, "inc": 0.77, "varpi": 96.998, "color": "blue" },
    { "name": "Neptune", "a": 30.0611, "e": 0.010, "inc": 1.77, "varpi": 273.187, "color": "purple" },
]

def visualize_orbits(orbits, count, elevation = 30, azimuth = 40, zoom = 1):

    ax = plt.figure(figsize=(8, 8)).add_subplot(projection='3d')
    max_extent = 0
    
    for i in range(0, count + 8):

        # Determines the shape of the given orbit
        a = orbits[i]['a']        # Semi-major axis
        e = orbits[i]['e']        # Eccentricity
        b = a * np.sqrt(1 - e ** 2)   # Semi-minor axis
        offset = a * e                # Position of the orbit's focus

        # Creates an ellipse representing the given orbit
        t = np.linspace(0, 2 * np.pi, 100)
        x = offset + a * np.cos(t)
        y = b * np.sin(t)
        
        # Rotates the ellipse both in its inclination and it's argument of perihelion
        theta = orbits[i]['varpi'] * np.pi / 180
        phi = orbits[i]['inc']  * np.pi / 180
        rot_x = x * np.cos(theta) - y * np.sin(theta)
        y = x * np.sin(theta) + y * np.cos(theta)
        x = rot_x * np.cos(phi)
        z = rot_x * -np.sin(phi)
        
        # Keeps track of the largest extent of all the orbits
        max_extent = max(max_extent, np.abs(np.min(x)), np.abs(np.min(y)), np.abs(np.min(z)), np.max(x), np.max(y), np.max(z))
        
        # Plots the orbit (with a specific color for the known solar system orbits)
        if orbits[i]['color'] == "random":
            plt.plot(x, y, z, label = orbits[i]['name'], alpha = 0.15 if count > 50 else 1, color="red")
        else:
            plt.plot(x, y, z, label = orbits[i]['name'], color=orbits[i]['color'])
    
    # Makes the 3d plot area square and allows for zooming in and out
    zoom /= 100
    log_zoom = np.emath.logn(2, 1 + zoom)
    max_log_zoom = np.emath.logn(2, 2)
    zoom = log_zoom / max_log_zoom
    extent = ((1 - zoom) * max_extent) + (zoom * 0.01) 
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_zlim(-extent, extent)
    print(zoom)
    
    # Adds the sun in the center, to scale
    u = np.linspace(0, 2 * np.pi, 200)
    v = np.linspace(0, np.pi, 200)
    x = 0.00485 * np.outer(np.cos(u), np.sin(v))
    y = 0.00485 * np.outer(np.sin(u), np.sin(v))
    z = 0.00485 * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color="orange")

    # Sets the angle of the viewpoint
    ax.view_init(elevation, azimuth)
    
    # Hides the grid background
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    #plt.legend(loc="upper right");
    
    
def interactive_plot():
    
    # Randomize the reference population data
    reference_population = pd.read_csv("reference_population.csv", comment = "#")
    reference_population = reference_population.sample(frac = 1).reset_index(drop = True)

    orbit_data = solar_system.copy()
    for i in range(1000):
        orbit_data.append({
            "name": "Orbit " + str(reference_population.at[i, 'index']),
            "a": reference_population.at[i, ' a'],
            "e": reference_population.at[i, ' e'],
            "inc": reference_population.at[i, ' inc'],
            "varpi": reference_population.at[i, ' varpi'],
            "color": "random"
        })
    
    
    count = ipy.IntSlider(10, min=0, max=1000, description="Orbits")
    elevation = ipy.FloatSlider(25, min=0, max=90, step=0.5, description="Elevation")
    azimuth = ipy.FloatSlider(60, min=0, max=90, step=0.5, description="Azimuth")
    zoom = ipy.FloatSlider(50, min = 0, max=100, step=0.01, description="Zoom")

    ui = ipy.HBox([
        ipy.VBox([count, zoom]),
        ipy.VBox([elevation, azimuth])
    ])

    out = ipy.interactive_output(
        visualize_orbits, 
        {'orbits': ipy.fixed(orbit_data),
         'count': count,
         'elevation': elevation,
         'azimuth': azimuth,
         'zoom': zoom}
    )

    display(ui, out);