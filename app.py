from flask import Flask, request, jsonify
import icalendar
import requests
from datetime import datetime, date, timezone, timedelta

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"

@app.route('/get_events', methods=['GET'])
def get_events():
    # Get the iCal URL from the GET request
    ical_url = request.args.get('ical_url')
    if not ical_url:
        return jsonify({"error": "Please provide an ical_url as a query parameter"}), 400
    
    try:
        # Fetch the iCal file from the provided URL
        response = requests.get(ical_url)
        calendar = icalendar.Calendar.from_ical(response.content)

        # Get today's date and set the range to the next 5 days
        today = datetime.now(timezone.utc)
        end_date = today + timedelta(days=5)

        # Find all events within the next 5 days
        events = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                event_date = component.get('dtstart').dt

                # Handle both datetime and date objects
                if isinstance(event_date, datetime):
                    if event_date.tzinfo is None:
                        event_date = event_date.replace(tzinfo=timezone.utc)
                elif isinstance(event_date, date):
                    # Convert date to datetime assuming time is midnight
                    event_date = datetime.combine(event_date, datetime.min.time(), tzinfo=timezone.utc)

                # If the event date is within the next 5 days
                if today <= event_date <= end_date:
                    events.append({
                        "summary": component.get('summary'),
                        "event_date": event_date.strftime("%A, %B %d, %Y %H:%M:%S")
                    })

        # Sort events by date
        events = sorted(events, key=lambda x: x["event_date"])

        # Return the events as JSON
        return jsonify({"events": events})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
