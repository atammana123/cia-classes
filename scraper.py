import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import re

# --- CONFIGURATION ---
URL = "https://register.culinary.edu/searchResults.cfm?facID=1&sorter=sch.schDateStart&sorter2=c.couTitle"
EMAIL_ADDRESS = os.environ.get('EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# The dates we already know about (to be ignored)
KNOWN_DATES = ["1/30/2026"]

def check_availability():
    print("Searching for NEW Sauce Class dates...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        
        for row in rows:
            row_text = row.get_text()
            
            # 1. Check if it's the right class and location
            if "Classic and Contemporary Sauces (Copia)" in row_text:
                
                # 2. Extract the date from this specific row
                # This regex looks for a pattern like MM/DD/YYYY
                date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', row_text)
                found_date = date_match.group(0) if date_match else "Unknown Date"
                
                # 3. Check if this is a NEW date
                if found_date not in KNOWN_DATES:
                    print(f"New date detected: {found_date}! Sending email...")
                    send_notification(found_date)
                    return # Exit after sending one notification to avoid spamming

        print("No new dates found.")

    except Exception as e:
        print(f"Error: {e}")

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

    # UPDATED FOR YAHOO:
    # Yahoo uses port 465 with SSL
    try:
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully via Yahoo.")
    except Exception as e:
        print(f"SMTP Error: {e}")
