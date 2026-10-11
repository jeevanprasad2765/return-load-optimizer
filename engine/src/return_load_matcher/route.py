import math
import httpx
from typing import Tuple, List, Optional, Dict
from return_load_matcher.models import Coordinate, TripInfo, ShipmentInfo
from return_load_matcher.config import MatchConfig

# In-memory OSRM Route Cache: key -> (distance_km, duration_minutes, geometry, is_fallback)
_OSRM_CACHE: Dict[str, Tuple[float, float, List[Coordinate], bool]] = {}

def clear_route_cache():
    _OSRM_CACHE.clear()

def haversine_distance_km(coord1: Coordinate, coord2: Coordinate) -> float:
    """Calculate Great Circle distance in kilometers between two points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(coord2.lat - coord1.lat)
    dlon = math.radians(coord2.lon - coord1.lon)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(coord1.lat)) * math.cos(math.radians(coord2.lat)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _make_cache_key(coords: List[Coordinate], base_url: str) -> str:
    coord_str = ";".join([c.to_osrm() for c in coords])
    return f"{base_url}:{coord_str}"

async def get_osrm_route(
    coords: List[Coordinate],
    base_url: str = "https://router.project-osrm.org",
    timeout: float = 5.0,
    client: Optional[httpx.AsyncClient] = None
) -> Tuple[float, float, List[Coordinate], bool]:
    """
    Call OSRM driving profile for a list of coordinates with in-memory caching.
    Returns (distance_km, duration_minutes, geometry_coordinates, is_fallback)
    """
    cache_key = _make_cache_key(coords, base_url)
    if cache_key in _OSRM_CACHE:
        return _OSRM_CACHE[cache_key]

    coord_str = ";".join([c.to_osrm() for c in coords])
    url = f"{base_url.rstrip('/')}/route/v1/driving/{coord_str}?overview=full&geometries=geojson"
    
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=timeout)
        close_client = True

    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            distance_km = route["distance"] / 1000.0
            duration_minutes = route["duration"] / 60.0
            raw_coords = route.get("geometry", {}).get("coordinates", [])
            # OSRM returns [lon, lat], convert to Coordinate(lat, lon)
            geometry = [Coordinate(lat=c[1], lon=c[0]) for c in raw_coords]
            res = (distance_km, duration_minutes, geometry, False)
            _OSRM_CACHE[cache_key] = res
            return res
    except Exception:
        pass
    finally:
        if close_client:
            await client.aclose()

    # Fallback to Haversine calculation if OSRM is unreachable/rate-limited
    total_km = 0.0
    for i in range(len(coords) - 1):
        total_km += haversine_distance_km(coords[i], coords[i+1])
    # Assume average speed of 50 km/h for heavy trucks in India
    duration_min = (total_km / 50.0) * 60.0
    fallback_dist = total_km * 1.25  # 1.25 winding factor for road network estimate
    fallback_res = (fallback_dist, duration_min, coords, True)
    _OSRM_CACHE[cache_key] = fallback_res
    return fallback_res

async def evaluate_route_compatibility(
    trip: TripInfo,
    shipment: ShipmentInfo,
    config: MatchConfig,
    client: Optional[httpx.AsyncClient] = None
) -> Tuple[float, float, float, float, bool, Optional[str], List[Coordinate], bool]:
    """
    Evaluates route compatibility using OSRM real road network routing.
    Returns:
    (route_score, detour_km, detour_minutes, direct_trip_km, is_rejected, rejection_reason, geometry, is_osrm_fallback)
    """
    # Direct route: Trip Origin -> Trip Destination
    direct_km, direct_min, direct_geom, fallback_direct = await get_osrm_route(
        [trip.origin, trip.destination],
        base_url=config.osrm_base_url,
        timeout=config.request_timeout_seconds,
        client=client
    )

    # Detour route: Trip Origin -> Shipment Pickup -> Shipment Destination -> Trip Destination
    detour_route_coords = [trip.origin]
    
    # Avoid duplicating if pickup is same as origin
    if haversine_distance_km(trip.origin, shipment.pickup) > 0.5:
        detour_route_coords.append(shipment.pickup)
        
    detour_route_coords.append(shipment.destination)
    
    # Avoid duplicating if destination is same as trip destination
    if haversine_distance_km(shipment.destination, trip.destination) > 0.5:
        detour_route_coords.append(trip.destination)

    detour_km_total, detour_min_total, matched_geom, fallback_detour = await get_osrm_route(
        detour_route_coords,
        base_url=config.osrm_base_url,
        timeout=config.request_timeout_seconds,
        client=client
    )

    is_fallback = fallback_direct or fallback_detour
    extra_detour_km = max(0.0, detour_km_total - direct_km)
    extra_detour_min = max(0.0, detour_min_total - direct_min)

    # Check rejection thresholds
    if extra_detour_km > config.max_detour_km:
        return (
            0.0, extra_detour_km, extra_detour_min, direct_km, True,
            f"Road detour of {extra_detour_km:.1f} km exceeds maximum allowed detour threshold of {config.max_detour_km:.1f} km",
            matched_geom, is_fallback
        )

    if direct_km > 0 and (extra_detour_km / direct_km) > config.max_detour_ratio:
        ratio_pct = (extra_detour_km / direct_km) * 100
        max_ratio_pct = config.max_detour_ratio * 100
        return (
            0.0, extra_detour_km, extra_detour_min, direct_km, True,
            f"Road detour ratio of {ratio_pct:.1f}% exceeds maximum allowed limit of {max_ratio_pct:.1f}% of trip distance",
            matched_geom, is_fallback
        )

    # Route score calculation (0 to 100)
    score_from_km = max(0.0, 100.0 * (1.0 - (extra_detour_km / config.max_detour_km)))
    ratio = extra_detour_km / max(1.0, direct_km)
    score_from_ratio = max(0.0, 100.0 * (1.0 - (ratio / config.max_detour_ratio)))

    route_score = round(0.6 * score_from_km + 0.4 * score_from_ratio, 2)
    return route_score, round(extra_detour_km, 2), round(extra_detour_min, 1), round(direct_km, 2), False, None, matched_geom, is_fallback
