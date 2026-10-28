# ✈️ AEROSENTINEL: Global Air Assistant AI & Flight Radar

An autonomous, real-time aviation analytics engine built to predict and explain **how late an aircraft might be** using live international flight telemetry and global atmospheric weather (METAR) data. Powered by **DuckDB** for in-process big data OLAP, **Streamlit** for the frontend, and a **Non-LLM Gradient Boosted Decision Tree (HistGradientBoosting)** AI engine.

---

## 🌟 Worldwide Coverage & Capabilities

| Feature | Details |
| :--- | :--- |
| **Global Airspace Coverage** | **39 Major Hubs across all 6 continents**: Asia & Middle East (`DXB`, `SIN`, `HND`, `NRT`, `HKG`, `DEL`, `BOM`, `ICN`, `BKK`, `DOH`, `PVG`), Europe (`LHR`, `CDG`, `FRA`, `AMS`, `MAD`, `IST`, `FCO`, `ZRH`), North America (`JFK`, `LAX`, `ORD`, `ATL`, `DFW`, `SFO`, `YYZ`, `MEX`), South America (`GRU`, `EZE`, `BOG`, `SCL`), Africa (`JNB`, `CAI`, `NBO`, `ADD`, `LOS`), Oceania (`SYD`, `MEL`, `AKL`). |
| **Premier International Airlines** | Emirates (`EK`), Qatar Airways (`QR`), Singapore Airlines (`SQ`), Air India (`AI`), Cathay Pacific (`CX`), ANA (`NH`), JAL (`JL`), Korean Air (`KE`), Turkish Airlines (`TK`), Lufthansa (`LH`), British Airways (`BA`), Air France (`AF`), Qantas (`QF`), LATAM (`LA`), Ethiopian (`ET`), Delta (`DL`), American (`AA`), United (`UA`), Air Canada (`AC`). |
| **Flightradar24-Scale Density** | **1,200+ Active Simultaneous Commercial Aircraft** operating worldwide across 39 international hubs on all 6 continents with sub-millisecond DuckDB OLAP processing. |
| **Live OpenSky ADS-B Ingestion** | **Authenticated OAuth2 Live Stream**: Pulls real-world airborne flights worldwide via OpenSky Network REST API with real ADS-B coordinates, altitudes, ground speeds, and callsigns. |
| **Origin & Destination Filters** | Isolate specific airport pairs (e.g., `JFK ➔ LHR`, `DXB ➔ SIN`, `HND ➔ SYD`) or filter by carrier and delay status. |
| **Selectable Weather Overlays** | User-toggleable meteorological layers: **Global Jet Streams** (125-155 kts), **Convective Doppler Radar Cells** (45-56 dBZ), **CAT Turbulence SIGMETs**, and **Marine/Radiation Fog Layers**. |
| **Dual Telemetry Modes** | Seamlessly toggle between **Live OpenSky API** (real airborne flights) and **Synthetic Simulator** (1,200+ hub aircraft). |
| **Interactive World Radar Map** | Great-circle flight paths, exact real ADS-B coordinates, and airport weather threat rings with 3D Globe, Natural Earth, and Mercator projections. |
| **Non-LLM Delay Prediction AI** | Scikit-Learn `HistGradientBoostingRegressor` + deterministic aerodynamic/congestion rules calculate delay in minutes ($0$ to $120+$ min) and explain root causes. |
| **Big Data Engine (DuckDB)** | Sub-millisecond queries on 1,000,000+ flight logs with synchronized, thread-safe connection pooling. |

---

## 🚀 How to Run on Windows (1-Click)

Simply double-click:

- **[`run.bat`](file:///d:/Prog4DSProject/run.bat)**: Runs natively on Windows using Python and launches the dashboard at `http://localhost:8501`.
- **[`run_docker.bat`](file:///d:/Prog4DSProject/run_docker.bat)**: Containerized startup via Docker Compose.

---

## 🗺️ Key Features in the Dashboard

### 1. 🗺️ Global Flight Radar & Weather Map
- **Flightradar24 Fleet Scale**: Over 1,200 commercial aircraft plotted geographically with real-time color-coded delay status (🟢 On-Time, 🟡 Moderate Delay, 🔴 Severe Hazard).
- **Origin & Destination Routing Filters**: Select any specific origin airport (e.g. `JFK`, `LHR`, `DXB`, `HND`, `SYD`) and destination airport (`All Destinations` or specific pairing).
- **Selectable Atmospheric Weather Overlays**:
  - `🌀 Global Jet Streams (High-Altitude Winds)`: High-velocity polar and subtropical jet stream cores (125-155 knots) at FL340-FL380.
  - `⛈ Convective Storm Radar (Doppler dBZ)`: Severe thunderstorm supercells and squall lines with radar reflectivity up to 56 dBZ.
  - `⚠️ Clear-Air Turbulence (CAT) & Icing Zones`: Mountain wave and high-shear SIGMET turbulence boundaries.
  - `🌫️ Low Visibility & Marine Fog Layers`: Advection and radiation fog corridors enforcing ILS CAT III instrument approaches.
  - `None (Clean Radar)`: Clean flight radar view.
- **Airspace Sector Filtering**: Filter by Continent (`🌍 All Continents`, `Asia & Middle East`, `Europe`, `North America`, `South America`, `Africa`, `Oceania`).
- **Map Projections**: `Natural Earth`, `Orthographic (3D Globe)`, `Equirectangular`, `Mercator`.

### 2. ✈️ Air Assistant & Flight Delay Inspector
- Select any active international flight (e.g. `EK-412 DXB ➔ SYD`, `AI-101 DEL ➔ JFK`, `SQ-322 SIN ➔ LHR`).
- Instant predicted delay gauge (`+42 min Expected Delay`) with confidence score.
- Root-cause breakdown (atmospheric friction vs. destination runway saturation).
- Interactive What-If Simulator: Adjust crosswind, precipitation, or runway queue sliders to observe AI delay predictions live.

### 3. 📡 Live Radar Feed & Analytics
- Live streaming table with flight metrics.
- Wind Speed vs. Predicted Delay scatter plot.
- Global airline reliability ranking and on-time performance (OTP).

### 4. 🌐 Worldwide Hubs Weather Matrix
- Live METAR observations (winds, visibility, rain, congestion index, ground stop alert level) across all 39 global airport hubs with continent filters.

### 5. ⛈ Extreme Weather Shock Testing
- Select any international hub (e.g., `DXB`, `HND`, `LHR`, `DEL`, `ORD`, `SYD`) in the sidebar and click **"⚡ Inject Storm Shock"**.
- Watch a simulated convective storm / typhoon / blizzard hit the hub and observe how the Air Assistant immediately re-evaluates all inbound aircraft.
