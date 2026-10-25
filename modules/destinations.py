"""
Predefined destination data and offline recommendation engine for Demo Mode.
Includes rich attributes for:
- Goa, Mumbai, Delhi, Jaipur, Kyoto, Paris, Bali, Singapore
"""

import random
from typing import List, Dict, Any

DESTINATIONS_DB: List[Dict[str, Any]] = [
    {
        "name": "Goa",
        "country": "India",
        "vibes": ["Beach", "Relaxation", "Adventure"],
        "budget_category": "Moderate",
        "avg_daily_budget_inr": 4000,
        "best_season": "October to March (Pleasant coastal breezes and lively beach shacks)",
        "best_for": "Beach Sunsets • Coastal Seafood • Portuguese Heritage",
        "highlight_tags": ["#BeachVibes", "#Seafood", "#PortugueseHeritage", "#Nightlife", "#WaterSports"],
        "hero_image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&q=80",
        "party_suitability": ["Friends", "Couple", "Solo", "Family"],
        "pace_match": ["Relaxed", "Moderate"],
        "clusters": {
            "North Goa - Panaji & Candolim": [
                {"name": "Fontainhas Latin Quarter Walking Tour", "cat": "Culture & Heritage", "cost": 300, "dur": "2.5 hrs"},
                {"name": "Aguada Fort & Lighthouse", "cat": "Sightseeing", "cost": 150, "dur": "2.0 hrs"},
                {"name": "Viva Panjim Heritage Lunch", "cat": "Food & Dining", "cost": 900, "dur": "1.5 hrs"},
                {"name": "Candolim Beach & Sunset Drinks", "cat": "Leisure", "cost": 800, "dur": "2.5 hrs"}
            ],
            "North Goa - Anjuna & Vagator": [
                {"name": "Anjuna Beach Watersports", "cat": "Adventure & Nature", "cost": 1500, "dur": "2.5 hrs"},
                {"name": "Artjuna Garden Cafe Brunch", "cat": "Food & Dining", "cost": 750, "dur": "1.5 hrs"},
                {"name": "Chapora Fort Panoramic Walk", "cat": "Sightseeing", "cost": 50, "dur": "2.0 hrs"},
                {"name": "Vagator Hilltop Sundowner", "cat": "Nightlife & Dining", "cost": 1600, "dur": "3.0 hrs"}
            ],
            "South Goa - Old Goa & Ponda": [
                {"name": "Basilica of Bom Jesus & Se Cathedral", "cat": "Culture & Heritage", "cost": 100, "dur": "2.0 hrs"},
                {"name": "Sahakari Spice Plantation Guided Tour", "cat": "Nature & Culture", "cost": 600, "dur": "2.5 hrs"},
                {"name": "Goan Organic Spice Buffet Lunch", "cat": "Food & Dining", "cost": 500, "dur": "1.5 hrs"},
                {"name": "Mandovi River Cruise & Folk Dance", "cat": "Leisure & Entertainment", "cost": 1100, "dur": "2.5 hrs"}
            ]
        }
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "vibes": ["Cultural", "Relaxation", "Nature"],
        "budget_category": "Moderate",
        "avg_daily_budget_inr": 8500,
        "best_season": "March to May (Cherry Blossoms) & Oct to Nov (Autumn Foliage)",
        "best_for": "Ancient Shrines • Zen Bamboo Groves • Traditional Kaiseki",
        "highlight_tags": ["#Culture", "#ZenGardens", "#Kaiseki", "#Photography", "#History"],
        "hero_image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
        "party_suitability": ["Couple", "Solo", "Family"],
        "pace_match": ["Relaxed", "Moderate"],
        "clusters": {
            "Arashiyama & Western Kyoto": [
                {"name": "Sagano Bamboo Forest & Tenryu-ji Zen Temple", "cat": "Nature & Culture", "cost": 500, "dur": "2.5 hrs"},
                {"name": "Togetsukyo Bridge & Matcha Ice Cream Walk", "cat": "Food & Leisure", "cost": 400, "dur": "1.5 hrs"},
                {"name": "Monkey Park Iwatayama Panorama", "cat": "Adventure & Nature", "cost": 600, "dur": "2.0 hrs"},
                {"name": "Traditional Soba Dining in Arashiyama", "cat": "Food & Dining", "cost": 1200, "dur": "1.5 hrs"}
            ],
            "Higashiyama & Gion District": [
                {"name": "Kiyomizu-dera Wooden Stage & City View", "cat": "Architecture & Culture", "cost": 600, "dur": "2.5 hrs"},
                {"name": "Sannenzaka & Ninenzaka Historic Streets", "cat": "Shopping & Photography", "cost": 400, "dur": "2.0 hrs"},
                {"name": "Nishiki Market Street Food Tasting", "cat": "Food & Dining", "cost": 1100, "dur": "2.0 hrs"},
                {"name": "Gion Evening Geisha District Lantern Walk", "cat": "Culture & Nightlife", "cost": 1500, "dur": "2.5 hrs"}
            ],
            "Fushimi & Southern Shrines": [
                {"name": "Fushimi Inari Taisha 1,000 Torii Gates", "cat": "History & Photography", "cost": 200, "dur": "3.0 hrs"},
                {"name": "Kizakura Kappa Sake Brewery & Museum", "cat": "Culture & Dining", "cost": 800, "dur": "1.5 hrs"},
                {"name": "Tofuku-ji Zen Rock Garden", "cat": "Relaxation & Architecture", "cost": 500, "dur": "2.0 hrs"},
                {"name": "Kamogawa Riverbank Evening Stroll & Yakitori", "cat": "Dining & Leisure", "cost": 1400, "dur": "2.5 hrs"}
            ]
        }
    },
    {
        "name": "Jaipur",
        "country": "India",
        "vibes": ["Cultural", "History", "Urban"],
        "budget_category": "Budget",
        "avg_daily_budget_inr": 3500,
        "best_season": "October to March (Cool, sunny, regal festival weather)",
        "best_for": "Royal Palaces • Heritage Bazaars • Rajasthani Thali",
        "highlight_tags": ["#PinkCity", "#FortsAndPalaces", "#RajasthaniFood", "#Shopping", "#History"],
        "hero_image": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&q=80",
        "party_suitability": ["Family", "Couple", "Solo", "Friends"],
        "pace_match": ["Moderate", "Fast-Paced"],
        "clusters": {
            "Amber & Old Royal Perimeter": [
                {"name": "Amber Fort Elephant Pathway & Sheesh Mahal", "cat": "Architecture & History", "cost": 500, "dur": "3.0 hrs"},
                {"name": "Panna Meena ka Kund Stepwell", "cat": "Photography & Architecture", "cost": 100, "dur": "1.0 hr"},
                {"name": "1135 AD Regal Amber Courtyard Dining", "cat": "Food & Dining", "cost": 1500, "dur": "1.5 hrs"},
                {"name": "Jal Mahal Lakeside Sunset View", "cat": "Sightseeing", "cost": 100, "dur": "1.5 hrs"}
            ],
            "Walled Pink City Central": [
                {"name": "Hawa Mahal Palace of Winds & Early Photography", "cat": "Architecture", "cost": 200, "dur": "1.5 hrs"},
                {"name": "City Palace Royal Museum & Chandra Mahal", "cat": "Culture & History", "cost": 700, "dur": "2.5 hrs"},
                {"name": "Laxmi Mishthan Bhandar (LMB) Heritage Thali", "cat": "Food & Dining", "cost": 850, "dur": "1.5 hrs"},
                {"name": "Johari Bazaar Handicraft & Blue Pottery Shopping", "cat": "Shopping & Culture", "cost": 600, "dur": "2.5 hrs"}
            ]
        }
    },
    {
        "name": "Bali",
        "country": "Indonesia",
        "vibes": ["Beach", "Nature", "Relaxation", "Adventure"],
        "budget_category": "Moderate",
        "avg_daily_budget_inr": 6000,
        "best_season": "April to October (Dry season with sunny skies & gentle winds)",
        "best_for": "Rice Terraces • Surf Beaches • Holistic Wellness",
        "highlight_tags": ["#TropicalParadise", "#RiceTerraces", "#Wellness", "#Surfing", "#Cafes"],
        "hero_image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80",
        "party_suitability": ["Couple", "Solo", "Friends", "Family"],
        "pace_match": ["Relaxed", "Moderate"],
        "clusters": {
            "Ubud Cultural Heartland": [
                {"name": "Tegallalang Sacred Rice Terraces & Jungle Swing", "cat": "Nature & Photography", "cost": 800, "dur": "2.5 hrs"},
                {"name": "Sacred Monkey Forest Sanctuary", "cat": "Nature & Wildlife", "cost": 500, "dur": "2.0 hrs"},
                {"name": "Clear Cafe Organic Farm-to-Table Lunch", "cat": "Food & Dining", "cost": 900, "dur": "1.5 hrs"},
                {"name": "Ubud Palace Traditional Legong Dance", "cat": "Culture & Entertainment", "cost": 600, "dur": "2.0 hrs"}
            ],
            "Uluwatu & Southern Cliffs": [
                {"name": "Padang Padang Beach Surf & Sun", "cat": "Beach & Adventure", "cost": 250, "dur": "3.0 hrs"},
                {"name": "Single Fin Clifftop Cafe Lunch", "cat": "Food & Dining", "cost": 1100, "dur": "1.5 hrs"},
                {"name": "Uluwatu Clifftop Temple & Kecak Fire Dance", "cat": "Culture & Sightseeing", "cost": 900, "dur": "2.5 hrs"},
                {"name": "Jimbaran Bay Candlelit Seafood Dinner on the Sand", "cat": "Food & Dining", "cost": 1700, "dur": "2.0 hrs"}
            ]
        }
    },
    {
        "name": "Paris",
        "country": "France",
        "vibes": ["Cultural", "Urban", "Relaxation"],
        "budget_category": "Luxury",
        "avg_daily_budget_inr": 15000,
        "best_season": "May to September (Warm café terraces & luminous late evenings)",
        "best_for": "World-Class Art • Haute Cuisine • Romantic Boulevards",
        "highlight_tags": ["#Romance", "#Louvre", "#HauteCuisine", "#ArtAndFashion", "#Architecture"],
        "hero_image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80",
        "party_suitability": ["Couple", "Solo", "Family", "Friends"],
        "pace_match": ["Moderate", "Relaxed"],
        "clusters": {
            "7th Arrondissement & Eiffel": [
                {"name": "Eiffel Tower Summit & Champ de Mars", "cat": "Architecture & Sightseeing", "cost": 2800, "dur": "3.0 hrs"},
                {"name": "Rue Cler Market Bistro Lunch", "cat": "Food & Dining", "cost": 2200, "dur": "1.5 hrs"},
                {"name": "Musée d'Orsay Impressionist Masterpieces", "cat": "Museums & Art", "cost": 1800, "dur": "2.5 hrs"},
                {"name": "Seine River Sunset Bateaux Mouches Cruise", "cat": "Leisure & Romance", "cost": 1600, "dur": "2.0 hrs"}
            ],
            "Montmartre & Le Marais": [
                {"name": "Sacre-Cœur Basilica & Artists' Place du Tertre", "cat": "Culture & Photography", "cost": 400, "dur": "2.5 hrs"},
                {"name": "Traditional Parisian Bakery Pastry Tour", "cat": "Food & Dining", "cost": 1200, "dur": "1.5 hrs"},
                {"name": "Le Marais Designer Boutiques & Place des Vosges", "cat": "Shopping & Architecture", "cost": 600, "dur": "2.5 hrs"},
                {"name": "Romantic Classic French Brasserie Dinner", "cat": "Dining & Nightlife", "cost": 3200, "dur": "2.5 hrs"}
            ]
        }
    },
    {
        "name": "Singapore",
        "country": "Singapore",
        "vibes": ["Urban", "Nature", "Cultural"],
        "budget_category": "Luxury",
        "avg_daily_budget_inr": 12000,
        "best_season": "Year-round (Equatorial lush garden city vibes)",
        "best_for": "Futuristic Architecture • Hawker Food • Clean Green Living",
        "highlight_tags": ["#GardenCity", "#HawkerFood", "#MarinaBay", "#FamilyFriendly", "#Modern"],
        "hero_image": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&q=80",
        "party_suitability": ["Family", "Couple", "Solo", "Friends"],
        "pace_match": ["Moderate", "Fast-Paced"],
        "clusters": {
            "Marina Bay & Downtown": [
                {"name": "Gardens by the Bay Flower Dome & Cloud Forest", "cat": "Nature & Architecture", "cost": 2200, "dur": "3.0 hrs"},
                {"name": "Lau Pa Sat Satay Street & Hawker Lunch", "cat": "Food & Dining", "cost": 900, "dur": "1.5 hrs"},
                {"name": "Marina Bay Sands SkyPark Observation Deck", "cat": "Sightseeing & Photography", "cost": 1900, "dur": "2.0 hrs"},
                {"name": "Spectra Light & Water Show by Marina Promenade", "cat": "Entertainment & Nightlife", "cost": 200, "dur": "2.0 hrs"}
            ],
            "Chinatown & Sentosa": [
                {"name": "Buddha Tooth Relic Temple & Chinatown Heritage Centre", "cat": "Culture & History", "cost": 350, "dur": "2.5 hrs"},
                {"name": "Maxwell Food Centre Hainanese Chicken Rice", "cat": "Food & Dining", "cost": 600, "dur": "1.0 hr"},
                {"name": "Sentosa Cable Car & Siloso Beach Leisure", "cat": "Adventure & Beach", "cost": 2100, "dur": "3.0 hrs"},
                {"name": "Clarke Quay Riverside Dining & Craft Cocktails", "cat": "Dining & Nightlife", "cost": 2500, "dur": "2.5 hrs"}
            ]
        }
    },
    {
        "name": "Mumbai",
        "country": "India",
        "vibes": ["Urban", "Cultural", "History"],
        "budget_category": "Moderate",
        "avg_daily_budget_inr": 4500,
        "best_season": "November to February (Pleasant maritime breeze)",
        "best_for": "Colonial Victorian Heritage • Bollywood • Coastal Street Food",
        "highlight_tags": ["#MaximumCity", "#MarineDrive", "#Colaba", "#StreetFood", "#Bollywood"],
        "hero_image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&q=80",
        "party_suitability": ["Friends", "Solo", "Couple", "Family"],
        "pace_match": ["Fast-Paced", "Moderate"],
        "clusters": {
            "South Mumbai & Colaba Heritage": [
                {"name": "Gateway of India & Iconic Taj Mahal Palace Hotel Walk", "cat": "Architecture & History", "cost": 200, "dur": "2.0 hrs"},
                {"name": "Cafe Mondegar / Leopold Cafe Irani & Parsi Brunch", "cat": "Food & Dining", "cost": 950, "dur": "1.5 hrs"},
                {"name": "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (CSMVS)", "cat": "Museums & History", "cost": 400, "dur": "2.5 hrs"},
                {"name": "Marine Drive 'Queen's Necklace' Sunset & Dinner at Chowpatty", "cat": "Leisure & Dining", "cost": 800, "dur": "2.5 hrs"}
            ],
            "Bandra & Coastal Suburbs": [
                {"name": "Bandra Bandstand & Mount Mary Church Heritage Walk", "cat": "Culture & Photography", "cost": 150, "dur": "2.0 hrs"},
                {"name": "Pali Hill Artisan Cafes & Street Art Tour", "cat": "Food & Shopping", "cost": 900, "dur": "2.0 hrs"},
                {"name": "Bandra Fort Seaside Sea Link Panorama", "cat": "Sightseeing", "cost": 50, "dur": "1.5 hrs"},
                {"name": "Bastian / Pali Village Cafe Coastal Dinner", "cat": "Dining & Nightlife", "cost": 2200, "dur": "2.5 hrs"}
            ]
        }
    },
    {
        "name": "Delhi",
        "country": "India",
        "vibes": ["Cultural", "History", "Urban"],
        "budget_category": "Budget",
        "avg_daily_budget_inr": 3500,
        "best_season": "October to March (Crisp winters with blooming Mughal gardens)",
        "best_for": "Mughal Architecture • Legendary Street Cuisine • Vibrant Bazaars",
        "highlight_tags": ["#CapitalHeritage", "#MughalMonuments", "#ChandniChowk", "#FoodieHeaven"],
        "hero_image": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80",
        "party_suitability": ["Family", "Solo", "Friends", "Couple"],
        "pace_match": ["Moderate", "Fast-Paced"],
        "clusters": {
            "Old Delhi Historic Core": [
                {"name": "Red Fort (Lal Qila) & Diwan-i-Khas Tour", "cat": "History & Architecture", "cost": 500, "dur": "2.5 hrs"},
                {"name": "Chandni Chowk Cycle Rickshaw & Paranthe Wali Gali", "cat": "Food & Culture", "cost": 650, "dur": "2.0 hrs"},
                {"name": "Jama Masjid & Khari Baoli Asia's Largest Spice Market", "cat": "Culture & Photography", "cost": 250, "dur": "2.0 hrs"},
                {"name": "Karim's / Al Jawahar Mughlai Feast", "cat": "Food & Dining", "cost": 1100, "dur": "1.5 hrs"}
            ],
            "New Delhi & Lutyens Splendor": [
                {"name": "Humayun's Tomb UNESCO Garden Heritage", "cat": "Architecture & Nature", "cost": 450, "dur": "2.0 hrs"},
                {"name": "Lodhi Art District Street Murals & Lodhi Garden Walk", "cat": "Art & Nature", "cost": 100, "dur": "2.0 hrs"},
                {"name": "Khan Market Bistro / Cafe Turtle Book Lunch", "cat": "Food & Dining", "cost": 1200, "dur": "1.5 hrs"},
                {"name": "Qutub Minar Complex Illuminated at Twilight", "cat": "History & Sightseeing", "cost": 500, "dur": "2.0 hrs"}
            ]
        }
    }
]

