import requests
response = requests.get("http://localhost:5000/api/ping")
print(response.json())  # {'python_version': 'unknown', 'status': 'alive'}
