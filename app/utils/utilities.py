from urllib.parse import urlparse, urljoin
from flask import request

def is_safe_url(target):
    """
    Ensures a redirect target is safe (belongs to the same host).
    """
    if not target:
        return False
        
    target = target.strip() 
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return (
        test_url.scheme in ('http', 'https') and
        ref_url.netloc == test_url.netloc
    )

def to_embed_url(maps_url):
    """
    Converts a regular Google Maps URL (with @lat,lng) into an embeddable iframe URL.
    Example input:
        https://www.google.com/maps/place/Eiffel+Tower/@48.8584,2.2945,17z/
    Output:
        https://www.google.com/maps?q=48.8584,2.2945&z=15&output=embed
    """
    import re
    match = re.search(r'@([-\d.]+),([-\d.]+)', maps_url)
    if not match:
        return None
    lat, lng = match.groups()
    # Adjust zoom (default 15 is good for city-level)
    return f"https://www.google.com/maps?q={lat},{lng}&z=15&output=embed"