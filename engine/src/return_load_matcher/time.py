from datetime import datetime, timezone
from typing import Tuple, Optional
from return_load_matcher.models import TripInfo, ShipmentInfo

def evaluate_time_compatibility(
    trip: TripInfo,
    shipment: ShipmentInfo,
    estimated_drive_minutes: float = 0.0
) -> Tuple[float, bool, Optional[str]]:
    """
    Evaluates time compatibility.
    Hard reject if:
    - Pickup window start/end is provided and departure is too late or early.
    - Delivery deadline is provided and estimated arrival exceeds deadline.
    """
    departure = trip.departure_time

    # Ensure timezones match for comparison if set
    if departure.tzinfo is None:
        departure = departure.replace(tzinfo=timezone.utc)

    # Check pickup window start
    if shipment.pickup_window_start:
        p_start = shipment.pickup_window_start
        if p_start.tzinfo is None:
            p_start = p_start.replace(tzinfo=timezone.utc)
        
        # Departure before pickup window start is unacceptable if > 12 hours earlier
        if departure < p_start:
            hours_early = (p_start - departure).total_seconds() / 3600.0
            if hours_early > 12.0:
                return (
                    0.0, True,
                    f"Trip departs {hours_early:.1f} hours before shipment pickup window opens"
                )

    # Check pickup window end
    if shipment.pickup_window_end:
        p_end = shipment.pickup_window_end
        if p_end.tzinfo is None:
            p_end = p_end.replace(tzinfo=timezone.utc)

        if departure > p_end:
            hours_late = (departure - p_end).total_seconds() / 3600.0
            return (
                0.0, True,
                f"Trip departs {hours_late:.1f} hours after shipment pickup window closes"
            )

    # Check delivery deadline
    if shipment.delivery_deadline:
        d_deadline = shipment.delivery_deadline
        if d_deadline.tzinfo is None:
            d_deadline = d_deadline.replace(tzinfo=timezone.utc)

        estimated_arrival_seconds = estimated_drive_minutes * 60.0
        arrival_time = datetime.fromtimestamp(departure.timestamp() + estimated_arrival_seconds, tz=timezone.utc)

        if arrival_time > d_deadline:
            hours_late = (arrival_time - d_deadline).total_seconds() / 3600.0
            return (
                0.0, True,
                f"Estimated delivery time is {hours_late:.1f} hours past delivery deadline"
            )

    # Score calculation
    # If no time constraints, give high score
    if not (shipment.pickup_window_start or shipment.pickup_window_end or shipment.delivery_deadline):
        return 100.0, False, None

    score_components = []

    if shipment.pickup_window_start and shipment.pickup_window_end:
        p_start = shipment.pickup_window_start.replace(tzinfo=timezone.utc) if shipment.pickup_window_start.tzinfo is None else shipment.pickup_window_start
        p_end = shipment.pickup_window_end.replace(tzinfo=timezone.utc) if shipment.pickup_window_end.tzinfo is None else shipment.pickup_window_end
        window_duration = max(1.0, (p_end - p_start).total_seconds() / 3600.0)
        
        # Perfect score if right in the middle of window
        midpoint = p_start.timestamp() + ((p_end - p_start).total_seconds() / 2.0)
        diff_hours = abs(departure.timestamp() - midpoint) / 3600.0
        window_score = max(50.0, 100.0 - ((diff_hours / window_duration) * 50.0))
        score_components.append(window_score)

    if shipment.delivery_deadline:
        d_deadline = shipment.delivery_deadline.replace(tzinfo=timezone.utc) if shipment.delivery_deadline.tzinfo is None else shipment.delivery_deadline
        arrival_time = datetime.fromtimestamp(departure.timestamp() + (estimated_drive_minutes * 60.0), tz=timezone.utc)
        slack_hours = (d_deadline - arrival_time).total_seconds() / 3600.0
        # Optimal slack is 2 to 6 hours before deadline
        if slack_hours >= 2.0:
            deadline_score = 100.0
        else:
            deadline_score = max(60.0, 60.0 + (slack_hours * 20.0))
        score_components.append(deadline_score)

    final_score = sum(score_components) / len(score_components) if score_components else 100.0
    return round(final_score, 2), False, None
