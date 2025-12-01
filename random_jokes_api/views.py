from django.shortcuts import render
import requests

# Create your views here.
def get_joke(request):
    # llama a la api externa
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    data = response.json()
    
    # pasamos datos al template
    return render (request, 'random_jokes_api/random_jokes.html', {'joke': data})
