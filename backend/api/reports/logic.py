import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from .data_loader import get_report_data
from .charts import create_usage_chart
import locale # For number formatting in the report

try:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
except locale.Error:
    # Fallback for systems where specific locale is unavailable (e.g., Windows)
    try:
        locale.setlocale(locale.LC_ALL, 'C') 
    except locale.Error:
        pass # Ignore if setting locale fails

def format_number(value):
    # Formats a number for display with commas and 2 decimal places.
    try:
        # Formats to a string with thousand separators and 2 decimal places
        return locale.format_string("%0.2f", value, grouping=True)
    except Exception:
        return str(round(value, 2))


def generate_pdf_report(start_date, end_date):
    # Orchestrates data fetching, chart generation, HTML rendering, and PDF creation.
    
    # 1. Get All Calculated Data (from data_loader.py)
    data = get_report_data(start_date, end_date)
    
    # 2. Generate Chart Image (from charts.py)
    # df_raw contains the time series needed for the chart
    chart_img_base64 = create_usage_chart(data['df_raw'], start_date, end_date)
    
    # 3. Prepare Context for Jinja2 Template
    
    # Generate the short insight/recommendation text (Requirement)
    insight = generate_insight(data['total_kwh'], data['total_cost'], data['top_consumers'])
    
    context = {
        "report_period": f"{start_date} to {end_date}",
        "total_kwh": format_number(data['total_kwh']),
        "total_cost": format_number(data['total_cost']),
        "top_consumers": data['top_consumers'], # List of dicts
        "chart_image": chart_img_base64, # Base64 string for HTML embedding
        "insight": insight,
        # Placeholder for Alert/Incidents data (requires more specific mock logic)
        "alerts": ["No high usage spikes detected during this period."]
    }
    
    # 4. Configure Jinja Environment and Render HTML
    
    # CRITICAL PATH FIX: Locate the 'templates' folder relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Goes up one level to 'api', then up another to 'backend', then into 'templates'
    templates_dir = os.path.join(current_dir, '..', '..', 'templates') 
    
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('report_template.html')
    
    # Render the template with the data context
    html_out = template.render(context)
    
    # 5. Convert to PDF using WeasyPrint
    pdf_bytes = HTML(string=html_out).write_pdf()
    
    return pdf_bytes

def generate_insight(total_kwh, total_cost, top_consumers):
    # Generates a short insight/recommendation summary (2-4 sentences).
    # Simple logic based on mock data:
    if total_kwh > 5000:
        recommendation = "Total consumption was slightly higher than average. Focus on optimizing usage for the top 3 consumers."
    elif total_kwh < 1000:
        recommendation = "Low consumption observed. Ensure all meters are reporting correctly."
    else:
        recommendation = "Consumption remains stable within expected seasonal variation. Continue monitoring the top consumers for potential efficiency gains."
        
    # The top consumer is always the first element of the sorted list
    if top_consumers:
        top_id = top_consumers[0]['contour_id']
        recommendation += f" The largest consumer, Contour ID **{top_id}**, accounted for the highest share of energy usage."
        
    return recommendation