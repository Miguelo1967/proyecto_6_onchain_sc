"""
viz.py — Proyecto 6: Onchain + Supply Chain
Genera visualizaciones para el README y LinkedIn.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os

os.makedirs("outputs", exist_ok=True)
sns.set_theme(style="darkgrid")
PALETTE = ["#627EEA", "#E84142", "#F5A623"]


def grafico_serie_doble(df):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.set_xlabel("Fecha", fontsize=12)
    ax1.set_ylabel("Precio ETH (USD)", color=PALETTE[0], fontsize=12)
    ax1.plot(df["fecha"], df["precio_eth"], color=PALETTE[0], linewidth=1.8, label="ETH Price")
    ax1.tick_params(axis="y", labelcolor=PALETTE[0])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Baltic Dry Index", color=PALETTE[2], fontsize=12)
    ax2.plot(df["fecha"], df["bdi"], color=PALETTE[2], linewidth=1.8,
             linestyle="--", label="BDI", alpha=0.85)
    ax2.tick_params(axis="y", labelcolor=PALETTE[2])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)
    plt.title("ETH Price vs Baltic Dry Index (2022–2025)", fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    plt.savefig("outputs/01_eth_vs_bdi.png", dpi=150)
    plt.close()
    print("✅ Guardado: outputs/01_eth_vs_bdi.png")


def grafico_correlacion_heatmap(df_pearson):
    df_plot = df_pearson.dropna(subset=["pearson_r"])
    if df_plot.empty:
        print("⚠️  Sin datos para heatmap")
        return
    pivot = df_plot.set_index("señal")[["pearson_r"]]
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="coolwarm",
                center=0, vmin=-1, vmax=1, ax=ax,
                linewidths=0.5, cbar_kws={"label": "Pearson r"})
    ax.set_title("Correlación Señales Onchain vs BDI", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("")
    fig.tight_layout()
    plt.savefig("outputs/02_heatmap_correlacion.png", dpi=150)
    plt.close()
    print("✅ Guardado: outputs/02_heatmap_correlacion.png")


def grafico_lag(df_lag):
    if df_lag.empty:
        print("⚠️  Sin datos de lag")
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    colores = [PALETTE[0] if r > 0 else PALETTE[1] for r in df_lag["pearson_r"]]
    bars = ax.barh(df_lag["señal"], df_lag["lag_optimo_dias"], color=colores, alpha=0.85)
    for bar, r in zip(bars, df_lag["pearson_r"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"r={r:.3f}", va="center", fontsize=10)
    ax.set_xlabel("Días de anticipación al BDI", fontsize=12)
    ax.set_title("¿Cuántos días antes anticipa ETH el BDI?",
                 fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    plt.savefig("outputs/03_lag_optimo.png", dpi=150)
    plt.close()
    print("✅ Guardado: outputs/03_lag_optimo.png")


if __name__ == "__main__":
    df = pd.read_csv("data/processed/dataset_maestro.csv", parse_dates=["fecha"])
    df_pearson = pd.read_csv("outputs/correlacion_pearson.csv")
    df_lag = pd.read_csv("outputs/correlacion_lag.csv")

    grafico_serie_doble(df)
    grafico_correlacion_heatmap(df_pearson)
    grafico_lag(df_lag)

    print("\n🎨 Todas las visualizaciones generadas en outputs/")