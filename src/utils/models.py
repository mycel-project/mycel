def deep_update_dict(original: dict, updates: dict) -> dict:
    """
    Recursively merges the updates dictionary into the original dictionary.

    This function updates values in place for nested mappings without overwriting
    entire dictionaries, allowing partial updates of deeply nested structures.
    """
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            original[key] = deep_update_dict(original[key], value)
        else:
            original[key] = value
    return original
