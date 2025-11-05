import sqlite3
import json
from datetime import datetime

def extract_data_for_dashboard():
    """Extract data from SQLite database and create JSON files for dashboard"""

    # Connect to database
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()

    # 1. Get total statistics
    cursor.execute("SELECT COUNT(*) FROM dadoscriminais")
    total_crimes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT NATUREZA_APURADA) FROM dadoscriminais")
    unique_crime_types = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT BAIRRO) FROM dadoscriminais WHERE BAIRRO != ''")
    unique_neighborhoods = cursor.fetchone()[0]

    # 2. Get top crime types
    cursor.execute("""
        SELECT NATUREZA_APURADA, COUNT(*) as count 
        FROM dadoscriminais 
        GROUP BY NATUREZA_APURADA 
        ORDER BY count DESC 
        LIMIT 15
    """)
    crime_types_data = cursor.fetchall()

    # 3. Get monthly trends
    cursor.execute("""
        SELECT strftime('%Y-%m', DATA_OCORRENCIA_BO) as month, COUNT(*) as count 
        FROM dadoscriminais 
        WHERE DATA_OCORRENCIA_BO != '' 
        GROUP BY month 
        ORDER BY month
    """)
    monthly_trends_data = cursor.fetchall()

    # 4. Get top neighborhoods
    cursor.execute("""
        SELECT BAIRRO, COUNT(*) as count 
        FROM dadoscriminais 
        WHERE BAIRRO != '' 
        GROUP BY BAIRRO 
        ORDER BY count DESC 
        LIMIT 10
    """)
    neighborhoods_data = cursor.fetchall()

    # 5. Categorize crimes for pie chart
    crime_categories = {
        'Crimes Contra o Patrimônio': ['ROUBO - OUTROS', 'FURTO DE VEÍCULO', 'ROUBO DE VEÍCULO', 'FURTO - OUTROS'],
        'Crimes Contra a Pessoa': ['LESÃO CORPORAL DOLOSA', 'LESÃO CORPORAL CULPOSA POR ACIDENTE DE TRÂNSITO', 'ESTUPRO DE VULNERÁVEL'],
        'Crimes de Drogas': ['TRÁFICO DE ENTORPECENTES', 'PORTE DE ENTORPECENTES', 'APREENSÃO DE ENTORPECENTES'],
        'Outros Crimes': []
    }

    category_counts = {category: 0 for category in crime_categories.keys()}

    for crime_type, count in crime_types_data:
        categorized = False
        for category, crimes in crime_categories.items():
            if crime_type in crimes:
                category_counts[category] += count
                categorized = True
                break
        if not categorized:
            category_counts['Outros Crimes'] += count

    # Create data structure for dashboard
    dashboard_data = {
        'stats': {
            'total_crimes': total_crimes,
            'crime_types': unique_crime_types,
            'neighborhoods': unique_neighborhoods
        },
        'crime_types': {
            'labels': [item[0] for item in crime_types_data],
            'data': [item[1] for item in crime_types_data]
        },
        'monthly_trends': {
            'labels': [item[0] for item in monthly_trends_data if item[0]],
            'data': [item[1] for item in monthly_trends_data if item[0]]
        },
        'neighborhoods': {
            'labels': [item[0] for item in neighborhoods_data],
            'data': [item[1] for item in neighborhoods_data]
        },
        'categories': {
            'labels': list(category_counts.keys()),
            'data': list(category_counts.values())
        },
        'crime_details': [
            {
                'name': item[0],
                'count': item[1],
                'percentage': round((item[1] / total_crimes) * 100, 2)
            }
            for item in crime_types_data
        ]
    }

    # Save to JSON file
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"Data extracted successfully!")
    print(f"Total crimes: {total_crimes:,}")
    print(f"Unique crime types: {unique_crime_types}")
    print(f"Unique neighborhoods: {unique_neighborhoods}")

    return dashboard_data

if __name__ == "__main__":
    extract_data_for_dashboard()
