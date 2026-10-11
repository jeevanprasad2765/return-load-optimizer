from typing import Tuple, Optional
from return_load_matcher.models import TripInfo, ShipmentInfo

def evaluate_capacity_fit(
    trip: TripInfo,
    shipment: ShipmentInfo
) -> Tuple[float, bool, Optional[str]]:
    """
    Evaluates capacity fit.
    Hard rejection if shipment weight > available capacity.
    Score ranges from 0-100 based on capacity utilization.
    Higher utilization = higher score.
    """
    if shipment.weight_kg <= 0:
        return 0.0, True, "Shipment weight must be greater than zero kg"

    if trip.available_capacity_kg <= 0:
        return 0.0, True, "Trip has no available capacity"

    if shipment.weight_kg > trip.available_capacity_kg:
        return (
            0.0, True,
            f"Shipment weight ({shipment.weight_kg:.0f} kg) exceeds available trip capacity ({trip.available_capacity_kg:.0f} kg)"
        )

    # Utilization ratio: 0.0 to 1.0
    utilization_ratio = shipment.weight_kg / trip.available_capacity_kg
    
    # Scale from 50 to 100 for valid fits, rewarding higher utilization
    # A shipment taking 90% of capacity gets 95 points, taking 10% gets 55 points
    capacity_score = round(50.0 + (utilization_ratio * 50.0), 2)
    return capacity_score, False, None
