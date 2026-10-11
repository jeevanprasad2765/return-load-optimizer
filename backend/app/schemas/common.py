from datetime import datetime, timezone
from typing import Annotated, Optional
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator

def parse_utc_datetime(v: any) -> Optional[datetime]:
    if v is None:
        return None
    if isinstance(v, str):
        # Convert string to datetime, handling Z suffix
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    if isinstance(v, datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    return v

def format_utc_datetime(v: Optional[datetime]) -> Optional[str]:
    if v is None:
        return None
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    else:
        v = v.astimezone(timezone.utc)
    # Output standardized ISO 8601 with explicit Z suffix
    return v.strftime("%Y-%m-%dT%H:%M:%SZ")

UTCDateTime = Annotated[
    datetime,
    BeforeValidator(parse_utc_datetime),
    PlainSerializer(format_utc_datetime, return_type=str, when_used="json-unless-none"),
]

OptionalUTCDateTime = Annotated[
    Optional[datetime],
    BeforeValidator(parse_utc_datetime),
    PlainSerializer(format_utc_datetime, return_type=Optional[str], when_used="json-unless-none"),
]
