"""
Personalized Travel Itinerary Planner
Skill Wallet Capstone Project 4
A complete, polished, deployable Streamlit application for AI-driven and curated travel planning.
"""

import os
import datetime
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="Personalized Travel Itinerary Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import internal modules
from modules.utils import get_wanderlust_css, format_currency, USD_TO_INR
from modules.destinations import DESTINATIONS_DB, get_demo_recommendations
from modules.itinerary import build_demo_itinerary, recalculate_itinerary_costs
from modules.ai_engine import (
    generate_destination_recommendations,
    generate_itinerary,
    swap_activity_ai,
    regenerate_single_day_ai
)
from modules.storage import (
    load_all_trips,
    save_trip,
    delete_trip,
    rename_trip,
    duplicate_trip,
    export_trip_json,
    get_trip_by_id
)
from modules.pdf_export import generate_itinerary_pdf

# Inject Wanderlust Custom Styling
st.markdown(get_wanderlust_css(), unsafe_allow_html=True)

# ----------------- SESSION STATE INITIALIZATION -----------------

if "current_trip" not in st.session_state:
    # Initialize with default sample trip
    saved = load_all_trips()
    if saved:
        st.session_state.current_trip = saved[0]
    else:
        default_pref = {
            "destination": "Goa",
            "vibe": "Beach",
            "duration": 3,
            "start_date": str(datetime.date.today() + datetime.timedelta(days=14)),
            "end_date": str(datetime.date.today() + datetime.timedelta(days=17)),
            "budget_tier": "Moderate",
            "approx_budget": 25000,
            "travel_party": "Friends",
            "pace": "Moderate",
            "interests": ["Food", "Beach", "Nightlife", "History"],
            "dietary": "No preference",
            "notes": "Interested in coastal food and Portuguese colonial quarters"
        }
        init_itin = build_demo_itinerary(default_pref)
        st.session_state.current_trip = {
            "id": "trip_current_active",
            "title": "Sun & Culture Weekend in Goa",
            "created_at": datetime.datetime.now().isoformat(),
            "destination": "Goa",
            "country": "India",
            "preferences": default_pref,
            "itinerary": init_itin,
            "estimated_cost": init_itin.get("total_estimated_cost", 20550)
        }

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "currency_display" not in st.session_state:
    st.session_state.currency_display = "INR"

if "swap_feedback" not in st.session_state:
    st.session_state.swap_feedback = None

# ----------------- SIDEBAR CONFIGURATION -----------------

