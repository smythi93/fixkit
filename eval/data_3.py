import scipy.stats as stats

# Daten
pygenprog = [179, 179, 179, 176, 181, 174, 167, 179, 187, 160]
pycardumen = [164, 148, 122, 158, 154, 148, 158, 140, 151, 154]
pykali = [153, 140, 147, 149, 150, 149, 153, 157, 143, 143]
pymutrepair = [147, 151, 148, 145, 146, 144, 146, 148, 146, 146]

# Shapiro-Wilk-Test für jeden Ansatz
for approach, data in zip(
    ["PyGenProg", "PyCardumen", "PyKali", "PyMutRepair"],
    [pygenprog, pycardumen, pykali, pymutrepair]
):
    stat, p = stats.shapiro(data)
    print(f"{approach}: Shapiro-Wilk-Statistik={stat}, p-Wert={p}")
    if p < 0.05:
        print(f"-> Die Daten für {approach} sind nicht normalverteilt.")
    else:
        print(f"-> Die Daten für {approach} könnten normalverteilt sein.")
