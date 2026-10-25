# ✈️ AEROSENTINEL: Global Air Assistant AI & Flight Radar

An autonomous, real-time aviation analytics engine built to predict and explain **how late an aircraft might be** using live international flight telemetry and global atmospheric weather (METAR) data. Powered by **DuckDB** for in-process big data OLAP, **Streamlit** for the frontend, and a **Non-LLM Gradient Boosted Decision Tree (HistGradientBoosting)** AI engine.

---

## 🌟 Worldwide Coverage & Capabilities

| Feature | Details |
| :--- | :--- |
| **Global Airspace Coverage** | **39 Major Hubs across all 6 continents**: Asia & Middle East (`DXB`, `SIN`, `HND`, `NRT`, `HKG`, `DEL`, `BOM`, `ICN`, `BKK`, `DOH`, `PVG`), Europe (`LHR`, `CDG`, `FRA`, `AMS`, `MAD`, `IST`, `FCO`, `ZRH`), North America (`JFK`, `LAX`, `ORD`, `ATL`, `DFW`, `SFO`, `YYZ`, `MEX`), South America (`GRU`, `EZE`, `BOG`, `SCL`), Africa (`JNB`, `CAI`, `NBO`, `ADD`, `LOS`), Oceania (`SYD`, `MEL`, `AKL`). |
| **Premier International Airlines** | Emirates (`EK`), Qatar Airways (`QR`), Singapore Airlines (`SQ`), Air India (`AI`), Cathay Pacific (`CX`), ANA (`NH`), JAL (`JL`), Korean Air (`KE`), Turkish Airlines (`TK`), Lufthansa (`LH`), British Airways (`BA`), Air France (`AF`), Qantas (`QF`), LATAM (`LA`), Ethiopian (`ET`), Delta (`DL`), American (`AA`), United (`UA`), Air Canada (`AC`). |
| **Flicker-Free UX (Zero-Blink)** | Isolated lightweight refresh fragments decouple the navigation tabs and interactive maps from background data streams. User interactions (dropdowns, sliders, 3D globe rotation) remain completely stable without jumping or blinking. |
| **Interactive World Radar Map** | Great-circle flight paths, dynamic aircraft position vectors, and airport weather threat rings with continent, delay, and weather filters. |
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
- Real-time commercial aircraft plotted geographically with color-coded delay status (🟢 On-Time, 🟡 Moderate, 🔴 Severe).
- Filter by Continent (`🌍 All Continents`, `Asia & Middle East`, `Europe`, `North America`, `South America`, `Africa`, `Oceania`).
- Filter by Delay Tier and Weather Severity (Storms, High Winds, Fog).
- Map projection options: `Natural Earth`, `Orthographic (3D Globe)`, `Equirectangular`, `Mercator`.
- Click **"🔄 Sync Radar Positions"** anytime for instant on-demand radar position advance without page flicker.

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
