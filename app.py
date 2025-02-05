from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🚀 Authenticate Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Load Google Cloud credentials from Render environment variables
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if creds_json:
    creds_dict = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
else:
    raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable is missing!")

client = gspread.authorize(creds)
sheet = client.open("DoD SkillBridge Job Listings").sheet1  

# 🚀 Set Up Flask API
app = Flask(__name__)

@app.route('/get_skillbridge_jobs', methods=['GET'])
def get_skillbridge_jobs():
    keyword = request.args.get('keyword', '').lower()
    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400

    # Fetch all rows from Google Sheets
    all_jobs = sheet.get_all_values()
    header = all_jobs[0]  # Extract headers
    data = all_jobs[1:]   # Exclude header row

    # Filter jobs based on keyword matching in job title, company, or job description
    matching_jobs = []
    for row in data:
        company_name = row[0].lower()
        internship_type = row[1].lower()
        delivery_method = row[2].lower()
        job_description = row[10].lower() if len(row) > 10 else ""

        if keyword in company_name or keyword in internship_type or keyword in job_description:
            matching_jobs.append({
                "company": row[0],
                "internship_type": row[1],
                "delivery_method": row[2],
                "duration": row[3],
                "employer_poc": row[4],
                "poc_email": row[5]
            })

    return jsonify(matching_jobs[:10])  # Return the top 10 matches

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