with st.sidebar:
    st.markdown("### 🧭 Travel Studio Controls")
    
    # 1. AI Provider Selection & Credentials
    st.markdown("#### 🤖 AI Engine Settings")
    ai_provider = st.selectbox("AI Provider", ["Gemini (Google)", "Groq (Llama 3.3)"], index=0)
    
    # Check secrets first
    secret_key = ""
    try:
        if "gemini" in ai_provider.lower():
            secret_key = st.secrets.get("GEMINI_API_KEY", "")
        else:
            secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        secret_key = ""

    api_key_input = st.text_input(
        "API Key (Optional in Demo Mode)",
        value=secret_key,
        type="password",
        help="Enter your Gemini or Groq API key. Leave blank to run entirely in Demo Mode."
    )
    
    # Demo Mode Switch
    demo_mode_default = not bool(api_key_input.strip())
    demo_mode = st.toggle("⚡ Demo Mode (Offline Curated Data)", value=demo_mode_default)
    
    if demo_mode:
        st.caption("🟢 Running in **Demo Mode**: Instant generation, zero API calls, full feature set enabled.")
    else:
        st.caption(f"🔵 Live Mode: Generating via **{ai_provider}**.")

    st.markdown("---")
    
    # Currency Switch
    st.markdown("#### 💱 Currency Display")
    curr_choice = st.radio("Display Currency", ["INR (₹)", "USD ($)"], horizontal=True)
    st.session_state.currency_display = "INR" if "INR" in curr_choice else "USD"
    if st.session_state.currency_display == "USD":
        st.caption(f"*Estimated rate: $1 ≈ ₹{USD_TO_INR} INR*")

    st.markdown("---")

    # 2. Trip Preferences Form
    st.markdown("#### 📋 Trip Preferences")
    
    curr_pref = st.session_state.current_trip.get("preferences", {})
    
    not_decided = st.checkbox("I haven't decided my destination yet", value=False)
    
    dest_options = [d["name"] for d in DESTINATIONS_DB]
    if not_decided:
        selected_dest = "Undecided"
        st.info("💡 Head to **Smart Destinations** tab for AI suggestions!")
    else:
        custom_or_preset = st.radio("Destination Mode", ["Popular Destination", "Custom City/Region"], horizontal=True)
        if custom_or_preset == "Popular Destination":
            default_dest_idx = dest_options.index(curr_pref.get("destination", "Goa")) if curr_pref.get("destination", "Goa") in dest_options else 0
            selected_dest = st.selectbox("Select Destination", dest_options, index=default_dest_idx)
        else:
            selected_dest = st.text_input("Enter Destination", value=curr_pref.get("destination", "Kyoto"))

    vibe_list = ["Beach", "Mountains", "Cultural", "Urban", "Nature", "Adventure", "Relaxation"]
    default_vibe_idx = vibe_list.index(curr_pref.get("vibe", "Beach")) if curr_pref.get("vibe", "Beach") in vibe_list else 0
    selected_vibe = st.selectbox("Open-Ended Travel Vibe", vibe_list, index=default_vibe_idx)

    trip_duration = st.slider("Trip Duration (Days)", min_value=1, max_value=14, value=int(curr_pref.get("duration", 3)))

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("Start Date", value=datetime.date.today() + datetime.timedelta(days=7))
    with col_d2:
        end_date = st.date_input("End Date", value=datetime.date.today() + datetime.timedelta(days=7 + trip_duration))

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        budget_tier = st.selectbox("Budget Tier", ["Budget", "Moderate", "Luxury"], index=1)
    with col_b2:
        party = st.selectbox("Travel Party", ["Solo", "Couple", "Family", "Friends"], index=1)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pace = st.selectbox("Pace", ["Relaxed", "Moderate", "Fast-Paced"], index=1)
    with col_p2:
        dietary = st.selectbox("Dietary Preference", ["No preference", "Vegetarian", "Vegan", "Other"], index=0)

    interest_options = ["Food", "Adventure", "History", "Culture", "Nature", "Shopping", "Nightlife", "Photography", "Architecture", "Museums"]
    default_interests = [i for i in curr_pref.get("interests", ["Food", "Culture"]) if i in interest_options]
    selected_interests = st.multiselect("Key Interests", interest_options, default=default_interests or ["Food", "Culture"])

    additional_notes = st.text_area("Additional Preferences / Special Requests", value=curr_pref.get("notes", ""), placeholder="e.g. Prefer sea-facing cafes, avoid steep stairs, interested in local craft markets...")

    # Form Submission Actions
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        generate_itin_clicked = st.button("🚀 Build Itinerary", use_container_width=True, type="primary")
    with col_btn2:
        explore_dest_clicked = st.button("✨ Recommend Dest", use_container_width=True)

    st.markdown("---")
    st.caption("Skill Wallet Capstone Project 4 • Personalized Travel Planner")

# ----------------- ACTION HANDLERS -----------------

# Package current user preferences
active_preferences = {
    "destination": selected_dest if not not_decided else "Undecided",
    "vibe": selected_vibe,
    "duration": trip_duration,
    "start_date": str(start_date),
    "end_date": str(end_date),
    "budget_tier": budget_tier,
    "approx_budget": 30000 if budget_tier == "Moderate" else (15000 if budget_tier == "Budget" else 80000),
    "travel_party": party,
    "pace": pace,
    "interests": selected_interests,
    "dietary": dietary,
    "notes": additional_notes
}

# 1. Action: Recommend Destinations
if explore_dest_clicked or (not_decided and not st.session_state.recommendations):
    with st.spinner("Analyzing vibes, budget, season, and interests to pick top destinations..."):
        recs, rec_err = generate_destination_recommendations(
            active_preferences,
            provider=ai_provider,
            api_key=api_key_input,
            is_demo=demo_mode
        )
        st.session_state.recommendations = recs
        if rec_err:
            st.warning(rec_err)
        st.success("Destination recommendations ready in Tab 1!")

