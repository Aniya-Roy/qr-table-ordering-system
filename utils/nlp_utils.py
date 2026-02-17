def extract_filters(message):
    message = message.lower()

    filters = {
        "is_veg": None,
        "max_price": None,
        "category": None
    }

    if "veg" in message:
        filters["is_veg"] = 1
    if "non veg" in message or "chicken" in message:
        filters["is_veg"] = 0

    if "under" in message:
        words = message.split()
        for w in words:
            if w.isdigit():
                filters["max_price"] = int(w)

    if "main course" in message:
        filters["category"] = "Main Course"
    if "breakfast" in message:
        filters["category"] = "Breakfast"

    return filters
