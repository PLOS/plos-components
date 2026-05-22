def fetch_design_system_title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()
