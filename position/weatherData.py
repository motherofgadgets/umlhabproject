import json, requests

key = 'cc37937f81cdf9eafb85b57597f9c3ef'

units = 'imperial'
cityid = '5272893'
url = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+cityid+'&units='+units+'&APPID='+key)

weather = json.loads(url.text)
mmhg = (weather['main']['pressure'] * 0.75006375541921)

print(weather['coord']['lon'], "Longitude")
print(int(mmhg), "mmHg")
print(weather['weather'][0]['description'])
