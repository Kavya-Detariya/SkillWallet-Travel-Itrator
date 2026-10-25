"""
PDF Generation module using ReportLab for Wanderlust Travel Itinerary Planner.
Generates an elegant, publication-quality travel dossier with Cover, Summary,
Day-by-Day Details, Budget Breakdown, and Emergency Travel Checklist.
"""

import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from modules.utils import format_currency

def generate_itinerary_pdf(trip_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generate a styled PDF document from itinerary and preferences.
    Returns in-memory BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Palettes
    PRIMARY_COLOR = colors.HexColor("#E06A3B")    # Warm Terracotta
    DARK_TEXT = colors.HexColor("#2D3142")        # Slate Charcoal
    MUTED_TEXT = colors.HexColor("#6B7280")       # Cool Grey
    LIGHT_BG = colors.HexColor("#FDFBF7")         # Soft Warm Cream
    ACCENT_BG = colors.HexColor("#F3EFE6")        # Light Neutral Warm
    BORDER_COLOR = colors.HexColor("#E5E7EB")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY_COLOR,
        alignment=0, # Left
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=MUTED_TEXT,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=DARK_TEXT,
        spaceBefore=14,
        spaceAfter=8
    )

    day_banner_style = ParagraphStyle(
        'DayBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.white
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=MUTED_TEXT
    )

    story = []

    destination = trip_data.get("destination", "Explore Destination")
    country = trip_data.get("country", "")
    full_dest = f"{destination}, {country}" if country and country != "Global" else destination
    preferences = trip_data.get("preferences", {})
    itinerary = trip_data.get("itinerary", {})
    days = itinerary.get("days", [])
    cost_summary = itinerary.get("cost_summary", {})
    duration = preferences.get("duration", len(days) or 1)

    # 1. HEADER / COVER BANNER
    header_data = [
        [
            Paragraph("PERSONALIZED TRAVEL ITINERARY", meta_style),
            Paragraph(f"Duration: {duration} Days", meta_style)
        ],
        [
            Paragraph(f"<b>{full_dest}</b>", title_style),
            Paragraph(f"<b>Style:</b> {preferences.get('vibe', 'Custom')}", body_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.2 * inch, 3.2 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=4, spaceAfter=14))

    # 2. TRIP SUMMARY BOX
    summary_cells = [
        [
            Paragraph("<b>Destination:</b>", body_style),
            Paragraph(full_dest, body_style),
            Paragraph("<b>Budget Tier:</b>", body_style),
            Paragraph(str(preferences.get("budget_tier", "Moderate")), body_style)
        ],
        [
            Paragraph("<b>Dates:</b>", body_style),
            Paragraph(f"{preferences.get('start_date', 'Flexible')} to {preferences.get('end_date', 'Flexible')}", body_style),
            Paragraph("<b>Travel Pace:</b>", body_style),
            Paragraph(str(preferences.get("pace", "Moderate")), body_style)
        ],
        [
            Paragraph("<b>Party:</b>", body_style),
            Paragraph(str(preferences.get("travel_party", "Couple")), body_style),
            Paragraph("<b>Dietary:</b>", body_style),
            Paragraph(str(preferences.get("dietary", "No preference")), body_style)
        ],
        [
            Paragraph("<b>Interests:</b>", body_style),
            Paragraph(", ".join(preferences.get("interests", ["Culture", "Food"])), body_style),
            Paragraph("<b>Est. Total:</b>", body_style),
            Paragraph(f"<b>{format_currency(cost_summary.get('trip_total_inr', trip_data.get('estimated_cost', 0)))}</b>", body_bold)
        ]
    ]
    summary_table = Table(summary_cells, colWidths=[1.1 * inch, 2.6 * inch, 1.2 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DFD9CC")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # 3. DAY-BY-DAY ITINERARY
    story.append(Paragraph("Day-by-Day Curated Schedule", h1_style))

    for day in days:
        day_num = day.get("day", 1)
        theme = day.get("theme", "Exploration")
        area = day.get("area", "District Cluster")

        # Day header banner
        day_banner_data = [
            [
                Paragraph(f"DAY {day_num}: {theme.upper()}", day_banner_style),
                Paragraph(f"Cluster: {area}", ParagraphStyle('ClusterText', parent=day_banner_style, alignment=2, fontSize=9))
            ]
        ]
        day_banner_table = Table(day_banner_data, colWidths=[5.0 * inch, 2.4 * inch])
        day_banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))

        # Daily slots table
        slot_rows = []
        for slot_key, slot_label, slot_color in [
            ("morning", "MORNING", colors.HexColor("#D97706")),
            ("lunch", "LUNCH", colors.HexColor("#059669")),
            ("afternoon", "AFTERNOON", colors.HexColor("#2563EB")),
            ("evening", "EVENING", colors.HexColor("#7C3AED"))
        ]:
            slot_data = day.get(slot_key, {})
            name = slot_data.get("name", "Scheduled Activity")
            desc = slot_data.get("description", "")
            time_str = slot_data.get("time", "")
            dur_str = slot_data.get("duration", "")
            cost_val = slot_data.get("cost_inr", 0)
            loc = slot_data.get("location", "")

            timing_display = f"{time_str} ({dur_str})" if time_str and dur_str else time_str
            est_cost_display = format_currency(cost_val)

            slot_rows.append([
                Paragraph(f"<b><font color='{slot_color}'>{slot_label}</font></b><br/><font size='7' color='#6B7280'>{timing_display}</font>", body_style),
                Paragraph(f"<b>{name}</b><br/>{desc}<br/><font size='7' color='#6B7280'>📍 {loc} • Est: {est_cost_display}</font>", body_style)
            ])

        # Daily cost line
        d_cost = day.get("daily_cost", {})
        cost_breakdown_str = f"Day {day_num} Est: Activities {format_currency(d_cost.get('activities', 0))} | Food {format_currency(d_cost.get('food', 0))} | Transport {format_currency(d_cost.get('transport', 0))} | <b>Day Total: {format_currency(d_cost.get('total', 0))}</b>"
        slot_rows.append([
            Paragraph("<b>DAILY TOTAL</b>", meta_style),
            Paragraph(cost_breakdown_str, body_style)
        ])

        day_content_table = Table(slot_rows, colWidths=[1.8 * inch, 5.6 * inch])
        day_content_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-2), LIGHT_BG),
            ('BACKGROUND', (0,-1), (-1,-1), ACCENT_BG),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))

        day_block = KeepTogether([day_banner_table, day_content_table, Spacer(1, 12)])
        story.append(day_block)

    # 4. BUDGET BREAKDOWN SUMMARY
    story.append(Spacer(1, 10))
    story.append(Paragraph("Estimated Budget Summary", h1_style))
    budget_data = [
        [Paragraph("<b>Expense Category</b>", body_bold), Paragraph("<b>Estimated Cost (INR)</b>", body_bold), Paragraph("<b>Estimated Cost (USD)</b>", body_bold)],
        [Paragraph("Activities & Sightseeing", body_style), Paragraph(format_currency(cost_summary.get('activities_total', 0)), body_style), Paragraph(format_currency(cost_summary.get('activities_total', 0), 'USD'), body_style)],
        [Paragraph("Dining & Food", body_style), Paragraph(format_currency(cost_summary.get('food_total', 0)), body_style), Paragraph(format_currency(cost_summary.get('food_total', 0), 'USD'), body_style)],
        [Paragraph("Local City Transportation", body_style), Paragraph(format_currency(cost_summary.get('transport_total', 0)), body_style), Paragraph(format_currency(cost_summary.get('transport_total', 0), 'USD'), body_style)],
        [Paragraph(f"Accommodation ({len(days)} Nights Est.)", body_style), Paragraph(format_currency(cost_summary.get('accommodation_estimated', 0)), body_style), Paragraph(format_currency(cost_summary.get('accommodation_estimated', 0), 'USD'), body_style)],
        [Paragraph("<b>TOTAL TRIP ESTIMATE</b>", body_bold), Paragraph(f"<b>{format_currency(cost_summary.get('trip_total_inr', 0))}</b>", body_bold), Paragraph(f"<b>{format_currency(cost_summary.get('trip_total_inr', 0), 'USD')}</b>", body_bold)]
    ]
    budget_table = Table(budget_data, colWidths=[3.4 * inch, 2.0 * inch, 2.0 * inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2D3142")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FEE2E2")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(budget_table)

    # 5. EMERGENCY CHECKLIST (As specified in requirement Section 14)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Essential Travel & Emergency Checklist", h1_style))
    checklist_data = [
        [Paragraph("<b>Emergency Contacts & Essentials</b>", body_bold), Paragraph("<b>Prepared Status</b>", body_bold)],
        [Paragraph("□ Local emergency services number saved (e.g. 112 in EU/India, 911 US)", body_style), Paragraph("Checked □", meta_style)],
        [Paragraph("□ Accommodation address and booking reference printed / offline", body_style), Paragraph("Checked □", meta_style)],
        [Paragraph("□ Comprehensive travel insurance policy copy & helpline contact", body_style), Paragraph("Checked □", meta_style)],
        [Paragraph("□ Passport / Government ID physical copy & encrypted cloud backup", body_style), Paragraph("Checked □", meta_style)],
        [Paragraph("□ Embassy or consulate contact for your nationality", body_style), Paragraph("Checked □", meta_style)],
        [Paragraph("□ Prescription medications with doctor's note in original bottles", body_style), Paragraph("Checked □", meta_style)],
        [Paragraph("□ Emergency cash in local currency split across bags", body_style), Paragraph("Checked □", meta_style)],
    ]
    checklist_table = Table(checklist_data, colWidths=[5.8 * inch, 1.6 * inch])
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ACCENT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(KeepTogether([checklist_table]))

    doc.build(story)
    buffer.seek(0)
    return buffer

