import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

# Daten
data = {
    "PyGenProg": [179, 179, 179, 176, 181, 174, 167, 179, 187, 160],
    "PyCardumen": [164, 148, 122, 158, 154, 148, 158, 140, 151, 154],
    "PyKali": [153, 140, 147, 149, 150, 149, 153, 157, 143, 143],
    "PyMutRepair": [147, 151, 148, 145, 146, 144, 146, 148, 146, 146],
}

# DataFrame erstellen
df = pd.DataFrame(data)

# Plot-Setup
fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.suptitle("Histogramme der Wahrscheinlichkeitsverteilungen mit Normalverteilung", fontsize=16)

# Plots erstellen
for i, (method, values) in enumerate(data.items()):
    ax = axes[i]
    mean, std = np.mean(values), np.std(values, ddof=1)
    
    # Histogramm der Daten
    ax.hist(values, bins=8, density=True, alpha=0.6, color="skyblue", edgecolor="black", label="Daten")
    
    # Normalverteilung
    x = np.linspace(mean - 4 * std, mean + 4 * std, 100)
    pdf = norm.pdf(x, mean, std)
    ax.plot(x, pdf, 'r-', label="Normalverteilung")
    
    # Titel und Achsenbeschriftung
    ax.set_title(method)
    ax.set_xlabel("Wert")
    ax.set_ylabel("Dichte" if i == 0 else "")
    ax.legend()

# Layout anpassen und anzeigen
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
