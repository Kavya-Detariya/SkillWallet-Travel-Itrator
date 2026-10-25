"""
Trip Persistence Layer: Local JSON storage & Streamlit session synchronization.
Provides full CRUD: Save, Load, Rename, Delete, Duplicate, Export.
"""

import os
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
TRIPS_FILE = os.path.join(DATA_DIR, "trips.json")

def ensure_data_file():
    """Ensure data directory and trips.json exist."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(TRIPS_FILE):
            with open(TRIPS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
    except Exception as e:
        print(f"Warning: Storage initialization fallback ({e})")

def load_all_trips() -> List[Dict[str, Any]]:
    """Load all saved trips from local JSON file."""
    ensure_data_file()
    try:
        if os.path.exists(TRIPS_FILE):
            with open(TRIPS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
    except Exception as e:
        print(f"Error reading trips from {TRIPS_FILE}: {e}")
    return []

def save_all_trips(trips: List[Dict[str, Any]]) -> bool:
    """Save all trips list back to local JSON file."""
    ensure_data_file()
    try:
        with open(TRIPS_FILE, "w", encoding="utf-8") as f:
            json.dump(trips, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing trips to {TRIPS_FILE}: {e}")
        return False

def save_trip(title: str, destination: str, country: str, preferences: Dict[str, Any], itinerary: Dict[str, Any], estimated_cost: float, trip_id: Optional[str] = None) -> Dict[str, Any]:
    """Create or update a saved trip."""
    trips = load_all_trips()
    now_iso = datetime.datetime.now().isoformat()
    
    if trip_id:
        # Update existing
        for t in trips:
            if t.get("id") == trip_id:
                t["title"] = title
                t["destination"] = destination
                t["country"] = country
                t["preferences"] = preferences
                t["itinerary"] = itinerary
                t["estimated_cost"] = estimated_cost
                t["updated_at"] = now_iso
                save_all_trips(trips)
                return t
                
    # Create new
    new_id = trip_id or f"trip_{uuid.uuid4().hex[:8]}"
    new_trip = {
        "id": new_id,
        "title": title or f"Trip to {destination}",
        "created_at": now_iso,
        "destination": destination,
        "country": country,
        "preferences": preferences,
        "itinerary": itinerary,
        "estimated_cost": estimated_cost
    }
    trips.insert(0, new_trip)
    save_all_trips(trips)
    return new_trip

def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific trip by its ID."""
    trips = load_all_trips()
    for t in trips:
        if t.get("id") == trip_id:
            return t
    return None

def delete_trip(trip_id: str) -> bool:
    """Delete a trip by its ID."""
    trips = load_all_trips()
    original_len = len(trips)
    trips = [t for t in trips if t.get("id") != trip_id]
    if len(trips) < original_len:
        save_all_trips(trips)
        return True
    return False

def rename_trip(trip_id: str, new_title: str) -> bool:
    """Rename a saved trip."""
    trips = load_all_trips()
    for t in trips:
        if t.get("id") == trip_id:
            t["title"] = new_title
            save_all_trips(trips)
            return True
    return False

def duplicate_trip(trip_id: str) -> Optional[Dict[str, Any]]:
    """Clone an existing trip with a new ID and title."""
    trip = get_trip_by_id(trip_id)
    if not trip:
        return None
    new_trip = json.loads(json.dumps(trip))  # Deep copy
    new_trip["id"] = f"trip_{uuid.uuid4().hex[:8]}"
    new_trip["title"] = f"{trip.get('title', 'Trip')} (Copy)"
    new_trip["created_at"] = datetime.datetime.now().isoformat()
    trips = load_all_trips()
    trips.insert(0, new_trip)
    save_all_trips(trips)
    return new_trip

def export_trip_json(trip: Dict[str, Any]) -> str:
    """Export a trip as a clean JSON formatted string."""
    return json.dumps(trip, indent=2, ensure_ascii=False)

