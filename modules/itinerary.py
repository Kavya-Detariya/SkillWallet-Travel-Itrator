"""
Itinerary processing engine, demo day synthesis, cost recalculation, and geographic clustering logic.
"""

import copy
import random
from typing import Dict, Any, List
from modules.destinations import get_destination_data, DESTINATIONS_DB
from modules.utils import USD_TO_INR

ACCOMMODATION_RATES_PER_NIGHT_INR = {
    "Budget": 2000,
    "Moderate": 4500,
    "Luxury": 12000
}

def recalculate_itinerary_costs(itinerary: Dict[str, Any], budget_tier: str = "Moderate") -> None:
    """Ensure all daily cost breakdowns and total trip summaries are strictly synchronized."""
    days = itinerary.get("days", [])
    total_activities = 0
    total_food = 0
    total_transport = 0

    tier_key = budget_tier.capitalize() if budget_tier else "Moderate"
    nightly_rate = ACCOMMODATION_RATES_PER_NIGHT_INR.get(tier_key, 4500)

    for day in days:
        # Sum morning, lunch, afternoon, evening
        m_cost = int(day.get("morning", {}).get("cost_inr", 0) or 0)
        l_cost = int(day.get("lunch", {}).get("cost_inr", 0) or 0)
        a_cost = int(day.get("afternoon", {}).get("cost_inr", 0) or 0)
        e_cost = int(day.get("evening", {}).get("cost_inr", 0) or 0)

        act_cost = m_cost + a_cost
        food_cost = l_cost + (e_cost if "dining" in day.get("evening", {}).get("category", "").lower() or "food" in day.get("evening", {}).get("category", "").lower() else int(e_cost * 0.6))
        # remainder of evening to activities or entertainment
        evening_extra_act = e_cost - (e_cost if "dining" in day.get("evening", {}).get("category", "").lower() or "food" in day.get("evening", {}).get("category", "").lower() else int(e_cost * 0.6))
        act_cost += evening_extra_act

        # Transport estimate per day based on tier
        trans_cost = 400 if tier_key == "Budget" else (700 if tier_key == "Moderate" else 1500)

        day_total = m_cost + l_cost + a_cost + e_cost + trans_cost
        day["daily_cost"] = {
            "activities": act_cost,
            "food": food_cost,
            "transport": trans_cost,
            "total": day_total
        }

        total_activities += act_cost
        total_food += food_cost
        total_transport += trans_cost

    num_nights = max(1, len(days))
    total_accommodation = num_nights * nightly_rate
    trip_total_inr = total_activities + total_food + total_transport + total_accommodation
    trip_total_usd = round(trip_total_inr / USD_TO_INR, 2)

    itinerary["cost_summary"] = {
        "activities_total": total_activities,
        "food_total": total_food,
        "transport_total": total_transport,
        "accommodation_estimated": total_accommodation,
        "trip_total_inr": trip_total_inr,
        "trip_total_usd": trip_total_usd
    }
    itinerary["total_estimated_cost"] = trip_total_inr

