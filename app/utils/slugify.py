import re
from unidecode import unidecode

def slugify(text):
    """
    Convert a string to a URL-friendly slug.
    
    Example:
        "This is a Test" -> "this-is-a-test"
    """
    text = unidecode(str(text).lower())
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[-\s]+', '-', text)
    return text 