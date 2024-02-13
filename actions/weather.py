import os
import requests
from actions.find_location import get_location

WEATHER_API_KEY = os.getenv('WEATHER')

##### Helper Functions #####

def format_weather(weather, unit_system='metric'):
    # Dictionary to hold the units for each weather attribute
    units = {
        'metric': {
            'temperature': '°C',
            'feels_like': '°C',
            'pressure': 'mb',
            'precipitation': 'mm',
            'wind_speed': 'kph',
            'gust_speed': 'kph',
        },
        'imperial': {
            'temperature': '°F',
            'feels_like': '°F',
            'pressure': 'inHg',
            'precipitation': 'in',
            'wind_speed': 'mph',
            'gust_speed': 'mph',
        }
    }
    
    units = units.get(unit_system, {})  # Get the units for the specified unit system

    # Start with an empty string
    weather_string = ""

    # Iterate through the weather dictionary
    for key, value in weather.items():
        # Append the key, value, and unit to the string, each on a new line
        if value is not None:  # Only add the entry if the value is not None
            weather_string += f"{key.replace('_', ' ').capitalize()}: {value} {units.get(key, '')}\n"

    # Return the formatted string, stripping the last newline character
    return weather_string.rstrip()

def parse_weather_data(weather_data, unit_system):
    """Parse the weather data from the API response into a more readable format.

    Args:
        weather_data (_type_): _description_
        unit_system (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Extract location data
    location_info = weather_data.get('location', {})
    location = {
        'name': location_info.get('name'),
        'region': location_info.get('region'),
        'country': location_info.get('country'),
        'latitude': location_info.get('lat'),
        'longitude': location_info.get('lon'),
        'timezone_id': location_info.get('tz_id'),
        'localtime': location_info.get('localtime')
    }

    # Extract current weather data
    current_weather = weather_data.get('current', {})
    weather_info = {
        'last_updated': current_weather.get('last_updated'),
        'is_day': current_weather.get('is_day'),
        'condition': current_weather.get('condition', {}).get('text'),
        'condition_icon': current_weather.get('condition', {}).get('icon'),
        'condition_code': current_weather.get('condition', {}).get('code'),
        'wind_degree': current_weather.get('wind_degree'),
        'wind_dir': current_weather.get('wind_dir'),
        'humidity': current_weather.get('humidity'),
        'cloud': current_weather.get('cloud'),
        'visibility': current_weather.get(f'vis_{"km" if unit_system == "metric" else "miles"}'),
        'uv_index': current_weather.get('uv'),
    }

    # Extract temperature, pressure, precipitation, and wind data based on unit system
    if unit_system == 'metric':
        weather_short = {
            'temperature': current_weather.get('temp_c'),
            'feels_like': current_weather.get('feelslike_c'),
            'pressure': current_weather.get('pressure_mb'),
            'precipitation': current_weather.get('precip_mm'),
            'wind_speed': current_weather.get('wind_kph'),
            'gust_speed': current_weather.get('gust_kph'),
        }
    elif unit_system == 'imperial':
        weather_short = {
            'temperature': current_weather.get('temp_f'),
            'feels_like': current_weather.get('feelslike_f'),
            'pressure': current_weather.get('pressure_in'),
            'precipitation': current_weather.get('precip_in'),
            'wind_speed': current_weather.get('wind_mph'),
            'gust_speed': current_weather.get('gust_mph'),
        }

    return {'location': location, 'weather': weather_info, 'weather_short': format_weather(weather_short, unit_system)}

##### Weather Action Functions #####

def get_weather():
    """Get the Weather data for the current location of the user at the current time.

    Returns:
        Dict: Weather data as a dictionary
    """
    location = get_location(standalone=False)
    lat =location["loc"][0]
    lon = location["loc"][1]
    url = "http://api.weatherapi.com/v1/current.json"
    #complete_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    response = requests.get(url, params={"key": WEATHER_API_KEY, "q": f"{lat},{lon}"})
    raw_data = response.json()
    
    final_weather_data = parse_weather_data(raw_data, "metric")
    return final_weather_data["weather_short"]

def get_weather_forecast(): # Example of a function that would be used in the future, this is also being used to show what happens without a function docstring for an Action when being passed to the LLM
    pass
