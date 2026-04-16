from flask import url_for

def smart_url_filter(img_path):
    """Checks if an image path is a URL or a local static file."""
    if not img_path:
        return url_for('static', filename='images/default_cafe.jpg')

    if img_path.startswith('http'):
        return img_path

    return url_for('static', filename=img_path)


def format_time(value):
    return value.strftime('%I:%M %p')