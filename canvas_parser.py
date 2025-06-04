import requests
import os
from datetime import datetime, timezone, timedelta
# from dateutil import tz as dateutil_tz # Available if more complex timezone logic is needed later
from flask import Flask, render_template

app = Flask(__name__)

# Helper function to parse ISO 8601 date strings, supporting 'Z' for UTC
def parse_iso_datetime(date_str: str) -> datetime | None:
    """Parses an ISO 8601 date string into a timezone-aware datetime object (UTC)."""
    if not date_str:
        return None
    try:
        # Replace 'Z' with '+00:00' for compatibility if datetime.fromisoformat doesn't handle it directly
        # (Python 3.11+ handles 'Z' in fromisoformat directly, older versions might not)
        if date_str.endswith('Z'):
            date_str_fixed = date_str[:-1] + '+00:00'
        else:
            date_str_fixed = date_str # Assume it's already in a compatible offset format or no tz
        return datetime.fromisoformat(date_str_fixed)
    except ValueError:
        # Fallback for slightly different formats or if timezone info is missing, assume UTC
        try:
            dt_naive = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            return dt_naive.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Warning: Could not parse date string '{date_str}' with expected ISO formats.")
            return None


def humanize_due_date(due_date_datetime: datetime) -> str:
    """
    Converts a timezone-aware due date (assumed UTC) into a human-friendly string.
    Times are displayed in UTC.
    """
    if not due_date_datetime:
        return "No due date"

    # Ensure due_date_datetime is UTC if it's not already (it should be from parsing)
    due_date_utc = due_date_datetime.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)

    # Calculate delta for date comparison (ignoring time part for "Today", "Tomorrow")
    today_utc_date = now_utc.date()
    due_date_utc_date = due_date_utc.date()
    delta_days = (due_date_utc_date - today_utc_date).days

    time_str = due_date_utc.strftime("%I:%M %p UTC").lstrip('0') # e.g., 3:00 PM UTC

    if delta_days == 0:
        return f"Today at {time_str}"
    elif delta_days == 1:
        return f"Tomorrow at {time_str}"
    elif 1 < delta_days < 7:
        return f"{due_date_utc.strftime('%a')} at {time_str}" # e.g., Mon at 3:00 PM UTC
    else:
        return f"{due_date_utc.strftime('%b %d')} at {time_str}" # e.g., Oct 28 at 3:00 PM UTC


def get_courses(api_url: str, access_token: str, only_favorites: bool = False) -> list:
    courses_url = f"{api_url.rstrip('/')}/api/v1/courses"
    headers = {"Authorization": f"Bearer {access_token}"}
    all_fetched_courses = []
    page = 1
    base_params = {'per_page': 100} # include[] is a list, handle properly
    if only_favorites:
        base_params['include[]'] = ['favorites']

    while True:
        try:
            params = base_params.copy()
            params['page'] = page
            response = requests.get(courses_url, headers=headers, params=params)
            response.raise_for_status()
            current_page_courses = response.json()
            if not current_page_courses:
                break
            all_fetched_courses.extend(current_page_courses)
            if len(current_page_courses) < base_params['per_page']:
                break
            page += 1
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred fetching courses: {http_err}")
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred fetching courses: {req_err}")
            return []
        except ValueError as json_err:
            print(f"JSON decode error fetching courses: {json_err}")
            return []

    if only_favorites:
        return [course for course in all_fetched_courses if course.get('is_favorite', False)]
    return all_fetched_courses

def get_assignments(api_url: str, access_token: str, course_id: int) -> list:
    assignments_url = f"{api_url.rstrip('/')}/api/v1/courses/{course_id}/assignments"
    headers = {"Authorization": f"Bearer {access_token}"}
    assignments = []
    page = 1
    params_base = {'per_page': 100}
    while True:
        try:
            params = params_base.copy()
            params['page'] = page
            response = requests.get(assignments_url, headers=headers, params=params)
            response.raise_for_status()
            current_page_assignments = response.json()
            if not current_page_assignments:
                break
            assignments.extend(current_page_assignments)
            if len(current_page_assignments) < params_base['per_page']:
                break
            page += 1
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error fetching assignments for course {course_id}: {http_err}")
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"Request error fetching assignments for course {course_id}: {req_err}")
            return []
        except ValueError as json_err: # Includes JSONDecodeError
            print(f"JSON decode error fetching assignments for course {course_id}: {json_err}")
            return []
    return assignments

@app.route('/upcoming')
def show_upcoming_assignments():
    API_URL = os.getenv("CANVAS_API_URL")
    ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")

    if not API_URL or not ACCESS_TOKEN:
        return render_template('error.html', message="CANVAS_API_URL and CANVAS_ACCESS_TOKEN environment variables must be set."), 500

    favorite_courses = get_courses(API_URL, ACCESS_TOKEN, only_favorites=True)
    if not favorite_courses:
        # It's better to render a template even for "no courses"
        return render_template('upcoming_assignments.html', title='Upcoming Assignments', assignments=[], message="No favorite courses found or an error occurred.")

    all_upcoming_assignments = []
    now_utc = datetime.now(timezone.utc)

    for course in favorite_courses:
        course_id = course.get('id')
        course_name = course.get('name', 'N/A')
        if not course_id:
            print(f"Warning: Course '{course_name}' is missing an ID.")
            continue

        assignments_data = get_assignments(API_URL, ACCESS_TOKEN, course_id)
        for assignment in assignments_data:
            due_at_str = assignment.get('due_at')
            parsed_due_at_datetime = parse_iso_datetime(due_at_str)

            if parsed_due_at_datetime and parsed_due_at_datetime >= now_utc:
                assignment_name = assignment.get('name', 'N/A')
                points_possible = assignment.get('points_possible', 'N/A')

                all_upcoming_assignments.append({
                    'name': assignment_name,
                    'due_at_datetime': parsed_due_at_datetime,
                    'due_at_friendly': humanize_due_date(parsed_due_at_datetime),
                    'course_name': course_name,
                    'points_possible': points_possible,
                    'url': assignment.get('html_url', '#') # Add link to assignment
                })

    all_upcoming_assignments.sort(key=lambda x: x['due_at_datetime'])

    return render_template('upcoming_assignments.html',
                           title='Upcoming Canvas Assignments (Favorites)',
                           assignments=all_upcoming_assignments)

if __name__ == '__main__':
    # Note: For production, use a proper WSGI server like Gunicorn or Waitress
    app.run(debug=True, host='0.0.0.0', port=5001)
