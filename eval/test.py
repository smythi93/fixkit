import pandas as pd

# Beispiel DataFrame
data = [
    ["True", 123.45, 0.95],
    ["False", 67.89, 0.85],
    ["TimeoutExpired", None, 0.75],
    ["TRUE", 456.78, 0.91],
    ["False", 123.45, 0.80]
]
columns = ["found", "duration", "fitness"]

# DataFrame erstellen
df = pd.DataFrame(data, columns=columns)

# Konvertiere 'found' zu Strings und bereinige Werte (strip für Leerzeichen)
df['found'] = df['found'].astype(str).str.strip().str.lower()

# Behalte nur Zeilen mit 'true' oder 'false'
df = df[df['found'].isin(['true', 'false'])]

# Konvertiere 'found' von String ('true', 'false') zu bool (True, False)
df['found'] = df['found'].map({'true': True, 'false': False})

# Ergebnis anzeigen
print(df["found"].dtype)
