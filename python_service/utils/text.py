def normalize_course_name(name: str) -> str:
    import re
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'[\s-]+', '_', name)
    return name