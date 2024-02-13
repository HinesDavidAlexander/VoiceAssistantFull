import requests
from actions.utils.action_output_prettify import dict_to_pretty_string

def get_location(standalone: bool = True):
    """Get the location of the user based on their IP address.

    Args:
        standalone (bool, optional): if function is to return as if it's a standalone call or a helper. Defaults to True.

    Returns:
        _type_: _description_
    """
    response = requests.get('http://ipinfo.io/json')
    data = response.json()
    
    city = data.get('city', 'Not Available')
    region = data.get('region', 'Not Available')
    country = data.get('country', 'Not Available')
    loc = data.get('loc', 'Not Available')  # Latitude and Longitude
    loc = loc.split(',')
    ip = data.get('ip', 'Not Available')
    
    if standalone:
        return dict_to_pretty_string({"city": city, "region": region, "country": country, "loc": loc, "ip": ip})
    else:
        return {"city": city, "region": region, "country": country, "loc": loc, "ip": ip}