def score_destination(dest: Dict[str, Any], vibe: str, budget_tier: str, party: str, pace: str, interests: List[str]) -> float:
    score = 0.0
    
    # Vibe match
    if vibe in dest.get("vibes", []):
        score += 35.0
    
    # Budget match
    dest_budget = dest.get("budget_category", "").lower()
    if budget_tier.lower() == dest_budget:
        score += 25.0
    elif (budget_tier.lower() == "budget" and dest_budget == "moderate") or (budget_tier.lower() == "moderate" and dest_budget in ["budget", "luxury"]):
        score += 15.0
    else:
        score += 5.0
        
    # Party suitability
    if party in dest.get("party_suitability", []):
        score += 15.0
        
    # Pace match
    if pace in dest.get("pace_match", []):
        score += 10.0
        
    # Interest overlap
    tags_and_vibes = " ".join(dest.get("highlight_tags", []) + dest.get("vibes", []) + [dest.get("best_for", "")]).lower()
    for item in interests:
        if item.lower() in tags_and_vibes:
            score += 5.0
            
    # Add a tiny random jitter so recommendations don't feel static
    score += random.uniform(0.1, 1.5)
    return score

def get_demo_recommendations(vibe: str, budget_tier: str, party: str, pace: str, interests: List[str], top_n: int = 3) -> List[Dict[str, Any]]:
    """Returns top 3 scored destination recommendations with rich reasoning."""
    scored = []
    for d in DESTINATIONS_DB:
        s = score_destination(d, vibe, budget_tier, party, pace, interests)
        scored.append((s, d))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    top_picks = scored[:top_n]
    
    results = []
    for score_val, dest in top_picks:
        # Build explanation
        why_match = (
            f"Spectacular fit for a {vibe.lower()} escape with a {budget_tier.lower()} budget. "
            f"Tailored for {party.lower()} travelers seeking a {pace.lower()} rhythm, "
            f"offering world-class experiences in {', '.join(interests[:3]) if interests else 'sightseeing and culture'}."
        )
        results.append({
            "destination": dest["name"],
            "country": dest["country"],
            "why_it_matches": why_match,
            "best_for": dest["best_for"],
            "estimated_budget_category": dest["budget_category"],
            "avg_daily_budget_inr": dest["avg_daily_budget_inr"],
            "season_suitability": dest["best_season"],
            "highlight_tags": dest["highlight_tags"],
            "hero_image": dest["hero_image"]
        })
    return results

def get_destination_data(name: str) -> Dict[str, Any] | None:
    for d in DESTINATIONS_DB:
        if d["name"].lower() == name.lower():
            return d
    return None

