from typing import List, Dict
from app.schemas.shipping import ShippingRate

# Define shipping zones and their base rates
SHIPPING_ZONES: Dict[str, Dict[str, float]] = {
    "US": {
        "standard": 5.99,
        "express": 12.99,
        "next_day": 24.99,
    },
    "CA": {
        "standard": 7.99,
        "express": 15.99,
        "next_day": 29.99,
    },
    "UK": {
        "standard": 8.99,
        "express": 16.99,
        "next_day": 34.99,
    },
    "EU": {
        "standard": 9.99,
        "express": 18.99,
        "next_day": 39.99,
    },
    "ASIA": {
        "standard": 12.99,
        "express": 24.99,
        "next_day": 49.99,
    },
    "OCEANIA": {
        "standard": 14.99,
        "express": 29.99,
        "next_day": 59.99,
    },
}

# Define country to zone mapping
COUNTRY_TO_ZONE: Dict[str, str] = {
    "US": "US",
    "CA": "CA",
    "GB": "UK",
    "UK": "UK",
    "DE": "EU",
    "FR": "EU",
    "IT": "EU",
    "ES": "EU",
    "CN": "ASIA",
    "JP": "ASIA",
    "KR": "ASIA",
    "AU": "OCEANIA",
    "NZ": "OCEANIA",
}

def get_shipping_zone(country: str) -> str:
    """Get the shipping zone for a given country code."""
    return COUNTRY_TO_ZONE.get(country.upper(), "US")

def is_remote_location(postal_code: str) -> bool:
    """
    Check if a postal code corresponds to a remote location.
    This is a simplified implementation. In a real application,
    you would use a geocoding service to determine the actual location.
    """
    # Example: Consider postal codes starting with '9' as remote
    return postal_code.startswith('9')

def calculate_distance_surcharge(postal_code: str) -> float:
    """
    Calculate additional surcharge based on distance.
    This is a simplified implementation. In a real application,
    you would use a distance calculation service.
    """
    if is_remote_location(postal_code):
        return 5.00
    return 0.00

def get_estimated_days(service: str, zone: str) -> str:
    """Get estimated delivery days based on service and zone."""
    estimates = {
        "standard": {
            "US": "3-5 days",
            "CA": "4-6 days",
            "UK": "4-6 days",
            "EU": "5-7 days",
            "ASIA": "7-10 days",
            "OCEANIA": "8-12 days",
        },
        "express": {
            "US": "2-3 days",
            "CA": "2-3 days",
            "UK": "2-3 days",
            "EU": "2-3 days",
            "ASIA": "3-5 days",
            "OCEANIA": "3-5 days",
        },
        "next_day": {
            "US": "1 day",
            "CA": "1-2 days",
            "UK": "1-2 days",
            "EU": "1-2 days",
            "ASIA": "2-3 days",
            "OCEANIA": "2-3 days",
        },
    }
    return estimates.get(service, {}).get(zone, "5-7 days")

async def calculate_shipping_rates(country: str, postal_code: str) -> List[ShippingRate]:
    """
    Calculate shipping rates based on country and postal code.
    This implementation includes:
    1. Zone-based pricing
    2. Remote location surcharges
    3. Distance-based surcharges
    4. Service-specific delivery estimates
    """
    # Get the shipping zone for the country
    zone = get_shipping_zone(country)
    
    # Get base rates for the zone
    zone_rates = SHIPPING_ZONES.get(zone, SHIPPING_ZONES["US"])
    
    # Calculate surcharges
    distance_surcharge = calculate_distance_surcharge(postal_code)
    
    # Generate shipping rates
    rates = []
    for service, base_rate in zone_rates.items():
        total_cost = base_rate + distance_surcharge
        estimated_days = get_estimated_days(service, zone)
        
        rates.append({
            "id": service,
            "name": f"{service.title()} Shipping",
            "description": f"Delivery in {estimated_days}",
            "cost": total_cost,
            "estimated_days": estimated_days,
        })
    
    return rates 