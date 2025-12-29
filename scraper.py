import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import re

# --- CONFIGURATION ---
URL = "https://register.culinary.edu/searchResults.cfm?facID=1&sorter=sch.schDateStart&sorter2=c.couTitle"
# Updated to match your new secret names
EMAIL_ADDRESS = os.environ.get('EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# For testing: I removed 4/18/2026 so it triggers an email immediately
KNOWN_DATES = ["1/30/2026"] 

def check_availability():
    print(f"DEBUG: Starting scraper. Looking for: Classic and Contemporary Sauces (Copia)")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        print("DEBUG: Fetching URL...")
        response = requests.get(URL, headers=headers, timeout=15)
        print(f"DEBUG: Response Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        print(f"DEBUG: Found {len(rows)} table rows.")

        for row in rows:
            row_text = row.get_text()
            if "Classic and Contemporary Sauces (Copia)" in row_text:
                # Extract the date using Regex
                date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', row_text)
                found_date = date_match.group(0) if date_match else "Unknown Date"
                print(f"DEBUG: Found class on {found_date}")

                if found_date not in KNOWN_DATES:
                    print(f"DEBUG: NEW DATE FOUND: {found_date}. Sending email...")
                    send_notification(found_date)
                    return 
                else:
                    print(f"DEBUG: Date {found_date} is already in ignore list.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

def send_notification(class_date):
    msg = EmailMessage()
    msg['Subject'] = "CIA sauce classes found!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    html_content = f"""
    <html>
        <body>
            <p>The scraper has found a new sauce class on {class_date}. 
            <a href="{URL}">Click here</a> to view available classes.</p>
        </body>
    </html>
    """
    msg.add_alternative(html_content, subtype='html')

    try:
        print("DEBUG: Connecting to Yahoo SMTP...")
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            smtp.login(EMAIL_
