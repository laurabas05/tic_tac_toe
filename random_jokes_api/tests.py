from django.test import TestCase
import requests

# Create your tests here.
response = requests.get("https://official-joke-api.appspot.com/random_ten")
response_json = response.json()
print(response_json)