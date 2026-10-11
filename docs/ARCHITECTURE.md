# System Architecture & Design

The **Empty Return Load Optimizer** is structured as a modular, production-ready monorepo separating domain logic, API server, data persistence, and interactive user interface.

## Monorepo Architecture Overview

```mermaid
graph TB
    subgraph ClientLayer["Frontend Layer (React.js + Vite)"]
        UI[React UI Components]
        Map[Leaflet OpenStreetMap View]
        Charts[Recharts Dashboard Panel]
    end

    subgraph APILayer["Backend API Layer (FastAPI)"]
        Router[REST API v1 /api/v1]
        AuthService[JWT Authentication & Argon2]
        MatchBridge[Matching Service Bridge]
        DashService[Dashboard Metrics Service]
    end

    subgraph EngineLayer["Engine Package (return-load-matcher)"]
        Scorer[Multi-Factor Scorer 0-100]
        RouteEval[OSRM Route Compatibility]
        CapEval[Capacity Fit Evaluator]
        TimeEval[Temporal Window Evaluator]
        VehEval[Vehicle Compatibility Matrix]
        Consolidator[Multi-Shipment Bin-Packer]
    end

    subgraph DataLayer["Persistence Layer"]
        DB[(PostgreSQL / SQLite)]
        Alembic[Alembic Database Migrations]
    end

    subgraph ExternalServices["External APIs"]
        OSRM[OSRM Route Server]
    end

    UI --> Router
    Map --> Router
    Charts --> Router
    Router --> AuthService
    Router --> MatchBridge
    Router --> DashService
    MatchBridge --> EngineLayer
    RouteEval --> OSRM
    Router --> DB
    Alembic --> DB
```

## Component Responsibilities

| Component | Technology | Responsibilities |
| :--- | :--- | :--- |
| **`/engine`** | Python 3.10+, pure dataclasses | Standalone, pip-installable algorithm package. Scores trip-shipment compatibility, evaluates detour penalties via OSRM, handles hard-rejections, and consolidates multi-shipment loads. **Zero DB/Web framework dependencies.** |
| **`/backend`** | Python FastAPI, Async SQLAlchemy, PyJWT | REST API provider. Manages user authentication (Carrier & Shipper roles), database models (`User`, `Truck`, `Trip`, `Shipment`, `Match`, `Booking`), and connects engine scoring with persistent storage. |
| **`/frontend`** | React 18, Vite, TailwindCSS v4 | Dark-mode glassmorphic web dashboard. Provides Carrier & Shipper workflows, Leaflet map views with route polyline geometry, and Recharts ROI/environmental impact analytics. |
| **`/docs`** | Markdown | Technical documentation, algorithm math, architecture diagrams, API specs, and integration guidelines. |
```
