# downloader.py

import requests
from urllib.parse import quote
from registry import WikiRegistry

class WikiDownloader:
    """Fetches raw content from absolute Wikipedia URLs and manages registry."""
    def __init__(self, registry: WikiRegistry):
        self.registry = registry

    def fetch_raw_html(self, page_name, lang="en"):
        count = self.registry.increment(page_name, lang)
        print(f"[{lang.upper()}] Fetching '{page_name}'... (Version #{count})")
        
        # Construct the absolute URL dynamically
        # quote() ensures characters like parentheses are safely URL-encoded
        formatted_title = quote(page_name.replace(" ", "_"))
        url = f"https://{lang}.wikipedia.org/wiki/{formatted_title}"
        
        # Remember to replace this with your email!
        headers = {
            "User-Agent": "WikiTokenizerProject/1.0 (your_email@example.com)"
        }
        
        try:
            # We are hitting the standard Wikipedia web URL, not the API
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Return the full raw HTML and the download count
            return response.text, count
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to download '{url}': {e}")
            return None, count