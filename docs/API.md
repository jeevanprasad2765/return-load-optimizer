# REST API Reference (`/api/v1`)

The Empty Return Load Optimizer exposes a OpenAPI 3.0-compliant REST API under `/api/v1`.

Interactive Swagger UI: `http://localhost:8000/api/v1/docs`  
ReDoc Documentation: `http://localhost:8000/api/v1/redoc`

---

## Endpoint Summary

### Authentication (`/auth`)
* `POST /auth/register` — Register carrier or shipper account
* `POST /auth/login` — Authenticate and receive JWT access token
* `GET /auth/me` — Retrieve current authenticated user profile

### Vehicles (`/trucks`)
* `GET /trucks` — List registered carrier trucks
* `POST /trucks` — Register new truck (carrier role required)
* `DELETE /trucks/{id}` — Remove vehicle

### Return Trips (`/trips`)
* `GET /trips` — List empty return trips
* `POST /trips` — Post empty return trip (carrier role required)
* `GET /trips/{id}/matches` — Get ranked shipment matches for trip
* `GET /trips/{id}/consolidation` — Get 2–3 multi-shipment consolidated load match groups

### Freight Shipments (`/shipments`)
* `GET /shipments` — List shipments
* `POST /shipments` — Post new shipment (shipper role required)
* `GET /shipments/{id}/matches` — Get ranked truck matches for shipment

### Matching Engine (`/matches`)
* `POST /matches/find` — Trigger batch matching run across all active trips
* `PUT /matches/{id}/accept` — Accept match
* `PUT /matches/{id}/reject` — Reject match

### Stateful Bookings (`/bookings`)
* `POST /bookings` — Shipper requests booking on a match ($\rightarrow$ status `pending`, triggers notification)
* `PATCH /bookings/{id}/status` — Carrier/Shipper updates booking status (`pending` $\rightarrow$ `confirmed` $\rightarrow$ `in_transit` $\rightarrow$ `delivered` / `cancelled`)
* `GET /bookings` — List bookings filtered by user role

### In-App Notifications (`/notifications`)
* `GET /notifications` — List notifications for authenticated user
* `PATCH /notifications/{id}/read` — Mark notification as read
* `POST /notifications/read-all` — Mark all notifications as read

### Dashboard Metrics (`/dashboard`)
* `GET /dashboard/metrics` — Aggregate ROI & environmental metrics, monthly trend points, route volumes, and active map route polylines