def build_demo_itinerary(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Build a realistic demo itinerary using predefined destination clusters or intelligent synthesis."""
    dest_name = preferences.get("destination", "Goa")
    duration = int(preferences.get("duration", 3))
    budget_tier = preferences.get("budget_tier", "Moderate")
    dietary = preferences.get("dietary", "No preference")
    vibe = preferences.get("vibe", "Beach")

    dest_data = get_destination_data(dest_name)
    country = dest_data.get("country", "Global") if dest_data else "International"

    days_list = []
    
    # If we have curated clusters for this destination in DESTINATIONS_DB
    if dest_data and "clusters" in dest_data:
        cluster_items = list(dest_data["clusters"].items())
        for d in range(1, duration + 1):
            cluster_idx = (d - 1) % len(cluster_items)
            area_name, activities = cluster_items[cluster_idx]
            
            # Select 4 items for Morning, Lunch, Afternoon, Evening
            morning_item = activities[0] if len(activities) > 0 else {"name": f"{dest_name} Morning Walk", "cat": "Sightseeing", "cost": 300, "dur": "2.5 hrs"}
            lunch_item = activities[2] if len(activities) > 2 else {"name": f"Local {dest_name} Bistro Lunch", "cat": "Food & Dining", "cost": 800, "dur": "1.5 hrs"}
            afternoon_item = activities[1] if len(activities) > 1 else {"name": f"{dest_name} Landmark Discovery", "cat": "Culture", "cost": 250, "dur": "2.0 hrs"}
            evening_item = activities[3] if len(activities) > 3 else {"name": f"Evening Sunset & Dining", "cat": "Dining & Nightlife", "cost": 1400, "dur": "2.5 hrs"}
            
            # Dietary customization
            lunch_desc = f"Handpicked meal highlighting local ingredients. Catering to {dietary} preferences." if dietary != "No preference" else "Authentic regional lunch featuring local specialties."

            day_obj = {
                "day": d,
                "theme": f"Exploring {area_name.split(' - ')[-1] if ' - ' in area_name else area_name}",
                "area": area_name,
                "morning": {
                    "name": morning_item["name"],
                    "description": f"Immerse yourself in {morning_item['name']}, nestled in the {area_name} district.",
                    "time": "09:00 - 11:30",
                    "duration": morning_item.get("dur", "2.5 hrs"),
                    "cost_inr": morning_item.get("cost", 400),
                    "category": morning_item.get("cat", "Sightseeing"),
                    "location": f"{morning_item['name']}, {area_name}"
                },
                "lunch": {
                    "name": lunch_item["name"],
                    "description": lunch_desc,
                    "time": "12:30 - 14:00",
                    "duration": lunch_item.get("dur", "1.5 hrs"),
                    "cost_inr": lunch_item.get("cost", 850),
                    "category": lunch_item.get("cat", "Food & Dining"),
                    "location": f"{lunch_item['name']}, {area_name}"
                },
                "afternoon": {
                    "name": afternoon_item["name"],
                    "description": f"Continue through {area_name} with an afternoon exploring local landmarks and hidden sights.",
                    "time": "15:00 - 17:00",
                    "duration": afternoon_item.get("dur", "2.0 hrs"),
                    "cost_inr": afternoon_item.get("cost", 300),
                    "category": afternoon_item.get("cat", "Culture"),
                    "location": f"{afternoon_item['name']}, {area_name}"
                },
                "evening": {
                    "name": evening_item["name"],
                    "description": f"Wind down your day in {area_name} with vibrant local dining and atmospheric evening views.",
                    "time": "18:00 - 21:00",
                    "duration": evening_item.get("dur", "3.0 hrs"),
                    "cost_inr": evening_item.get("cost", 1500),
                    "category": evening_item.get("cat", "Dining & Nightlife"),
                    "location": f"{evening_item['name']}, {area_name}"
                }
            }
            days_list.append(day_obj)
    else:
        # Synthesize realistic clustered days for any custom destination entered by user
        areas = [
            f"Central {dest_name} Heritage District",
            f"Old Town & Waterfront Quarter",
            f"Arts & Garden District",
            f"Uptown & Panoramic Hills"
        ]
        for d in range(1, duration + 1):
            area = areas[(d - 1) % len(areas)]
            days_list.append({
                "day": d,
                "theme": f"Highlights of {area}",
                "area": area,
                "morning": {
                    "name": f"{dest_name} Historical Landmark & Plaza",
                    "description": f"Start the morning in {area} discovering celebrated architecture and scenic viewpoints.",
                    "time": "09:00 - 11:30",
                    "duration": "2.5 hours",
                    "cost_inr": 450,
                    "category": "Sightseeing & Architecture",
                    "location": area
                },
                "lunch": {
                    "name": f"{dest_name} Local Flavors Bistro",
                    "description": f"Delicious regional cuisine suited to {dietary} dietary choices.",
                    "time": "12:30 - 14:00",
                    "duration": "1.5 hours",
                    "cost_inr": 850,
                    "category": "Food & Dining",
                    "location": area
                },
                "afternoon": {
                    "name": f"{area} Artisan Market & Cultural Walk",
                    "description": f"Stroll through pedestrian promenades, artisan stalls, and boutique galleries.",
                    "time": "15:00 - 17:30",
                    "duration": "2.5 hours",
                    "cost_inr": 300,
                    "category": "Culture & Shopping",
                    "location": area
                },
                "evening": {
                    "name": f"Twilight Dining & Scenic Viewpoint in {area}",
                    "description": f"Relaxing evening dinner with ambient music and sunset vistas.",
                    "time": "18:30 - 21:30",
                    "duration": "3.0 hours",
                    "cost_inr": 1600,
                    "category": "Dining & Leisure",
                    "location": area
                }
            })

    result = {
        "destination": dest_name,
        "country": country,
        "days": days_list
    }
    recalculate_itinerary_costs(result, budget_tier)
    return result

def build_demo_day(destination: str, day_num: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize a fresh, cohesive alternative day for single-day regeneration."""
    budget_tier = preferences.get("budget_tier", "Moderate")
    dietary = preferences.get("dietary", "No preference")
    vibe = preferences.get("vibe", "Cultural")

    fresh_areas = [
        f"Artisans & Riverside Quarter, {destination}",
        f"Hillside Heritage & Vista Heights, {destination}",
        f"Botanical Gardens & Old Bazaars, {destination}",
        f"Modern Coastal Promenade, {destination}"
    ]
    area = fresh_areas[(day_num * 2 + 1) % len(fresh_areas)]

    new_day = {
        "day": day_num,
        "theme": f"Fresh Discovery: {area}",
        "area": area,
        "morning": {
            "name": f"Sunrise Heritage Walk & Tea/Coffee",
            "description": f"Early morning guided stroll through the serene alleyways and morning markets of {area}.",
            "time": "08:30 - 11:00",
            "duration": "2.5 hours",
            "cost_inr": 350,
            "category": "Culture & Photography",
            "location": area
        },
        "lunch": {
            "name": f"Garden Terrace Cafe ({dietary} friendly)",
            "description": f"Fresh seasonal produce and hearty dishes in a lush courtyard setting.",
            "time": "12:00 - 13:30",
            "duration": "1.5 hours",
            "cost_inr": 800,
            "category": "Food & Dining",
            "location": area
        },
        "afternoon": {
            "name": f"Interactive Craft Workshop & Museum Tour",
            "description": f"Hands-on cultural experience with local artisans in {area}.",
            "time": "14:30 - 17:00",
            "duration": "2.5 hours",
            "cost_inr": 550,
            "category": "Culture & Workshop",
            "location": area
        },
        "evening": {
            "name": f"Rooftop Sunset Lounge & Regional Tasting Menu",
            "description": f"Breathtaking skyline views paired with craft mocktails and local delicacies.",
            "time": "18:00 - 21:00",
            "duration": "3.0 hours",
            "cost_inr": 1800,
            "category": "Dining & Entertainment",
            "location": area
        }
    }
    
    # Calculate daily cost
    m_cost = new_day["morning"]["cost_inr"]
    l_cost = new_day["lunch"]["cost_inr"]
    a_cost = new_day["afternoon"]["cost_inr"]
    e_cost = new_day["evening"]["cost_inr"]
    trans_cost = 600
    
    new_day["daily_cost"] = {
        "activities": m_cost + a_cost,
        "food": l_cost + int(e_cost * 0.7),
        "transport": trans_cost,
        "total": m_cost + l_cost + a_cost + e_cost + trans_cost
    }
    return new_day

def get_demo_activity_swap(destination: str, area: str, slot_name: str, user_request: str, budget_tier: str) -> Dict[str, Any]:
    """Generate an activity swap accurately tailored to common user requests."""
    req_lower = user_request.lower()
    
    # Check common swap themes
    if "vegetarian" in req_lower or "vegan" in req_lower or "food" in req_lower or "lunch" in req_lower:
        return {
            "name": f"Sattva Organic Herbivore Kitchen ({area})",
            "description": f"Farm-fresh 100% vegetarian & vegan specialties crafted with local organic produce. Perfect answer to '{user_request}'.",
            "time": "12:30 - 14:00",
            "duration": "1.5 hours",
            "cost_inr": 650,
            "category": "Food & Dining",
            "location": f"{area} Culinary Alley"
        }
    elif "adventure" in req_lower or "thrill" in req_lower or "outdoor" in req_lower or "hike" in req_lower:
        return {
            "name": f"Outdoor Cliff Trail & Kayak Adventure",
            "description": f"Guided active exploration matching your request for '{user_request}' in {area}.",
            "time": "14:30 - 17:00",
            "duration": "2.5 hours",
            "cost_inr": 1200,
            "category": "Adventure & Nature",
            "location": f"{area} Waterfront / Ridge"
        }
    elif "cheap" in req_lower or "free" in req_lower or "budget" in req_lower:
        return {
            "name": f"Public Botanical Gardens & Sculpture Walk",
            "description": f"Peaceful scenic walking paths and open-air public art with free admission, answering '{user_request}'.",
            "time": "15:00 - 17:00",
            "duration": "2.0 hours",
            "cost_inr": 50,
            "category": "Nature & Leisure",
            "location": f"{area} Public Gardens"
        }
    elif "market" in req_lower or "shop" in req_lower:
        return {
            "name": f"{area} Street Artisan Bazaar & Flea Market",
            "description": f"Vibrant open-air market with local textile weavers, spices, and handmade souvenirs.",
            "time": "15:00 - 17:30",
            "duration": "2.5 hours",
            "cost_inr": 200,
            "category": "Shopping & Culture",
            "location": f"{area} Market Square"
        }
    elif "relax" in req_lower or "chill" in req_lower or "slow" in req_lower:
        return {
            "name": f"Ayurvedic Herbal Tea Lounge & Zen Courtyard",
            "description": f"Soothing relaxation stop featuring organic herbal infusions and quiet reading corners in {area}.",
            "time": "15:30 - 17:30",
            "duration": "2.0 hours",
            "cost_inr": 350,
            "category": "Wellness & Relaxation",
            "location": f"{area} Courtyard"
        }
    else:
        return {
            "name": f"Custom Curated Experience in {area}",
            "description": f"Tailored activity honoring '{user_request}' while keeping you comfortably clustered in {area}.",
            "time": "15:00 - 17:00",
            "duration": "2.0 hours",
            "cost_inr": 500,
            "category": "Tailored Leisure",
            "location": area
        }

