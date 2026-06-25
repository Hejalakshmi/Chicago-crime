"""
Dashboard view for the Chicago Crime Analytics web app.

Reads the analytical results directly from the SQLite database
(chicago_crime.db, built by the use-case scripts) using pandas, and
passes them to the dashboard template - the same approach used in the
Flask version of this app.
"""

import sqlite3
import pandas as pd
from django.conf import settings
from django.shortcuts import render


def get_dashboard_data():
    conn = sqlite3.connect(settings.CHICAGO_CRIME_DB)

    # ---- Key summary numbers ----
    total_crimes = pd.read_sql("SELECT COUNT(*) as total FROM chicago_crime", conn)['total'][0]

    arrest_rate = pd.read_sql(
        "SELECT AVG(arrest) * 100 as rate FROM chicago_crime", conn)['rate'][0]

    most_common_crime = pd.read_sql("""
        SELECT primary_type, COUNT(*) as crime_count
        FROM chicago_crime
        GROUP BY primary_type
        ORDER BY crime_count DESC
        LIMIT 1
    """, conn)

    total_years = pd.read_sql(
        "SELECT MIN(Year) as min_year, MAX(Year) as max_year FROM chicago_crime", conn)

    # ---- Tables for the dashboard ----
    crime_by_year = pd.read_sql(
        "SELECT Year, COUNT(*) as crime_count FROM chicago_crime GROUP BY Year ORDER BY Year", conn)

    top5_crime_types = pd.read_sql(f"""
        SELECT primary_type,
               COUNT(*) as crime_count,
               ROUND(COUNT(*) * 100.0 / {total_crimes}, 2) as percentage
        FROM chicago_crime
        GROUP BY primary_type
        ORDER BY crime_count DESC
        LIMIT 5
    """, conn)

    arrest_by_year = pd.read_sql("""
        SELECT Year, COUNT(*) as arrest_count
        FROM chicago_crime
        WHERE arrest = 1
        GROUP BY Year
        ORDER BY Year
    """, conn)

    conn.close()

    return {
        "total_crimes": total_crimes,
        "arrest_rate": round(arrest_rate, 2),
        "most_common_crime": most_common_crime['primary_type'][0],
        "year_range": f"{total_years['min_year'][0]} - {total_years['max_year'][0]}",
        "crime_by_year": crime_by_year.to_dict(orient='records'),
        "top5_crime_types": top5_crime_types.to_dict(orient='records'),
        "arrest_by_year": arrest_by_year.to_dict(orient='records'),
    }


def dashboard_view(request):
    context = get_dashboard_data()
    return render(request, 'dashboard/index.html', context)
