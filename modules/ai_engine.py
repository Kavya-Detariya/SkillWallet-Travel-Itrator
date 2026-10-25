"""
AI Engine: Unified abstraction layer supporting Gemini, Groq, and Demo Mode fallbacks.
Handles:
- Destination Recommendations
- Day-by-Day Structured Itinerary Generation with Geographic Clustering
- Activity Swapping
- Single-Day Regeneration
"""

import json
import requests
from typing import Dict, Any, List, Optional, Tuple

from modules.destinations import get_demo_recommendations, get_destination_data, DESTINATIONS_DB
from modules.utils import extract_json_from_text

# System prompts for structured generation
ITINERARY_SYSTEM_PROMPT = """You are an expert luxury and cultural travel planner.
You specialize in designing highly curated, geographically clustered daily itineraries.
CRITICAL RULES FOR GEOGRAPHIC CLUSTERING:
1. Group nearby morning, lunch, afternoon, and evening venues in the same district/neighborhood each day.
2. Minimize cross-city travel and avoid backtracking.
3. Every day must include an explicit "area" or "neighborhood" tag explaining the cluster.
4. Costs must be realistic estimates in local currency or INR.
5. Provide structured JSON ONLY. Do not wrap in conversational prose.
"""

def call_gemini_api(prompt: str, system_prompt: str, api_key: str, model: str = "gemini-1.5-flash") -> Tuple[Optional[str], Optional[str]]:
    """Call Google Gemini REST endpoint directly for highest reliability."""
    if not api_key or not api_key.strip():
        return None, "Gemini API key is missing."
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=40)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", ""), None
            return None, "Empty response from Gemini."
        elif resp.status_code == 400:
            # Fallback without responseMimeType in case older models reject it
            payload["generationConfig"].pop("responseMimeType", None)
            resp2 = requests.post(url, headers=headers, json=payload, timeout=40)
            if resp2.status_code == 200:
                data = resp2.json()
                return data["candidates"][0]["content"]["parts"][0]["text"], None
            err_msg = resp.json().get("error", {}).get("message", resp.text)
            return None, f"Gemini API Error (400): {err_msg}"
        elif resp.status_code == 403 or resp.status_code == 401:
            return None, "Authentication failed: Please verify your Gemini API key."
        elif resp.status_code == 429:
            return None, "Gemini rate limit exceeded. Please wait a moment or switch to Demo Mode."
        else:
            return None, f"Gemini API returned HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.exceptions.Timeout:
        return None, "Gemini API timed out after 40 seconds. Check connection."
    except Exception as e:
        return None, f"Failed to connect to Gemini API: {str(e)}"

def call_groq_api(prompt: str, system_prompt: str, api_key: str, model: str = "llama-3.3-70b-versatile") -> Tuple[Optional[str], Optional[str]]:
    """Call Groq OpenAI-compatible chat completions endpoint."""
    if not api_key or not api_key.strip():
        return None, "Groq API key is missing."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt + "\nReturn ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=35)
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"], None
        elif resp.status_code in [401, 403]:
            return None, "Authentication failed: Please verify your Groq API key."
        elif resp.status_code == 429:
            return None, "Groq rate limit exceeded. Please wait a moment or switch to Demo Mode."
        else:
            # Retry without response_format if model doesn't support json_object
            payload.pop("response_format", None)
            resp2 = requests.post(url, headers=headers, json=payload, timeout=35)
            if resp2.status_code == 200:
                data = resp2.json()
                return data["choices"][0]["message"]["content"], None
            err_msg = resp.json().get("error", {}).get("message", resp.text)
            return None, f"Groq API Error ({resp.status_code}): {err_msg}"
    except requests.exceptions.Timeout:
        return None, "Groq API timed out after 35 seconds. Check connection."
    except Exception as e:
        return None, f"Failed to connect to Groq API: {str(e)}"

