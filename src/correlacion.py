"""
correlacion.py — Proyecto 6: Onchain + Supply Chain
Análisis de correlación entre señales onchain y Baltic Dry Index.
"""

import pandas as pd
import numpy as np
from scipy import stats
import os


def cargar_dataset():
    df = pd.read_csv("data/processed/dataset_maestro.csv", parse_dates=["fecha"])
    df = df.dropna(subset=["bdi", "precio_eth"])
    return df


def correlacion_pearson(df):
    señales = {
        "precio_eth":        "Precio ETH (USD)",
        "volumen_eth":       "Volumen ETH en mercado",
        "eth_ballena_total": "ETH movido por ballenas",
        "txs_ballena":       "Nº transacciones ballena",
    }
    resultados = []
    for col, nombre in señales.items():
        if col not in df.columns or df[col].dropna().empty:
            continue
        r, p = stats.pearsonr(df[col].fillna(0), df["bdi"])
        resultados.append({
            "señal":         nombre,
            "columna":       col,
            "pearson_r":     round(r, 4),
            "p_valor":       round(p, 4),
            "significativo": "✅" if p < 0.05 else "❌"
        })
    return pd.DataFrame(resultados)


def correlacion_lag(df, max_lag=30):
    señales = ["precio_eth", "eth_ballena_total", "txs_ballena"]
    resultados = []
    for col in señales:
        if col not in df.columns:
            continue
        # Saltar señales sin variación (todos ceros)
        if df[col].std() == 0:
            print(f"   ⚠️  '{col}' sin variación — omitiendo lag")
            continue
        mejor_r, mejor_lag, mejor_p = 0, 0, 1
        for lag in range(1, max_lag + 1):
            serie_lag = df[col].shift(lag).fillna(0)
            if len(serie_lag.dropna()) < 2:
                continue
            r, p = stats.pearsonr(serie_lag, df["bdi"])
            if abs(r) > abs(mejor_r):
                mejor_r, mejor_lag, mejor_p = r, lag, p
        if mejor_lag > 0:
            resultados.append({
                "señal":           col,
                "lag_optimo_dias": mejor_lag,
                "pearson_r":       round(mejor_r, 4),
                "p_valor":         round(mejor_p, 4),
                "interpretacion":  f"'{col}' anticipa el BDI {mejor_lag} días antes"
            })
    return pd.DataFrame(resultados)

def resumen_hallazgos(df_pearson, df_lag):
    print("\n" + "="*55)
    print("  HALLAZGOS — Correlación Onchain vs Supply Chain")
    print("="*55)
    print("\n📊 Correlación directa (Pearson):")
    print(df_pearson.to_string(index=False))
    print("\n⏱️  Análisis de rezago (¿anticipan las ballenas al BDI?):")
    print(df_lag.to_string(index=False))
    print("="*55)


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    df = cargar_dataset()
    print(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")

    df_pearson = correlacion_pearson(df)
    df_lag     = correlacion_lag(df)
    resumen_hallazgos(df_pearson, df_lag)

    df_pearson.to_csv("outputs/correlacion_pearson.csv", index=False)
    df_lag.to_csv("outputs/correlacion_lag.csv", index=False)
    print("\n✅ Resultados guardados en outputs/")