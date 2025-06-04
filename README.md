# Canvas API Parser

## Description

This script fetches course and assignment data from the Canvas Learning Management System API. It retrieves all courses accessible with the provided API token and then lists all assignments for each of those courses, including details like due dates and points possible.

## Prerequisites

- Python 3.x
- `requests` library (managed via `requirements.txt`)

## Installation

1.  **Clone the repository** (if applicable) or download the `canvas_parser.py` and `requirements.txt` files.
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

This script requires two environment variables to be set for authentication and API endpoint configuration:

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

Once the prerequisites are met, dependencies are installed, and environment variables are configured, run the script from the root directory:

```bash
python canvas_parser.py
```

The script will output the list of courses and their corresponding assignments to the console.
