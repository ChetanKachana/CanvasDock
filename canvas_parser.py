import requests
import os

def get_courses(api_url: str, access_token: str) -> list:
    """
    Fetches all courses from the Canvas API.

    Args:
        api_url: The base URL of the Canvas API.
        access_token: The Canvas API access token.

    Returns:
        A list of course objects from the JSON response.
        Returns an empty list if an error occurs or no courses are found.
    """
    courses_url = f"{api_url.rstrip('/')}/api/v1/courses"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    courses = []
    page = 1

    while True:
        try:
            params = {'page': page, 'per_page': 100}
            response = requests.get(courses_url, headers=headers, params=params)
            response.raise_for_status()

            current_page_courses = response.json()
            if not current_page_courses:
                break

            courses.extend(current_page_courses)

            if len(current_page_courses) < params['per_page']:
                break

            page += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            # print(f"Response content: {response.content}") # Potentially too verbose for general use
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            return []
        except ValueError as json_err:
            print(f"JSON decode error: {json_err}")
            # print(f"Response content: {response.content}") # Potentially too verbose
            return []

    return courses

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
            # print(f"Response content: {response.content}")
            return []
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred while fetching assignments for course {course_id}: {req_err}")
            return []
        except ValueError as json_err: # Includes JSONDecodeError
            print(f"JSON decode error while fetching assignments for course {course_id}: {json_err}")
            # print(f"Response content: {response.content}")
            return []

    return assignments

def main():
    """
    Main function to fetch and display courses and their assignments.
    """
    API_URL = os.getenv("CANVAS_API_URL")
    ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")

    if not API_URL or not ACCESS_TOKEN:
        print("Error: Please set CANVAS_API_URL and CANVAS_ACCESS_TOKEN environment variables.")
        return

    print(f"Fetching courses from {API_URL}...")
    all_courses = get_courses(API_URL, ACCESS_TOKEN)

    if not all_courses:
        print("No courses found or an error occurred while fetching courses.")
        return

    print(f"\nFound {len(all_courses)} courses:")
    for course in all_courses:
        course_id = course.get('id')
        course_name = course.get('name', 'N/A')
        print(f"\nCourse: {course_name} (ID: {course_id})")

        if not course_id:
            print("  Error: Course ID missing, cannot fetch assignments.")
            continue

        print(f"  Fetching assignments for {course_name}...")
        assignments = get_assignments(API_URL, ACCESS_TOKEN, course_id)

        if not assignments:
            print(f"  No assignments found for {course_name} or an error occurred.")
            continue

        print(f"  Found {len(assignments)} assignments:")
        for assignment in assignments:
            assignment_name = assignment.get('name', 'N/A')
            due_at = assignment.get('due_at', 'No due date')
            points = assignment.get('points_possible', 'N/A')
            print(f"    - Name: {assignment_name}, Due: {due_at}, Points: {points}")

if __name__ == '__main__':
    main()
