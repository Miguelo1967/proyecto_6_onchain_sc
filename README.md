# Proyecto 6: Onchain + Supply Chain Integrado
## Detección de señales anticipatorias entre movimientos onchain de Ethereum y disrupciones en el comercio global

### 📌 Hipótesis

Los movimientos de grandes wallets de Ethereum (ballenas) anticipan o reaccionan a disrupciones
en el comercio global de commodities, medidas a través del Baltic Dry Index (BDI) como proxy
de actividad logística marítima internacional.

### 🎯 Objetivo

Integrar analítica onchain (blockchain) con analítica de supply chain tradicional para determinar
si existe una relación estadísticamente significativa —y con valor predictivo— entre la actividad
en el mercado de Ethereum y la actividad del comercio marítimo global.

### 🗂️ Fuentes de datos

| Variable | Fuente | Período | Notas |
|---|---|---|---|
| Precio ETH | Binance API pública (`/api/v3/klines`) | 2022–2025 | Sin límite histórico, sin API key |
| Volumen ETH | Binance API pública | 2022–2025 | Proxy de actividad de grandes holders |
| Baltic Dry Index (BDI) | Investing.com (CSV manual) | 2022–2025 | NASDAQ Data Link descontinuó el dataset gratuito |

**Decisión metodológica:** se descartó el análisis directo de wallets ballena vía Etherscan
por requerir el plan Pro (US$199/mes). En su lugar, se usó el volumen de trading de ETH en
Binance como proxy de actividad de grandes tenedores — una aproximación razonable dado que
movimientos grandes de ballenas típicamente se reflejan en picos de volumen.

### 🔧 Metodología

1. **ETL** (`src/etl.py`): extracción y limpieza de precio/volumen ETH (Binance) y BDI
   (CSV local), consolidación en dataset maestro diario.
2. **Análisis de correlación** (`src/correlacion.py`): correlación de Pearson entre ambas
   series + análisis de rezagos (lag analysis) para identificar si una serie anticipa a la otra.
3. **Visualización** (`src/viz.py`): generación de gráficos comparativos y de correlación cruzada.

### 📊 Dataset

- **1,461 días** de datos diarios (2022–2025)
- **4 columnas:** `fecha`, `precio_eth`, `volumen_eth`, `bdi`

### 📈 Hallazgos principales

- **Precio ETH → BDI:** correlación de Pearson r = 0.29 (contemporánea); la correlación se
  fortalece a r = 0.31 cuando el precio ETH se desplaza **30 días** antes del BDI — es decir,
  el precio de ETH parece anticipar movimientos en el índice de comercio marítimo con un mes
  de antelación.
- **Volumen ETH → BDI:** correlación más débil pero consistente, con el volumen anticipando
  al BDI en **3 días** (r = 0.12).
- Ambas señales son estadísticamente significativas (p = 0.0).

### 💡 Interpretación de negocio

Estos hallazgos sugieren que los mercados de criptoactivos —altamente líquidos y sensibles a
expectativas macro— podrían estar incorporando señales de riesgo comercial global antes de que
estas se reflejen en indicadores logísticos tradicionales como el BDI. Para equipos de supply
chain y procurement, esto abre la puerta a explorar el precio y volumen de ETH como **indicador
adelantado (leading indicator)** complementario en la gestión de riesgo de cadena de suministro,
sin reemplazar las fuentes tradicionales.

### ⚠️ Limitaciones

- Correlación no implica causalidad; se requiere validación adicional con más variables de control.
- El uso de volumen ETH como proxy de "ballenas" es una aproximación, no una medición directa
  de wallets grandes.
- El BDI es un proxy del comercio marítimo global, no una medida directa de disrupciones
  específicas por commodity o ruta.

### 🛠️ Stack técnico

- Python 3.13
- Binance API pública (`/api/v3/klines`)
- Pandas, SciPy (Pearson, lag analysis)
- Matplotlib/Seaborn para visualización

### 📁 Estructura del proyecto

​```
proyecto_6_onchain_sc/
├── data/
│   ├── raw/bdi_historico.csv
│   └── processed/dataset_maestro.csv
├── src/
│   ├── etl.py
│   ├── correlacion.py
│   └── viz.py
├── outputs/
│   ├── *.png (3 gráficos)
│   └── *.csv (2 resultados)
├── requirements.txt
└── README.md
​```

### 👤 Autor

Miguel Oswaldo Amaya Gómez — Analista de datos que convierte datos complejos en decisiones
de negocio. Especializado en Supply Chain, Data Analytics y Blockchain/Onchain analysis.

📘 *El Manual del Analista Cripto*: https://go.hotmart.com/T105702815H
🔗 GitHub: [github.com/Miguelo1967](https://github.com/Miguelo1967)