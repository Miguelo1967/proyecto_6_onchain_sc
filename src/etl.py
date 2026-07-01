"""
ETL — Proyecto 6: Onchain + Supply Chain
Fuentes:
  1. CoinGecko  — precio ETH histórico (2022-2025)
  2. Etherscan v2 — transacciones grandes (ballenas)
  3. Baltic Dry Index (BDI) — CSV de Investing.com (NASDAQ descontinuó el dataset gratuito)
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_API_KEY")
COINGECKO_KEY = os.getenv("COINGECKO_API_KEY")


# ─────────────────────────────────────────────
# 1. PRECIO ETH — CoinGecko (sin API key)
# ─────────────────────────────────────────────
def obtener_precio_eth(desde="2022-01-01", hasta="2025-12-31"):
    """
    Descarga precio diario de ETH/USDT desde Binance (klines).
    No requiere API key y no tiene límite de 365 días como CoinGecko free tier.
    Pagina en bloques de 1000 velas (máximo por llamada).
    Retorna DataFrame con columnas: fecha, precio_eth, volumen_eth
    """
    print("📡 Descargando precio ETH desde Binance...")

    desde_ms = int(pd.Timestamp(desde).timestamp() * 1000)
    hasta_ms = int(pd.Timestamp(hasta).timestamp() * 1000)

    todas_velas = []
    cursor = desde_ms

    while cursor < hasta_ms:
        url = (
            f"https://api.binance.com/api/v3/klines"
            f"?symbol=ETHUSDT&interval=1d"
            f"&startTime={cursor}&endTime={hasta_ms}&limit=1000"
        )
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        velas = resp.json()

        if not velas:
            break

        todas_velas.extend(velas)
        cursor = velas[-1][0] + 1
        time.sleep(0.2)

    df = pd.DataFrame(todas_velas, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_base", "taker_quote", "ignore"
    ])

    df["fecha"] = pd.to_datetime(df["open_time"], unit="ms").dt.normalize()
    df["precio_eth"] = df["close"].astype(float)
    df["volumen_eth"] = df["volume"].astype(float)

    df = df[["fecha", "precio_eth", "volumen_eth"]].reset_index(drop=True)

    print(f"   ✅ {len(df)} días descargados")
    return df

# ─────────────────────────────────────────────
# 2. TRANSACCIONES BALLENA — Etherscan v2
# ─────────────────────────────────────────────
def obtener_transacciones_ballena(umbral_eth=1000, max_pages=5):
    """
    Extrae transferencias internas grandes de ETH.
    Retorna DataFrame con columnas: fecha, eth_ballena_total, txs_ballena
    """
    print(f"🐋 Descargando transacciones ballena (>= {umbral_eth} ETH) desde Etherscan...")

    todas = []
    for page in range(1, max_pages + 1):
        url = (
            f"https://api.etherscan.io/v2/api"
            f"?chainid=1"
            f"&module=account"
            f"&action=txlistinternal"
            f"&startblock=0"
            f"&endblock=99999999"
            f"&page={page}"
            f"&offset=200"
            f"&sort=desc"
            f"&apikey={ETHERSCAN_KEY}"
        )
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "1" or not data.get("result"):
            break

        todas.extend(data["result"])
        time.sleep(0.25)

    if not todas:
        print("   ⚠️  Sin resultados de Etherscan")
        return pd.DataFrame()

    df = pd.DataFrame(todas)
    df["valor_eth"] = df["value"].astype(float) / 1e18
    df = df[df["valor_eth"] >= umbral_eth].copy()
    df["fecha"] = pd.to_datetime(df["timeStamp"].astype(int), unit="s").dt.normalize()
    df = df[["fecha", "hash", "valor_eth", "from", "to"]].reset_index(drop=True)

    resumen = df.groupby("fecha").agg(
        eth_ballena_total=("valor_eth", "sum"),
        txs_ballena=("hash", "count")
    ).reset_index()

    print(f"   ✅ {len(resumen)} días con actividad ballena")
    return resumen


# ─────────────────────────────────────────────
# 3. BALTIC DRY INDEX — CSV local (Investing.com)
# ─────────────────────────────────────────────
def obtener_bdi(desde="2022-01-01", hasta="2026-12-31",
                 ruta_csv="data/raw/bdi_historico.csv"):
    """
    Lee el Baltic Dry Index desde un CSV descargado manualmente de Investing.com.
    Retorna DataFrame con columnas: fecha, bdi
    """
    print(f"🚢 Leyendo Baltic Dry Index desde {ruta_csv}...")

    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(
            f"No se encontró {ruta_csv}. Descarga el histórico desde "
            "https://www.investing.com/indices/baltic-dry-historical-data "
            "y guárdalo en esa ruta."
        )

    df = pd.read_csv(ruta_csv)
    df.columns = [c.strip() for c in df.columns]

    df["fecha"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")

    df["bdi"] = (
        df["Price"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    df = df[["fecha", "bdi"]].sort_values("fecha").reset_index(drop=True)
    df = df[(df["fecha"] >= desde) & (df["fecha"] <= hasta)].reset_index(drop=True)

    print(f"   ✅ {len(df)} registros BDI cargados ({df['fecha'].min().date()} a {df['fecha'].max().date()})")
    return df


# ─────────────────────────────────────────────
# 4. MERGE FINAL
# ─────────────────────────────────────────────
def construir_dataset_maestro(desde="2022-01-01", hasta="2025-12-31"):
    """
    Integra las tres fuentes en un solo DataFrame diario.
    Guarda en data/processed/dataset_maestro.csv
    """
    eth_df = obtener_precio_eth(desde, hasta)
    ballena_df = obtener_transacciones_ballena()
    bdi_df = obtener_bdi(desde="2022-01-01", hasta="2026-12-31")

    df = eth_df.merge(ballena_df, on="fecha", how="left")
    df = df.merge(bdi_df, on="fecha", how="left")

    df["bdi"] = df["bdi"].ffill()
    df["eth_ballena_total"] = df["eth_ballena_total"].fillna(0)
    df["txs_ballena"] = df["txs_ballena"].fillna(0)

    output_path = "data/processed/dataset_maestro.csv"
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\n✅ Dataset maestro guardado: {output_path}")
    print(f"   Shape: {df.shape}")
    print(df.head())
    return df


if __name__ == "__main__":
    construir_dataset_maestro()