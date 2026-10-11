# Matching Algorithm & Scoring Engine Specification

The `return-load-matcher` engine evaluates empty return truck trips against pending freight shipments. Each trip-shipment pair receives a composite score from **0 to 100**, alongside a detailed breakdown per factor, rate estimations, and hard-rejection reasons.

## 1. Mathematical Scoring Formula

The total score $S$ is calculated as a weighted sum of four independent compatibility factors:

$$S = (W_{\text{route}} \times S_{\text{route}}) + (W_{\text{capacity}} \times S_{\text{capacity}}) + (W_{\text{time}} \times S_{\text{time}}) + (W_{\text{vehicle}} \times S_{\text{vehicle}})$$

### Default Configurable Weights:
* **Route Compatibility ($W_{\text{route}}$): 40%**
* **Capacity Fit ($W_{\text{capacity}}$): 25%**
* **Time Compatibility ($W_{\text{time}}$): 20%**
* **Vehicle Type Match ($W_{\text{vehicle}}$): 15%**

---

## 2. Hard Rejection Filters

Before computing scores, candidate matches undergo 4 hard-rejection validation checks:

1. **Weight Exceeds Available Capacity**:
   $$\text{Shipment Weight (kg)} > \text{Trip Available Capacity (kg)}$$
2. **Excessive Road Detour Distance (OSRM)**:
   $$\Delta d = d_{\text{road\_detour}} - d_{\text{road\_direct}} > \text{Max Detour Threshold (60.0 km)}$$
   $$\text{or } \frac{\Delta d}{d_{\text{road\_direct}}} > \text{Max Detour Ratio (35\%)}$$
3. **Incompatible Vehicle Type**:
   Required vehicle type specified by shipper cannot be safely carried by truck (e.g. refrigerated cargo on open-body truck).
4. **Time Window / Deadline Violation**:
   Trip departure occurs after shipment pickup window closes, or estimated arrival time exceeds delivery deadline.

---

## 3. Real OSRM Road Detour & Caching

The engine queries the **OSRM API** (`https://router.project-osrm.org`) for exact road distances:
$$\text{Baseline Route} = \text{Origin} \rightarrow \text{Destination}$$
$$\text{Detour Route} = \text{Origin} \rightarrow \text{Shipment Pickup} \rightarrow \text{Shipment Dropoff} \rightarrow \text{Destination}$$

* **Caching**: All coordinate pairs are cached in memory to eliminate redundant OSRM requests.
* **Graceful Fallback**: If OSRM is unreachable or rate-limited, the engine falls back to Haversine distance with a 1.25 winding factor and flags `is_osrm_fallback = True` for UI transparency.

---

## 4. Rate & Price Estimation ($S_{\text{pricing}}$)

The engine applies configurable **Vehicle Rate Cards** (base rate/km + rate/kg):

$$\text{Estimated Price (Shipper)} = (\text{Billable km} \times \text{Rate/km}) + (\text{Shipment kg} \times \text{Rate/kg}) + \text{Base Fee}$$

$$\text{Baseline Dedicated Truck Cost} = (\text{Direct km} \times \text{Rate/km} \times 1.30) + (\text{Trip Max Capacity} \times \text{Rate/kg}) + \text{Base Fee}$$

$$\text{Cost Savings ₹} = \max(0, \text{Baseline Cost} - \text{Estimated Price})$$
$$\text{Cost Savings \%} = \frac{\text{Cost Savings ₹}}{\text{Baseline Cost}} \times 100\%$$

---

## 5. Multi-Shipment Load Consolidation

The engine evaluates combinations of 2 to 3 compatible shipments (`find_multi_shipment_consolidation`):

1. Generates combinations of 2–3 shipments where $\sum w_i \le C_{\text{available}}$.
2. Scores each combination using total load capacity fill %, route detour compatibility, and individual match scores.
3. Groups can be accepted in a single click on the carrier UI.

---

## 6. Notification Triggers

Whenever a match score $\ge 70$, or a booking status changes (`pending` $\rightarrow$ `confirmed` $\rightarrow$ `in_transit` $\rightarrow$ `delivered` / `cancelled`), notifications are automatically sent to the relevant user's navbar bell dropdown.
