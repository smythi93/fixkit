import scipy.stats as stats
import pandas as pd
from pathlib import Path
import os
import numpy as np
import scikit_posthocs as sp

# Daten laden
data = {
    "PyGenProg": [179, 179, 179, 176, 181, 174, 167, 179, 187, 160],
    "PyCardumen": [164, 148, 122, 158, 154, 148, 158, 140, 151, 154],
    "PyKali": [153, 140, 147, 149, 150, 149, 153, 157, 143, 143],
    "PyMutRepair": [147, 151, 148, 145, 146, 144, 146, 148, 146, 146],
}

def mean_and_shit(df: pd.DataFrame):
    stats = df.describe()

    print(stats)
    print("Variance: ")
    print(df.var())
    print("Median: ")
    print(df.median())

def anova_test(df) -> float:
    f_stat, p_value = stats.f_oneway(
    df["PyGenProg"],
    df["PyCardumen"],
    df["PyKali"],
    df["PyMutRepair"]
)

    # Ergebnisse anzeigen
    print("ANOVA-Test Ergebnisse:")
    print(f"F-Statistik: {f_stat}")
    print(f"P-Wert: {p_value}")

    # Entscheidung basierend auf dem p-Wert
    alpha = 0.05
    if p_value < alpha:
        print("Die Mittelwerte der Gruppen sind signifikant unterschiedlich (H0 ablehnen).")
    else:
        print("Die Mittelwerte der Gruppen sind nicht signifikant unterschiedlich (H0 beibehalten).")

    return p_value


# Levene-Test (Homogenität)
def levene_test(df):
    stat, p = stats.levene(
        df["PyGenProg"], df["PyCardumen"], df["PyKali"], df["PyMutRepair"]
    )
    print(f"Levene-Test: Statistik={stat}, p-Wert={p}")
    if p < 0.05:
        print("Die Varianzen sind nicht homogen (Verletzung der ANOVA-Annahmen).")
    else:
        print("Die Varianzen sind homogen.")

#Falls keine Normalverteilung
def kruskal_wallis_test(df):
    # Kruskal-Wallis-Test
    stat, p = stats.kruskal(df['PyGenProg'], df['PyCardumen'], df['PyKali'], df['PyMutRepair'])
    print(f"Kruskal-Wallis-Statistik: {stat}, p-Wert: {p}")

#posthoc nach kruskal wallis
def posthoc_dunn_test(df):
    df_melted = df.melt(var_name="Gruppe", value_name="Wert")
    posthoc = sp.posthoc_dunn(df_melted, val_col="Wert", group_col="Gruppe", p_adjust="bonferroni")
    print(posthoc)

#posthoc nach anova
def posthoc_turkey_test(df):
    df_long = df.melt(var_name="Group", value_name="Value")

    # Tukey HSD Test mit scikit_posthocs
    tukey_result = sp.posthoc_tukey(
        df_long,
        val_col="Value",  # Abhängige Variable
        group_col="Group",   # Gruppierungsvariable
    )

    # Ergebnisse anzeigen
    print(tukey_result)

def save_data(df, name):
    df.to_csv(os.path.join(Path(__file__).parent, name), index=False)

#test normalverteilung
def test_shapiro(df: pd.DataFrame, col):
    sw_stat, sw_p = stats.shapiro(df[col])
    print(sw_stat, sw_p)

#test normalverteilung
def test_ks(df:pd.DataFrame, col):
    mean, std = df[col].mean(), df[col].std(ddof=1)
    ks_stat, ks_p = stats.kstest(df[col], "norm", args=(mean, std))
    print(ks_stat, ks_p)

def test_anderson(df: pd.DataFrame, col):
    ad_result = stats.anderson(df[col], dist="norm")
    ad_stat = ad_result.statistic
    ad_critical_values = ad_result.critical_values
    ad_significance = ad_result.significance_level
    print(ad_stat)
    print(ad_critical_values)
    print(ad_significance)


# Daten umformen
df = pd.DataFrame(data)

#59 überall abziehen
filtered_df = df.map(lambda x: x-59)

mean_and_shit(filtered_df)
#test_anderson(filtered_df, "PyGenProg")
#test_anderson(filtered_df, "PyCardumen")
#test_anderson(filtered_df, "PyKali")
#test_anderson(filtered_df, "PyMutRepair")

#test_shapiro(filtered_df, "PyGenProg")
#test_shapiro(filtered_df, "PyCardumen")
#test_shapiro(filtered_df, "PyKali")
#test_shapiro(filtered_df, "PyMutRepair")

#test_ks(filtered_df, "PyGenProg")
#test_ks(filtered_df, "PyCardumen")
#test_ks(filtered_df, "PyKali")
#test_ks(filtered_df, "PyMutRepair")

#anova_test(filtered_df)
#mean_and_shit(filtered_df)
#posthoc_turkey_test(filtered_df)
#posthoc_dunn_test(filtered_df)