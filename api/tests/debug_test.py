import requests
import json

# Test the API endpoint directly
url = "http://localhost:8001/executive-summary"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzM0NDUxOX0.cH5yIlT0wuMDRlJw0rUVB3HCLUDCyAXkz4b4V1D3FWk"}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")