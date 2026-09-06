import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

REPORTS_DIR = os.path.join("assets","reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_report_for_player(player, sport, df_player_sport, stats):
    if df_player_sport is None or df_player_sport.empty:
        return None

    filename = os.path.join(REPORTS_DIR, f"{player}_{sport}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    temp_chart = os.path.join(REPORTS_DIR, "temp_chart.png")

    # Create chart image
    plt.figure(figsize=(10, 6))
    
    if sport in ["Running", "Swimming"]:
        # Plot Speed and Distance for running/swimming
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Speed chart
        ax1.plot(df_player_sport["Date"], df_player_sport["Speed"], marker="o", linestyle="-", color='blue', linewidth=2)
        ax1.set_title(f"{player} — {sport} Speed Over Time")
        ax1.set_ylabel("Speed (km/h)")
        ax1.grid(True, linestyle="--", alpha=0.5)
        
        # Distance chart
        ax2.plot(df_player_sport["Date"], df_player_sport["Distance"], marker="s", linestyle="-", color='green', linewidth=2)
        ax2.set_title(f"{player} — {sport} Distance Over Time")
        ax2.set_ylabel("Distance (km)")
        ax2.set_xlabel("Date")
        ax2.grid(True, linestyle="--", alpha=0.5)
        
        plt.tight_layout()
        
    else:
        # For Football, plot Duration and other metrics
        metric = "Duration"
        plt.plot(df_player_sport["Date"], df_player_sport[metric], marker="o", linestyle="-", linewidth=2)
        plt.title(f"{player} — {sport} {metric} Over Time")
        plt.xlabel("Date")
        plt.ylabel(metric + " (min)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()

    plt.savefig(temp_chart, dpi=150, bbox_inches='tight')
    plt.close()

    # Build PDF
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"<b>{player} — {sport} Performance Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Summary Statistics
    story.append(Paragraph("<b>Summary Statistics</b>", styles["Heading2"]))
    
    summary_data = [
        ["Total Sessions", f"{stats['sessions']}"],
        ["Total Duration", f"{stats['total_duration']:.1f} min"],
        ["Total Distance", f"{stats['total_distance']:.2f} km"],
    ]
    
    if sport in ["Running", "Swimming"]:
        summary_data.append(["Average Speed", f"{stats['avg_speed']:.2f} km/h"])
    
    if stats['last_date'] is not None and not pd.isna(stats['last_date']):
        last_date = stats['last_date'].strftime("%Y-%m-%d")
        summary_data.append(["Last Session", last_date])

    summary_table = Table(summary_data, colWidths=[200, 100])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Performance Chart
    if os.path.exists(temp_chart):
        story.append(Paragraph("<b>Performance Trends</b>", styles["Heading2"]))
        story.append(Image(temp_chart, width=600, height=400))
        story.append(Spacer(1, 12))

    # Detailed Session Records
    story.append(Paragraph("<b>Detailed Session Records</b>", styles["Heading2"]))
    
    # Prepare table data
    table_data = [["Date", "Duration", "Distance", "Speed" if sport in ["Running", "Swimming"] else "Goals", "Assists" if sport == "Football" else "Calories", "Notes"]]
    
    for _, session in df_player_sport.iterrows():
        date_str = session["Date"].strftime("%Y-%m-%d") if not pd.isna(session["Date"]) else "N/A"
        duration = f"{session['Duration']}" if session['Duration'] else "0"
        distance = f"{session['Distance']:.2f}" if session['Distance'] else "0.00"
        
        if sport in ["Running", "Swimming"]:
            speed = f"{session['Speed']:.2f}" if session['Speed'] else "N/A"
            calories = f"{session['Calories']}" if session['Calories'] else "0"
            row = [date_str, duration, distance, speed, calories, session.get("Notes", "")]
        else:
            goals = f"{session['Goals']}" if session['Goals'] else "0"
            assists = f"{session['Assists']}" if session['Assists'] else "0"
            row = [date_str, duration, distance, goals, assists, session.get("Notes", "")]
        
        table_data.append(row)

    # Create table
    session_table = Table(table_data, repeatRows=1, colWidths=[80, 60, 60, 60, 60, 150])
    session_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(session_table)
    story.append(Spacer(1, 12))

    # Build the PDF
    doc.build(story)

    # Clean up temporary chart file
    if os.path.exists(temp_chart):
        try:
            os.remove(temp_chart)
        except:
            pass

    return filename