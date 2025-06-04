# Canvas API Parser Web Application

## Description

This script, now a Flask web application, fetches course and assignment data from the Canvas Learning Management System API.
It focuses on **courses that you have marked as "Favorite"** in Canvas.
For each of these favorite courses, it retrieves their assignments.

The application then processes these assignments and displays them on a web page:
- Only **upcoming assignments** are shown (i.e., assignments where the `due_at` date is present and not in the past).
- These upcoming assignments are **sorted by their due date**.
- The web page lists each upcoming assignment's name (as a link to the Canvas assignment page), a human-friendly due date (e.g., "Today at 3:00 PM UTC"), the course name, and points possible.

## Prerequisites

- Python 3.x
- Key Python libraries:
    - `Flask` (for the web application framework)
    - `requests` (for making HTTP API calls to Canvas)
    - `python-dateutil` (for robust date/time parsing, though direct datetime methods are primarily used)
- All dependencies are managed via `requirements.txt`.

## Installation

1.  **Clone the repository** (if applicable) or download the `canvas_parser.py`, `requirements.txt`, and the `templates` folder.
2.  **Navigate to the directory** containing the files.
3.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

This application requires two environment variables to be set for authentication and API endpoint configuration. These must be set in the environment where the Flask application is run.

1.  `CANVAS_API_URL`: The base URL for your Canvas instance's API.
    *   Example: `https://yourinstitution.instructure.com`
2.  `CANVAS_ACCESS_TOKEN`: Your Canvas API access token. You can generate this token from your Canvas user settings.

**Setting Environment Variables:**

-   **Linux/macOS (temporary for current session):**
    ```bash
    export CANVAS_API_URL="your_canvas_api_url"
    export CANVAS_ACCESS_TOKEN="your_canvas_access_token"
    ```
    To make them permanent, add these lines to your shell's configuration file (e.g., `.bashrc`, `.zshrc`).

-   **Windows (temporary for current session in Command Prompt):**
    ```cmd
    set CANVAS_API_URL="your_canvas_api_url"
    set CANVAS_ACCESS_TOKEN="your_canvas_access_token"
    ```
-   **Windows (temporary for current session in PowerShell):**
    ```powershell
    $env:CANVAS_API_URL="your_canvas_api_url"
    $env:CANVAS_ACCESS_TOKEN="your_canvas_access_token"
    ```
    For permanent setting on Windows, search for "environment variables" in the system settings.

## Usage

Once the prerequisites are met, dependencies are installed, and environment variables are configured:

1.  **Run the Flask application** from the script's root directory:
    ```bash
    python canvas_parser.py
    ```
2.  The script will start a local development web server.
3.  **Open your web browser** and navigate to:
    ```
    http://127.0.0.1:5001/upcoming
    ```
    (Or `http://<your-ip-address>:5001/upcoming` if accessing from another device on the same network, as the server listens on `0.0.0.0`).

The web page will display a list of your favorite courses' upcoming assignments, sorted by due date. If environment variables are missing, an error page will be shown.

Note: The Flask development server is suitable for testing. For production, consider using a dedicated WSGI server like Gunicorn or Waitress.