# 2. Action: Generate Full Itinerary
if generate_itin_clicked:
    target_dest = selected_dest if not not_decided else "Goa"
    if not_decided:
        st.info("No destination selected. Defaulting to Goa for demonstration.")
        active_preferences["destination"] = "Goa"
        
    with st.spinner(f"Crafting geographically clustered {trip_duration}-day itinerary for {target_dest}..."):
        itin_result, itin_err = generate_itinerary(
            active_preferences,
            provider=ai_provider,
            api_key=api_key_input,
            is_demo=demo_mode
        )
        
        # Save into active session
        st.session_state.current_trip = {
            "id": f"trip_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": f"{active_preferences['vibe']} Escape in {target_dest}",
            "created_at": datetime.datetime.now().isoformat(),
            "destination": target_dest,
            "country": itin_result.get("country", "Global"),
            "preferences": active_preferences,
            "itinerary": itin_result,
            "estimated_cost": itin_result.get("total_estimated_cost", 0)
        }
        
        if itin_err:
            st.warning(itin_err)
        st.success(f"Itinerary for {target_dest} created successfully!")

# ----------------- MAIN UI HEADER -----------------

st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">Personalized Travel Itinerary Planner</h1>
    <p class="hero-tagline">AI-Powered Travel Architecture • Geographic Clustering • Tailored Vibe Customization</p>
    <div class="hero-badges">
        <span class="hero-badge">📍 Smart Neighborhood Clustering</span>
        <span class="hero-badge">💰 Transparent Cost Tracking</span>
        <span class="hero-badge">🔄 One-Click Activity Swaps</span>
        <span class="hero-badge">📄 Publication-Quality PDF Dossier</span>
        <span class="hero-badge">⚡ 100% Offline Demo Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- TABS NAVIGATION -----------------

tab_recommender, tab_itinerary, tab_customization, tab_trips = st.tabs([
    "🧭 Smart Destinations",
    "📅 Day-by-Day Itinerary",
    "🔄 Vibe Customization & Swap",
    "🗂️ Trip Management & PDF"
])