def call_ai(prompt: str, system_prompt: str, provider: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """Route to selected AI provider."""
    provider_norm = provider.lower() if provider else "gemini"
    if "groq" in provider_norm:
        return call_groq_api(prompt, system_prompt, api_key)
    else:
        return call_gemini_api(prompt, system_prompt, api_key)

# ----------------- DESTINATION RECOMMENDATIONS -----------------

def generate_destination_recommendations(preferences: Dict[str, Any], provider: str, api_key: str, is_demo: bool = False) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Generate top 3 recommendations based on travel preferences."""
    vibe = preferences.get("vibe", "Cultural")
    budget = preferences.get("budget_tier", "Moderate")
    party = preferences.get("travel_party", "Couple")
    pace = preferences.get("pace", "Moderate")
    interests = preferences.get("interests", ["Food", "History"])
    duration = preferences.get("duration", 3)
    
    if is_demo or not api_key:
        return get_demo_recommendations(vibe, budget, party, pace, interests, top_n=3), None
        
    prompt = f"""
Recommend the top 3 best holiday travel destinations in the world matching these criteria:
- Open-ended travel vibe: {vibe}
- Budget Tier: {budget}
- Travel Party: {party}
- Preferred Pace: {pace}
- Specific Interests: {', '.join(interests)}
- Duration: {duration} days

Return a JSON array of exactly 3 objects with this exact structure:
[
  {{
    "destination": "City or Region name",
    "country": "Country name",
    "why_it_matches": "Detailed 2-3 sentences explaining why it fits the vibe, pace, and party.",
    "best_for": "3 highlights separated by bullets e.g. Culture • Food • History",
    "estimated_budget_category": "{budget}",
    "avg_daily_budget_inr": 5000,
    "season_suitability": "Ideal months to visit",
    "highlight_tags": ["#Tag1", "#Tag2", "#Tag3", "#Tag4"],
    "hero_image": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80"
  }}
]
"""
    raw_text, err = call_ai(prompt, "You are a world travel consultant. Return ONLY a valid JSON array.", provider, api_key)
    if err:
        fallback = get_demo_recommendations(vibe, budget, party, pace, interests, top_n=3)
        return fallback, f"API notice: {err} (Showing curated recommendations)"
        
    parsed = extract_json_from_text(raw_text)
    if isinstance(parsed, list) and len(parsed) >= 1:
        # Guarantee image fallback if empty
        for idx, item in enumerate(parsed):
            if not item.get("hero_image"):
                item["hero_image"] = DESTINATIONS_DB[idx % len(DESTINATIONS_DB)]["hero_image"]
        return parsed, None
    elif isinstance(parsed, dict) and "destinations" in parsed and isinstance(parsed["destinations"], list):
        return parsed["destinations"], None
    else:
        fallback = get_demo_recommendations(vibe, budget, party, pace, interests, top_n=3)
        return fallback, "Could not parse AI output format; falling back to curated recommendations."

# ----------------- ITINERARY GENERATION -----------------

def generate_itinerary(preferences: Dict[str, Any], provider: str, api_key: str, is_demo: bool = False) -> Tuple[Dict[str, Any], Optional[str]]:
    """Generate structured day-by-day itinerary with geographic clustering and cost tracking."""
    destination = preferences.get("destination", "Goa")
    vibe = preferences.get("vibe", "Beach")
    duration = int(preferences.get("duration", 3))
    budget_tier = preferences.get("budget_tier", "Moderate")
    party = preferences.get("travel_party", "Couple")
    pace = preferences.get("pace", "Moderate")
    interests = preferences.get("interests", ["Food", "Culture"])
    dietary = preferences.get("dietary", "No preference")
    notes = preferences.get("notes", "")

    # Check if we should use demo mode or offline database
    if is_demo or not api_key:
        from modules.itinerary import build_demo_itinerary
        return build_demo_itinerary(preferences), None

    prompt = f"""
Plan a complete {duration}-day travel itinerary for {destination}.
Preferences:
- Travel Vibe: {vibe}
- Budget Tier: {budget_tier}
- Travel Party: {party}
- Travel Pace: {pace}
- Interests: {', '.join(interests)}
- Dietary Preference: {dietary}
- Custom notes: {notes}

MANDATORY GEOGRAPHIC CLUSTERING:
Group nearby attractions in the same neighborhood for each day to eliminate unnecessary cross-town transit.

Return a JSON object matching this schema:
{{
  "destination": "{destination}",
  "country": "Country name",
  "days": [
    {{
      "day": 1,
      "theme": "Theme of Day 1",
      "area": "Specific neighborhood/district cluster name",
      "morning": {{
        "name": "Activity Name",
        "description": "Engaging 2-sentence description",
        "time": "09:00 - 11:30",
        "duration": "2.5 hours",
        "cost_inr": 400,
        "category": "Culture / Sightseeing",
        "location": "Neighborhood & Landmark"
      }},
      "lunch": {{
        "name": "Restaurant / Food Spot",
        "description": "Cuisine highlights matching dietary preference ({dietary})",
        "time": "12:30 - 14:00",
        "duration": "1.5 hours",
        "cost_inr": 800,
        "category": "Food & Dining",
        "location": "Neighborhood"
      }},
      "afternoon": {{
        "name": "Afternoon Leisure or Sight",
        "description": "Engaging description",
        "time": "14:30 - 17:00",
        "duration": "2.5 hours",
        "cost_inr": 300,
        "category": "Sightseeing / Adventure",
        "location": "Nearby Neighborhood"
      }},
      "evening": {{
        "name": "Evening Dining / Entertainment",
        "description": "Atmospheric evening experience",
        "time": "18:00 - 21:00",
        "duration": "3.0 hours",
        "cost_inr": 1500,
        "category": "Dining & Nightlife",
        "location": "Nearby Neighborhood"
      }},
      "daily_cost": {{
        "activities": 700,
        "food": 2300,
        "transport": 500,
        "total": 3500
      }}
    }}
  ],
  "cost_summary": {{
    "activities_total": 0,
    "food_total": 0,
    "transport_total": 0,
    "accommodation_estimated": 0,
    "trip_total_inr": 0,
    "trip_total_usd": 0
  }}
}}
Make sure to provide all {duration} days in the "days" array. Calculate sums accurately.
"""
    raw_text, err = call_ai(prompt, ITINERARY_SYSTEM_PROMPT, provider, api_key)
    if err:
        from modules.itinerary import build_demo_itinerary
        demo_itin = build_demo_itinerary(preferences)
        return demo_itin, f"AI generation warning: {err}. Loaded curated fallback itinerary."
        
    parsed = extract_json_from_text(raw_text)
    if isinstance(parsed, dict) and "days" in parsed and len(parsed["days"]) > 0:
        # Recalculate totals to guarantee arithmetic integrity
        from modules.itinerary import recalculate_itinerary_costs
        recalculate_itinerary_costs(parsed, budget_tier)
        return parsed, None
    else:
        from modules.itinerary import build_demo_itinerary
        demo_itin = build_demo_itinerary(preferences)
        return demo_itin, "AI response could not be parsed as valid itinerary JSON. Loaded curated fallback."

# ----------------- VIBE CUSTOMIZATION & ACTIVITY SWAP -----------------

def swap_activity_ai(
    destination: str,
    day_num: int,
    area: str,
    slot_name: str,
    current_activity: Dict[str, Any],
    user_request: str,
    dietary: str,
    budget_tier: str,
    provider: str,
    api_key: str,
    is_demo: bool = False
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Swap a single activity while preserving neighborhood clustering and trip coherence.
    Returns replacement activity dict.
    """
    if is_demo or not api_key:
        from modules.itinerary import get_demo_activity_swap
        return get_demo_activity_swap(destination, area, slot_name, user_request, budget_tier), None

    prompt = f"""
In the travel itinerary for {destination}, Day {day_num} is clustered in the area: "{area}".
The current {slot_name} activity is:
Name: {current_activity.get('name')}
Category: {current_activity.get('category')}
Description: {current_activity.get('description')}
Cost: ₹{current_activity.get('cost_inr', 500)}

The traveler requested: "{user_request}"
Dietary restriction: {dietary}
Budget tier: {budget_tier}

Generate a single replacement activity that strictly honors the user's request AND remains in or very near "{area}".
Return ONLY this JSON object:
{{
  "name": "Replacement Activity Name",
  "description": "Engaging description explaining why this fulfills the request",
  "time": "{current_activity.get('time', '14:00 - 16:30')}",
  "duration": "{current_activity.get('duration', '2.0 hours')}",
  "cost_inr": 600,
  "category": "Appropriate category",
  "location": "Neighborhood location in {area}"
}}
"""
    raw_text, err = call_ai(prompt, "You are an expert local guide. Return ONLY valid JSON.", provider, api_key)
    if err:
        from modules.itinerary import get_demo_activity_swap
        return get_demo_activity_swap(destination, area, slot_name, user_request, budget_tier), f"Notice: {err} (Applied curated swap)"
        
    parsed = extract_json_from_text(raw_text)
    if isinstance(parsed, dict) and "name" in parsed:
        return parsed, None
    else:
        from modules.itinerary import get_demo_activity_swap
        return get_demo_activity_swap(destination, area, slot_name, user_request, budget_tier), "Parsing failed; applied curated swap."

# ----------------- DAY REGENERATION -----------------

def regenerate_single_day_ai(
    destination: str,
    day_num: int,
    preferences: Dict[str, Any],
    other_days_areas: List[str],
    provider: str,
    api_key: str,
    is_demo: bool = False
) -> Tuple[Dict[str, Any], Optional[str]]:
    """Regenerate a single day with fresh activities in a new or refined cluster."""
    budget_tier = preferences.get("budget_tier", "Moderate")
    dietary = preferences.get("dietary", "No preference")
    vibe = preferences.get("vibe", "Cultural")
    interests = preferences.get("interests", ["Food", "History"])

    if is_demo or not api_key:
        from modules.itinerary import build_demo_day
        return build_demo_day(destination, day_num, preferences), None

    prompt = f"""
Regenerate ONLY Day {day_num} for a trip to {destination}.
Preferences:
- Vibe: {vibe}
- Budget Tier: {budget_tier}
- Dietary: {dietary}
- Interests: {', '.join(interests)}
- Other days in the itinerary have covered these areas: {', '.join(other_days_areas)}

Please pick a fresh, cohesive neighborhood/area for Day {day_num} that hasn't been overly repeated.
Return ONLY this JSON object for Day {day_num}:
{{
  "day": {day_num},
  "theme": "Fresh theme for this day",
  "area": "Cohesive neighborhood cluster",
  "morning": {{
    "name": "Morning activity",
    "description": "Description",
    "time": "09:00 - 11:30",
    "duration": "2.5 hours",
    "cost_inr": 400,
    "category": "Sightseeing",
    "location": "Specific location"
  }},
  "lunch": {{
    "name": "Lunch spot",
    "description": "Description matching {dietary}",
    "time": "12:30 - 14:00",
    "duration": "1.5 hours",
    "cost_inr": 800,
    "category": "Food & Dining",
    "location": "Specific location"
  }},
  "afternoon": {{
    "name": "Afternoon activity",
    "description": "Description",
    "time": "14:30 - 17:00",
    "duration": "2.5 hours",
    "cost_inr": 350,
    "category": "Culture / Leisure",
    "location": "Specific location"
  }},
  "evening": {{
    "name": "Evening dining / leisure",
    "description": "Description",
    "time": "18:00 - 21:00",
    "duration": "3.0 hours",
    "cost_inr": 1500,
    "category": "Dining & Entertainment",
    "location": "Specific location"
  }},
  "daily_cost": {{
    "activities": 750,
    "food": 2300,
    "transport": 500,
    "total": 3550
  }}
}}
"""
    raw_text, err = call_ai(prompt, ITINERARY_SYSTEM_PROMPT, provider, api_key)
    if err:
        from modules.itinerary import build_demo_day
        return build_demo_day(destination, day_num, preferences), f"Notice: {err} (Generated fresh curated day)"
        
    parsed = extract_json_from_text(raw_text)
    if isinstance(parsed, dict) and "morning" in parsed:
        parsed["day"] = day_num
        return parsed, None
    else:
        from modules.itinerary import build_demo_day
        return build_demo_day(destination, day_num, preferences), "Parsing failed; generated fresh curated day."

