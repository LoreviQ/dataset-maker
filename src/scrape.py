"""Scrape images from source"""


def get_tags() -> str:
    """Get tags from user"""
    tags = input("Enter space seperated tags: ")
    tags = (
        tags.replace(" ", "+")
        .replace("(", "%28")
        .replace(")", "%29")
        .replace(":", "%3a")
        .replace("&", "%26")
    )
    return tags
