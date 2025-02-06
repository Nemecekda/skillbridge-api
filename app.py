from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# Load credentials from environment variables
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("DoD SkillBridge Job Listings").sheet1  

# 🚀 Set Up Flask API
app = Flask(__name__)

@app.route('/get_skillbridge_jobs', methods=['GET'])
def get_skillbridge_jobs():
    keyword = request.args.get('keyword', '').lower()
    location_filter = request.args.get('location', '').lower()

    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400

    # Fetch all rows from Google Sheets
    all_jobs = sheet.get_all_values()
    header = all_jobs[0]  # Extract headers
    data = all_jobs[1:]   # Exclude header row

    # Debugging: Print fetched job count
    print(f"Fetched {len(data)} jobs from Google Sheets.")

    # Filter jobs based on keyword in job title, company, or job description
    matching_jobs = []
    for row in data:
        job_title = row[0].lower()
        company_name = row[1].lower()
        job_location = row[2].lower()
        job_description = row[10].lower() if len(row) > 10 else ""

        # Match keyword in title, company, or description
        if keyword in job_title or keyword in company_name or keyword in job_description:
            # Apply location filter correctly
            if not location_filter or location_filter in job_location:
                matching_jobs.append({
                    "job_title": row[0],
                    "company": row[1],
                    "location": row[2],
                    "duration": row[3],
                    "skillbridge_url": f"https://skillbridge.osd.mil/opportunities/{row[0].replace(' ', '-').lower()}"
                })

    if not matching_jobs:
        return jsonify({"error": f"No matching jobs found for keyword '{keyword}' and location '{location_filter}'."}), 404

    return jsonify(matching_jobs[:10])  # Return the top 10 matches

# Run Flask app
if __name__ == "__main__":
    app.run(port=5000)


