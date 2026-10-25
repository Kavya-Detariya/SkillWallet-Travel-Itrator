"""
Utility functions: Currency conversion, JSON cleanup, date helpers, and Wanderlust CSS.
"""

import re
import json
from typing import Dict, Any, Optional

USD_TO_INR = 83.5
EUR_TO_INR = 90.5

def format_currency(amount_inr: float, currency: str = "INR") -> str:
    """Format an INR amount into INR or USD or EUR with appropriate symbols."""
    try:
        val = float(amount_inr)
    except (ValueError, TypeError):
        val = 0.0

    if currency.upper() == "USD":
        usd_val = val / USD_TO_INR
        return f"${usd_val:,.2f}"
    elif currency.upper() == "EUR":
        eur_val = val / EUR_TO_INR
        return f"€{eur_val:,.2f}"
    else:
        return f"₹{val:,.0f}"

def extract_json_from_text(text: str) -> Optional[Any]:
    """
    Robustly extract JSON from AI response that might contain markdown fences,
    prose, or minor formatting irregularities.
    """
    if not text:
        return None
        
    text = text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
        
    # Check for ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        raw_inside = match.group(1).strip()
        try:
            return json.loads(raw_inside)
        except Exception:
            pass
            
    # Try finding the first '{' or '[' and last '}' or ']'
    first_brace = text.find('{')
    first_bracket = text.find('[')
    
    start_idx = -1
    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        start_idx = first_brace
        end_idx = text.rfind('}')
    elif first_bracket != -1:
        start_idx = first_bracket
        end_idx = text.rfind(']')
    else:
        return None
        
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        candidate = text[start_idx:end_idx + 1]
        try:
            return json.loads(candidate)
        except Exception:
            # Try cleaning trailing commas
            cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(cleaned)
            except Exception:
                pass
                
    return None

def get_wanderlust_css() -> str:
    """Return polished custom CSS styling for the Wanderlust Travel Planner UI."""
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(224, 106, 59, 0.92) 0%, rgba(45, 49, 66, 0.95) 100%),
                    url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600&q=80') center/cover no-repeat;
        border-radius: 20px;
        padding: 40px 35px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0 0 10px 0;
        color: #FFFFFF;
        text-shadow: 0 2px 4px rgba(0,0,0,0.25);
    }

    .hero-tagline {
        font-size: 1.15rem;
        color: #F8F9FA;
        margin: 0 0 18px 0;
        font-weight: 400;
        opacity: 0.95;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .hero-badge {
        background: rgba(255, 255, 255, 0.22);
        backdrop-filter: blur(8px);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }

    /* Cards */
    .travel-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #EAE6DF;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(45, 49, 66, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .travel-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(45, 49, 66, 0.08);
    }

    .destination-card {
        background: #FFFFFF;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #EAE6DF;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .destination-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }

    .destination-body {
        padding: 20px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }

    .destination-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #2D3142;
        margin-bottom: 6px;
    }

    /* Metric Box */
    .metric-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #EAE6DF;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }

    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #7D8597;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #E06A3B;
    }

    /* Activity Slot Pill */
    .slot-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .slot-morning {
        background: #FFF4E5;
        color: #D97706;
        border: 1px solid #FCD34D;
    }

    .slot-lunch {
        background: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }

    .slot-afternoon {
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #BFDBFE;
    }

    .slot-evening {
        background: #F5F3FF;
        color: #7C3AED;
        border: 1px solid #DDD6FE;
    }

    .tag-chip {
        display: inline-block;
        background: #F3EFE6;
        color: #4F5D75;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Streamlit Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 8px;
        border-bottom: 2px solid #EAE6DF;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 10px;
        color: #4F5D75;
    }

    .stTabs [aria-selected="true"] {
        background-color: #E06A3B !important;
        color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    /* Day Accordion / Header */
    .day-header {
        background: linear-gradient(90deg, #FDFBF7 0%, #F5EFEB 100%);
        border-left: 5px solid #E06A3B;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin: 20px 0 15px 0;
    }

    .day-header-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #2D3142;
        margin: 0;
    }

    .day-header-subtitle {
        font-size: 0.88rem;
        color: #7D8597;
        margin-top: 3px;
    }
    </style>
    """

