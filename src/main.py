"""Main file for project."""

from scrape import download_images
from setup import prepare_project_directory


def main() -> None:
    """Main function for project."""
    prepare_project_directory()
    print("📷 Download images from gelbooru.com?")
    if input().lower() == "y":
        download_images()


if __name__ == "__main__":
    main()
