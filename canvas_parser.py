import requests
import os
from datetime import datetime, timezone

def get_courses(api_url: str, access_token: str, only_favorites: bool = False) -> list:
    """
    Fetches courses from the Canvas API.

    Args:
        api_url: The base URL of the Canvas API.
        access_token: The Canvas API access token.
        only_favorites: If True, filters for courses marked as favorite.
                        The 'is_favorite' flag must be available in the course object.

    Returns:
        A list of course objects from the JSON response.
        Returns an empty list if an error occurs or no courses are found.
    """
    courses_url = f"{api_url.rstrip('/')}/api/v1/courses"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    all_fetched_courses = []
    page = 1

    base_params = {'page': page, 'per_page': 100}
    if only_favorites:
        base_params['include[]'] = 'favorites'

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

            if len(current_page_courses) < params['per_page']:
                break

            page += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            return []
        except ValueError as json_err:
            print(f"JSON decode error: {json_err}")
            return []

    if only_favorites:
        favorite_courses = [
            course for course in all_fetched_courses if course.get('is_favorite', False) is True
        ]
        return favorite_courses
    else:
        return all_fetched_courses

def get_assignments(api_url: str, access_token: str, course_id: int) -> list:
    """
    Fetches all assignments for a given course from the Canvas API.

    Args:
        api_url: The base URL of the Canvas API.
        access_token: The Canvas API access token.
        course_id: The ID of the course.

    Returns:
        A list of assignment objects from the JSON response.
        Returns an empty list if an error occurs or no assignments are found.
    """
    assignments_url = f"{api_url.rstrip('/')}/api/v1/courses/{course_id}/assignments"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    assignments = []
    page = 1

    while True:
        try:
            params = {'page': page, 'per_page': 100}
            response = requests.get(assignments_url, headers=headers, params=params)
            response.raise_for_status()

            current_page_assignments = response.json()
            if not current_page_assignments:
                break

            assignments.extend(current_page_assignments)

            if len(current_page_assignments) < params['per_page']:
                break

            page += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while fetching assignments for course {course_id}: {http_err}")
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred while fetching assignments for course {course_id}: {req_err}")
            return []
        except ValueError as json_err:
            print(f"JSON decode error while fetching assignments for course {course_id}: {json_err}")
            return []

    return assignments

def main():
    """
    Main function to fetch and display courses and their assignments.
    It fetches only favorite courses and, for each course, lists assignments
    that are not yet past their due date, sorted by due date.
    """
    API_URL = os.getenv("CANVAS_API_URL")
    ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")

    if not API_URL or not ACCESS_TOKEN:
        print("Error: Please set CANVAS_API_URL and CANVAS_ACCESS_TOKEN environment variables.")
        return

    print(f"Fetching favorite courses from {API_URL}...")
    # Step 1: Call get_courses with only_favorites=True
    favorite_courses = get_courses(API_URL, ACCESS_TOKEN, only_favorites=True)

    if not favorite_courses:
        print("No favorite courses found or an error occurred while fetching courses.")
        return

    print(f"\nFound {len(favorite_courses)} favorite courses:")
    now_utc = datetime.now(timezone.utc) # Step 3c: Get current UTC time once

    for course in favorite_courses:
        course_id = course.get('id')
        course_name = course.get('name', 'N/A')
        is_favorite_status = course.get('is_favorite', False)

        print(f"\nCourse: {course_name} (ID: {course_id}, Favorite: {is_favorite_status})")

        if not course_id:
            print("  Error: Course ID missing, cannot fetch assignments.")
            continue

        print(f"  Fetching assignments for {course_name}...")
        assignments = get_assignments(API_URL, ACCESS_TOKEN, course_id)

        if not assignments:
            print(f"  No assignments found for {course_name}.")
            continue

        # Step 2: Create an empty list for valid assignments
        valid_assignments = []

        # Step 3: Loop through assignments, parse dates, and filter
        for assignment in assignments:
            due_at_str = assignment.get('due_at')

            # Step 3a: Check if due_at is present
            if due_at_str:
                try:
                    # Step 3b: Parse to timezone-aware datetime object
                    # Python 3.7+ fromisoformat handles 'Z' directly if it's not older python.
                    # To be safe for wider compatibility (e.g. Python < 3.11 for 'Z'), replace 'Z'.
                    if due_at_str.endswith('Z'):
                        due_at_str_fixed = due_at_str[:-1] + '+00:00'
                    else: # Should not happen with Canvas if it's always 'Z'
                        due_at_str_fixed = due_at_str

                    due_date_obj = datetime.fromisoformat(due_at_str_fixed)

                    # Step 3d: If due date is not in the past
                    if due_date_obj >= now_utc:
                        assignment['due_at_datetime'] = due_date_obj # Store for sorting
                        valid_assignments.append(assignment)
                except ValueError as ve:
                    print(f"    Warning: Could not parse due date '{due_at_str}' for assignment '{assignment.get('name')}'. Error: {ve}")
                except Exception as e: # Catch any other unexpected error during date processing
                    print(f"    Warning: An unexpected error occurred processing due date for assignment '{assignment.get('name')}'. Error: {e}")

        if not valid_assignments:
            print(f"  No upcoming assignments found for {course_name}.")
            continue

        # Step 4: Sort valid_assignments by due_at_datetime
        valid_assignments.sort(key=lambda x: x['due_at_datetime'])

        print(f"  Found {len(valid_assignments)} upcoming assignments (sorted by due date):")
        # Step 5: Iterate through sorted valid_assignments to print details
        for assignment in valid_assignments:
            assignment_name = assignment.get('name', 'N/A')
            # Display the original due_at string or format the datetime object
            due_at_display = assignment.get('due_at', 'No due date')
            points = assignment.get('points_possible', 'N/A')
            print(f"    - Name: {assignment_name}, Due: {due_at_display}, Points: {points}")

if __name__ == '__main__':
    main()
