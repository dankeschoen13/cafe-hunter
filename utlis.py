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