# =========================================================================
# TAB 1: SMART DESTINATION RECOMMENDER
# =========================================================================
with tab_recommender:
    st.markdown("### 🧭 Smart Destination Recommender")
    st.markdown(
        "Unsure where to wander? Our recommender matches your **mood, party style, budget tier, and season** "
        "to suggest top handpicked destinations."
    )
    
    col_rec_top1, col_rec_top2 = st.columns([3, 1])
    with col_rec_top1:
        st.info(f"Current Vibe: **{selected_vibe}** | Budget: **{budget_tier}** | Party: **{party}** | Pace: **{pace}**")
    with col_rec_top2:
        if st.button("🔄 Refresh Recommendations", use_container_width=True):
            with st.spinner("Generating fresh suggestions..."):
                recs, err = generate_destination_recommendations(
                    active_preferences,
                    provider=ai_provider,
                    api_key=api_key_input,
                    is_demo=demo_mode
                )
                st.session_state.recommendations = recs
                st.rerun()

    # If no recommendations yet, load default demo picks
    if not st.session_state.recommendations:
        st.session_state.recommendations = get_demo_recommendations(selected_vibe, budget_tier, party, pace, selected_interests)

    # Display 3 Cards
    rec_cols = st.columns(len(st.session_state.recommendations))
    for idx, rec in enumerate(st.session_state.recommendations):
        with rec_cols[idx]:
            img_url = rec.get("hero_image") or "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80"
            dest_name = rec.get("destination", "Destination")
            country_name = rec.get("country", "")
            why_match = rec.get("why_it_matches", "")
            best_for = rec.get("best_for", "")
            budget_cat = rec.get("estimated_budget_category", budget_tier)
            season = rec.get("season_suitability", "")
            tags = rec.get("highlight_tags", [])
            avg_budget = rec.get("avg_daily_budget_inr", 5000)

            st.markdown(f"""
            <div class="destination-card">
                <img src="{img_url}" class="destination-image" alt="{dest_name}">
                <div class="destination-body">
                    <div class="destination-title">{dest_name}, {country_name}</div>
                    <p style="font-size:0.85rem; color:#E06A3B; font-weight:700; margin-bottom:8px;">
                        ✨ {best_for}
                    </p>
                    <p style="font-size:0.88rem; color:#4F5D75; line-height:1.45; margin-bottom:12px;">
                        {why_match}
                    </p>
                    <div style="font-size:0.82rem; margin-bottom:6px;">
                        <b>Budget:</b> <span style="color:#059669; font-weight:600;">{budget_cat}</span> (~{format_currency(avg_budget, st.session_state.currency_display)} / day)
                    </div>
                    <div style="font-size:0.82rem; margin-bottom:12px; color:#7D8597;">
                        <b>Best Season:</b> {season}
                    </div>
                    <div style="margin-top:auto; margin-bottom:14px;">
                        {" ".join([f'<span class="tag-chip">{t}</span>' for t in tags[:4]])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🎯 Select & Plan {dest_name}", key=f"btn_pick_dest_{idx}", use_container_width=True, type="primary"):
                # Update preferences
                active_preferences["destination"] = dest_name
                with st.spinner(f"Synthesizing customized itinerary for {dest_name}..."):
                    new_itin, err = generate_itinerary(
                        active_preferences,
                        provider=ai_provider,
                        api_key=api_key_input,
                        is_demo=demo_mode
                    )
                    st.session_state.current_trip = {
                        "id": f"trip_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "title": f"{active_preferences['vibe']} Trip to {dest_name}",
                        "created_at": datetime.datetime.now().isoformat(),
                        "destination": dest_name,
                        "country": country_name,
                        "preferences": active_preferences,
                        "itinerary": new_itin,
                        "estimated_cost": new_itin.get("total_estimated_cost", 0)
                    }
                    st.success(f"{dest_name} selected! Switched to your customized itinerary.")
                    st.rerun()

# =========================================================================
# TAB 2: DAY-BY-DAY ITINERARY GENERATOR
# =========================================================================
with tab_itinerary:
    current_trip = st.session_state.current_trip
    itin_data = current_trip.get("itinerary", {})
    dest = current_trip.get("destination", "Goa")
    trip_title = current_trip.get("title", f"Trip to {dest}")
    days = itin_data.get("days", [])
    cost_summary = itin_data.get("cost_summary", {})
    curr_code = st.session_state.currency_display

    # Top Overview Bar
    st.markdown(f"### 📍 {trip_title}")
    
    # Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Destination</div>
            <div class="metric-value" style="font-size:1.25rem;">{dest}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Duration</div>
            <div class="metric-value">{len(days)} Days</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        trip_cost_val = cost_summary.get("trip_total_inr", current_trip.get("estimated_cost", 0))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Estimated Total</div>
            <div class="metric-value">{format_currency(trip_cost_val, curr_code)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        vibe_badge = current_trip.get("preferences", {}).get("vibe", "Relaxed")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Travel Style</div>
            <div class="metric-value" style="font-size:1.25rem;">{vibe_badge}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Geographic Clustering Notice
    st.info("🗺️ **Geographic Clustering Active:** Each day groups attractions within the same neighborhood or district to eliminate backtracking and reduce travel fatigue.")

    # Render Day-by-Day Accordion / Cards
    for day in days:
        d_num = day.get("day", 1)
        theme = day.get("theme", "Day Exploration")
        area = day.get("area", "District Cluster")
        d_cost = day.get("daily_cost", {})

        with st.expander(f"🗓️ Day {d_num}: {theme}  •  📍 {area}", expanded=(d_num == 1)):
            st.markdown(f"""
            <div class="day-header">
                <div class="day-header-title">Day {d_num}: {theme}</div>
                <div class="day-header-subtitle">📍 Geographic Focus: <b>{area}</b> | Minimizes cross-city travel</div>
            </div>
            """, unsafe_allow_html=True)

            slot_col1, slot_col2 = st.columns(2)
            
            # Morning Slot
            with slot_col1:
                m = day.get("morning", {})
                st.markdown(f"""
                <div class="travel-card">
                    <span class="slot-pill slot-morning">🌅 Morning • {m.get('time', '09:00 - 11:30')}</span>
                    <h4 style="margin:4px 0 8px 0; color:#2D3142;">{m.get('name', 'Morning Exploration')}</h4>
                    <p style="font-size:0.9rem; color:#4F5D75; margin-bottom:12px;">{m.get('description', '')}</p>
                    <div style="font-size:0.82rem; color:#7D8597; border-top:1px dashed #E5E7EB; padding-top:8px;">
                        <span>📍 <b>Location:</b> {m.get('location', area)}</span><br/>
                        <span>⏱️ <b>Duration:</b> {m.get('duration', '2.5 hrs')}</span> • 
                        <span>💰 <b>Cost:</b> {format_currency(m.get('cost_inr', 0), curr_code)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Lunch Slot
            with slot_col2:
                l = day.get("lunch", {})
                st.markdown(f"""
                <div class="travel-card">
                    <span class="slot-pill slot-lunch">🍴 Lunch • {l.get('time', '12:30 - 14:00')}</span>
                    <h4 style="margin:4px 0 8px 0; color:#2D3142;">{l.get('name', 'Local Lunch')}</h4>
                    <p style="font-size:0.9rem; color:#4F5D75; margin-bottom:12px;">{l.get('description', '')}</p>
                    <div style="font-size:0.82rem; color:#7D8597; border-top:1px dashed #E5E7EB; padding-top:8px;">
                        <span>📍 <b>Location:</b> {l.get('location', area)}</span><br/>
                        <span>⏱️ <b>Duration:</b> {l.get('duration', '1.5 hrs')}</span> • 
                        <span>💰 <b>Cost:</b> {format_currency(l.get('cost_inr', 0), curr_code)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            slot_col3, slot_col4 = st.columns(2)

            # Afternoon Slot
            with slot_col3:
                a = day.get("afternoon", {})
                st.markdown(f"""
                <div class="travel-card">
                    <span class="slot-pill slot-afternoon">☀️ Afternoon • {a.get('time', '14:30 - 17:00')}</span>
                    <h4 style="margin:4px 0 8px 0; color:#2D3142;">{a.get('name', 'Afternoon Sightseeing')}</h4>
                    <p style="font-size:0.9rem; color:#4F5D75; margin-bottom:12px;">{a.get('description', '')}</p>
                    <div style="font-size:0.82rem; color:#7D8597; border-top:1px dashed #E5E7EB; padding-top:8px;">
                        <span>📍 <b>Location:</b> {a.get('location', area)}</span><br/>
                        <span>⏱️ <b>Duration:</b> {a.get('duration', '2.5 hrs')}</span> • 
                        <span>💰 <b>Cost:</b> {format_currency(a.get('cost_inr', 0), curr_code)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Evening Slot
            with slot_col4:
                e = day.get("evening", {})
                st.markdown(f"""
                <div class="travel-card">
                    <span class="slot-pill slot-evening">🌙 Evening • {e.get('time', '18:00 - 21:00')}</span>
                    <h4 style="margin:4px 0 8px 0; color:#2D3142;">{e.get('name', 'Evening Dining / Sunset')}</h4>
                    <p style="font-size:0.9rem; color:#4F5D75; margin-bottom:12px;">{e.get('description', '')}</p>
                    <div style="font-size:0.82rem; color:#7D8597; border-top:1px dashed #E5E7EB; padding-top:8px;">
                        <span>📍 <b>Location:</b> {e.get('location', area)}</span><br/>
                        <span>⏱️ <b>Duration:</b> {e.get('duration', '3.0 hrs')}</span> • 
                        <span>💰 <b>Cost:</b> {format_currency(e.get('cost_inr', 0), curr_code)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Day Cost Summary Bar & Regenerate Button
            day_act = d_cost.get("activities", 0)
            day_food = d_cost.get("food", 0)
            day_trans = d_cost.get("transport", 0)
            day_tot = d_cost.get("total", 0)

            c_cost1, c_cost2 = st.columns([3, 1])
            with c_cost1:
                st.markdown(
                    f"💵 **Day {d_num} Estimated Breakdown:** "
                    f"Activities: `{format_currency(day_act, curr_code)}` | "
                    f"Food: `{format_currency(day_food, curr_code)}` | "
                    f"Transport: `{format_currency(day_trans, curr_code)}` | "
                    f"**Total: `{format_currency(day_tot, curr_code)}`**"
                )
            with c_cost2:
                if st.button(f"🔄 Regenerate Day {d_num}", key=f"btn_regen_day_{d_num}", use_container_width=True):
                    with st.spinner(f"Rebuilding Day {d_num} with a fresh neighborhood cluster..."):
                        other_areas = [d.get("area", "") for d in days if d.get("day") != d_num]
                        new_day_obj, r_err = regenerate_single_day_ai(
                            dest,
                            d_num,
                            current_trip.get("preferences", {}),
                            other_areas,
                            provider=ai_provider,
                            api_key=api_key_input,
                            is_demo=demo_mode
                        )
                        # Replace in place
                        for idx_d, old_d in enumerate(days):
                            if old_d.get("day") == d_num:
                                days[idx_d] = new_day_obj
                                break
                        recalculate_itinerary_costs(itin_data, current_trip.get("preferences", {}).get("budget_tier", "Moderate"))
                        st.session_state.current_trip["estimated_cost"] = itin_data["total_estimated_cost"]
                        st.success(f"Day {d_num} refreshed!")
                        st.rerun()

    # Total Itinerary Financial Summary Table
    st.markdown("---")
    st.markdown("### 📊 Comprehensive Trip Cost Tracking")
    st.caption("Estimated costs are derived from local norms, dining choices, and planned activities. Transparent and editable.")

    sum_col1, sum_col2, sum_col3, sum_col4, sum_col5 = st.columns(5)
    with sum_col1:
        st.metric("Total Activities", format_currency(cost_summary.get("activities_total", 0), curr_code))
    with sum_col2:
        st.metric("Total Dining & Food", format_currency(cost_summary.get("food_total", 0), curr_code))
    with sum_col3:
        st.metric("City Transit", format_currency(cost_summary.get("transport_total", 0), curr_code))
    with sum_col4:
        st.metric("Est. Lodging", format_currency(cost_summary.get("accommodation_estimated", 0), curr_code))
    with sum_col5:
        st.metric("TOTAL TRIP (INR & USD)", f"{format_currency(cost_summary.get('trip_total_inr', 0), 'INR')} (~{format_currency(cost_summary.get('trip_total_usd', 0), 'USD')})")

    # Quick Action Buttons
    st.markdown("---")
    act_col1, act_col2, act_col3 = st.columns(3)
    with act_col1:
        if st.button("💾 Save Trip to Wallet", use_container_width=True, type="primary"):
            saved_item = save_trip(
                title=current_trip.get("title", f"Trip to {dest}"),
                destination=dest,
                country=current_trip.get("country", "Global"),
                preferences=current_trip.get("preferences", {}),
                itinerary=current_trip.get("itinerary", {}),
                estimated_cost=current_trip.get("estimated_cost", 0),
                trip_id=current_trip.get("id")
            )
            st.success(f"Trip '{saved_item['title']}' persisted to local wallet!")
    with act_col2:
        # Instant PDF Download
        try:
            pdf_buf = generate_itinerary_pdf(current_trip)
            st.download_button(
                label="📄 Download PDF Dossier",
                data=pdf_buf,
                file_name=f"Itinerary_{dest}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF creation error: {e}")
    with act_col3:
        # Export as JSON
        json_data = export_trip_json(current_trip)
        st.download_button(
            label="📦 Export Trip JSON",
            data=json_data,
            file_name=f"trip_{dest.lower()}_{datetime.date.today()}.json",
            mime="application/json",
            use_container_width=True
        )

# =========================================================================
# TAB 3: VIBE CUSTOMIZATION & ACTIVITY SWAP
# =========================================================================
with tab_customization:
    st.markdown("### 🔄 Vibe Customization & Granular Activity Swapping")
    st.markdown(
        "Want to change a single activity without blowing up your entire day? "
        "Select any time slot, type your desire, and swap only that activity. "
        "**The rest of your itinerary and geographic proximity remain strictly preserved.**"
    )

    current_trip = st.session_state.current_trip
    itin_data = current_trip.get("itinerary", {})
    days = itin_data.get("days", [])
    dest = current_trip.get("destination", "Goa")

    if not days:
        st.warning("No active itinerary found. Please generate an itinerary first!")
    else:
        col_swap_pick1, col_swap_pick2 = st.columns(2)
        with col_swap_pick1:
            day_choices = [d.get("day", i+1) for i, d in enumerate(days)]
            target_day_num = st.selectbox("Select Day to Modify", day_choices, index=0)
        with col_swap_pick2:
            target_slot = st.selectbox("Select Time Slot", ["Morning", "Lunch", "Afternoon", "Evening"], index=1)

        # Locate selected day and slot activity
        selected_day_obj = next((d for d in days if d.get("day") == target_day_num), days[0])
        slot_key = target_slot.lower()
        current_act = selected_day_obj.get(slot_key, {})
        current_area = selected_day_obj.get("area", dest)

        # Display Current Activity Card
        st.markdown(f"#### 📌 Currently Scheduled {target_slot} Activity (Day {target_day_num} • {current_area})")
        st.markdown(f"""
        <div class="travel-card" style="border-left:5px solid #2563EB;">
            <h4 style="margin:0 0 6px 0; color:#2D3142;">{current_act.get('name', 'Current Activity')}</h4>
            <p style="font-size:0.92rem; color:#4F5D75; margin-bottom:10px;">{current_act.get('description', '')}</p>
            <div style="font-size:0.84rem; color:#7D8597;">
                📍 <b>Location:</b> {current_act.get('location', current_area)} | 
                ⏱️ <b>Time:</b> {current_act.get('time', 'N/A')} ({current_act.get('duration', 'N/A')}) | 
                💰 <b>Cost:</b> {format_currency(current_act.get('cost_inr', 0), st.session_state.currency_display)} |
                🏷️ <b>Category:</b> {current_act.get('category', 'Activity')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Suggested swap prompts
        st.markdown("#### 💬 What would you like instead?")
        quick_swap_options = [
            "Find a vegetarian/vegan culinary alternative",
            "Swap for a vibrant local outdoor artisan market",
            "Make this activity more adventurous and active",
            "Find a cheaper or budget-friendly alternative",
            "Make this slot more relaxed and serene (wellness/cafe)"
        ]
        chosen_quick_prompt = st.selectbox("💡 Quick Ideas", ["Choose a preset idea..." ] + quick_swap_options)
        
        custom_prompt_input = st.text_input(
            "Or enter your exact requirement:",
            value=chosen_quick_prompt if chosen_quick_prompt != "Choose a preset idea..." else "",
            placeholder="e.g. Find an authentic vegetarian thali spot near Fontainhas with outdoor seating"
        )

        btn_swap_col1, btn_swap_col2 = st.columns([1, 2])
        with btn_swap_col1:
            execute_swap = st.button("✨ Swap This Activity", use_container_width=True, type="primary")

        if execute_swap:
            if not custom_prompt_input.strip():
                st.error("Please provide a prompt or select a quick idea to swap.")
            else:
                with st.spinner(f"Finding perfect replacement for {target_slot} in {current_area}..."):
                    replacement_act, swap_err = swap_activity_ai(
                        destination=dest,
                        day_num=target_day_num,
                        area=current_area,
                        slot_name=target_slot,
                        current_activity=current_act,
                        user_request=custom_prompt_input,
                        dietary=current_trip.get("preferences", {}).get("dietary", "No preference"),
                        budget_tier=current_trip.get("preferences", {}).get("budget_tier", "Moderate"),
                        provider=ai_provider,
                        api_key=api_key_input,
                        is_demo=demo_mode
                    )

                    # Update only this slot
                    selected_day_obj[slot_key] = replacement_act
                    recalculate_itinerary_costs(itin_data, current_trip.get("preferences", {}).get("budget_tier", "Moderate"))
                    st.session_state.current_trip["estimated_cost"] = itin_data["total_estimated_cost"]
                    st.session_state.swap_feedback = {
                        "day": target_day_num,
                        "slot": target_slot,
                        "old": current_act.get("name"),
                        "new": replacement_act.get("name")
                    }
                    st.success(f"Swapped '{current_act.get('name')}' ➔ '{replacement_act.get('name')}'!")
                    st.rerun()

        # Display swap feedback if present
        if st.session_state.swap_feedback:
            fb = st.session_state.swap_feedback
            st.info(f"✅ Recently swapped on Day {fb['day']} ({fb['slot']}): **{fb['old']}** was replaced with **{fb['new']}**. All other days and slots are unchanged.")

        # Full Day Custom Regeneration
        st.markdown("---")
        st.markdown(f"#### 🌅 Complete Regeneration for Day {target_day_num}")
        st.caption("Re-clusters this specific day around a new theme while keeping all other days intact.")
        
        if st.button(f"🔄 Regenerate All Activities for Day {target_day_num}", use_container_width=False):
            with st.spinner(f"Synthesizing fresh day plan for Day {target_day_num}..."):
                other_areas = [d.get("area", "") for d in days if d.get("day") != target_day_num]
                new_day_obj, r_err = regenerate_single_day_ai(
                    dest,
                    target_day_num,
                    current_trip.get("preferences", {}),
                    other_areas,
                    provider=ai_provider,
                    api_key=api_key_input,
                    is_demo=demo_mode
                )
                for idx_d, old_d in enumerate(days):
                    if old_d.get("day") == target_day_num:
                        days[idx_d] = new_day_obj
                        break
                recalculate_itinerary_costs(itin_data, current_trip.get("preferences", {}).get("budget_tier", "Moderate"))
                st.session_state.current_trip["estimated_cost"] = itin_data["total_estimated_cost"]
                st.success(f"Day {target_day_num} successfully regenerated with fresh activities!")
                st.rerun()

# =========================================================================
# TAB 4: TRIP MANAGEMENT & PDF
# =========================================================================
with tab_trips:
    st.markdown("### 🗂️ Trip Management & Saved Dossiers")
    st.markdown("Manage your local trips, load previous itineraries, duplicate plans, and generate downloadable travel PDFs.")

    saved_trips = load_all_trips()

    col_tm1, col_tm2 = st.columns([2, 1])
    with col_tm1:
        st.markdown(f"**Saved Trips in Wallet:** `{len(saved_trips)}`")
    with col_tm2:
        if st.button("➕ Save Current Trip as New", use_container_width=True):
            current = st.session_state.current_trip
            saved_item = save_trip(
                title=f"{current.get('title', 'Trip')} (Saved {datetime.datetime.now().strftime('%b %d')})",
                destination=current.get("destination", "Goa"),
                country=current.get("country", "Global"),
                preferences=current.get("preferences", {}),
                itinerary=current.get("itinerary", {}),
                estimated_cost=current.get("estimated_cost", 0)
            )
            st.success(f"Saved '{saved_item['title']}'!")
            st.rerun()

    if not saved_trips:
        st.info("No trips saved yet. Generate an itinerary and click 'Save Trip to Wallet'!")
    else:
        st.markdown("<br/>", unsafe_allow_html=True)
        for t in saved_trips:
            t_id = t.get("id", "")
            t_title = t.get("title", "Untitled Trip")
            t_dest = t.get("destination", "Destination")
            t_cost = t.get("estimated_cost", 0)
            t_date = t.get("created_at", "")[:10]
            t_days = len(t.get("itinerary", {}).get("days", []))

            with st.container():
                st.markdown(f"""
                <div class="travel-card" style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:#2D3142;">{t_title}</h4>
                            <p style="font-size:0.85rem; color:#7D8597; margin:3px 0 0 0;">
                                📍 <b>{t_dest}</b> • {t_days} Days • Est: {format_currency(t_cost, st.session_state.currency_display)} • Created: {t_date}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                act_row1, act_row2, act_row3, act_row4, act_row5 = st.columns([1.2, 1.2, 1.2, 1.5, 1])
                
                with act_row1:
                    if st.button("📂 Load Trip", key=f"load_{t_id}", use_container_width=True):
                        st.session_state.current_trip = t
                        st.success(f"Loaded '{t_title}' into active session!")
                        st.rerun()

                with act_row2:
                    if st.button("📑 Duplicate", key=f"dup_{t_id}", use_container_width=True):
                        duplicate_trip(t_id)
                        st.success("Trip duplicated!")
                        st.rerun()

                with act_row3:
                    try:
                        t_pdf = generate_itinerary_pdf(t)
                        st.download_button(
                            label="📄 PDF",
                            data=t_pdf,
                            file_name=f"{t_title.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{t_id}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.caption("PDF Error")

                with act_row4:
                    new_name_val = st.text_input(f"Rename", value=t_title, key=f"ren_input_{t_id}", label_visibility="collapsed")
                    if new_name_val != t_title and st.button("Save Name", key=f"ren_btn_{t_id}"):
                        rename_trip(t_id, new_name_val)
                        st.success("Renamed!")
                        st.rerun()

                with act_row5:
                    if st.button("🗑️ Delete", key=f"del_{t_id}", use_container_width=True):
                        delete_trip(t_id)
                        st.warning("Trip deleted.")
                        st.rerun()

    # Streamlit Cloud Persistence Note
    st.markdown("---")
    st.caption(
        "🔒 **Local Persistence Model:** Trips are stored locally in `data/trips.json` and mirrored in Streamlit Session State. "
        "On ephemeral Streamlit Community Cloud instances, session state protects during user interaction, while local JSON provides demo persistence."
    )

