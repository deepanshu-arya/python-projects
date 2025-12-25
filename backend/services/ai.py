import re
from typing import List, Dict

def parse_items(text: str) -> List[Dict]:
    """
    Converts:
    '2 rice 1 milk'
    into:
    [{'item': 'rice', 'quantity': 2}, {'item': 'milk', 'quantity': 1}]
    """

    text = text.lower()
    pattern = r'(\d+)\s+([a-zA-Z]+)'

    matches = re.findall(pattern, text)

    items = []
    for qty, name in matches:
        items.append({
            "item": name,
            "quantity": int(qty)
        })

    return items
