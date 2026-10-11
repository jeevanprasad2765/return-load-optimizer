from typing import Tuple, Optional
from return_load_matcher.models import TripInfo, ShipmentInfo

# Compatibility Matrix
# Key: required_vehicle_type, Value: list of compatible truck vehicle_types with compatibility scores
COMPATIBILITY_RULES = {
    "open": {
        "open": 100.0,
        "flatbed": 90.0,
        "closed": 80.0,
        "container": 80.0,
    },
    "closed": {
        "closed": 100.0,
        "container": 95.0,
        "refrigerated": 85.0,  # Refrigerated truck can carry general closed goods
    },
    "refrigerated": {
        "refrigerated": 100.0,
        # Cold chain goods cannot be carried by non-refrigerated trucks
    },
    "flatbed": {
        "flatbed": 100.0,
        "open": 85.0,
    },
    "container": {
        "container": 100.0,
        "closed": 90.0,
    }
}

def evaluate_vehicle_compatibility(
    trip: TripInfo,
    shipment: ShipmentInfo
) -> Tuple[float, bool, Optional[str]]:
    """
    Evaluates vehicle type compatibility.
    If no required_vehicle_type is specified by shipper, score is 100.
    If required_vehicle_type is specified:
      - Exact match = 100
      - Compatible match = matrix score
      - Incompatible = Hard rejection
    """
    req_type = shipment.required_vehicle_type
    truck_type = trip.vehicle_type

    if not req_type or req_type.strip() == "" or req_type.lower() == "any":
        return 100.0, False, None

    req_type = req_type.lower().strip()
    truck_type = truck_type.lower().strip()

    if req_type == truck_type:
        return 100.0, False, None

    allowed_types = COMPATIBILITY_RULES.get(req_type, {})
    if truck_type in allowed_types:
        score = allowed_types[truck_type]
        return score, False, None

    # Hard rejection
    return (
        0.0, True,
        f"Incompatible vehicle type: Shipment requires '{req_type}' truck, but truck is '{truck_type}'"
    )
