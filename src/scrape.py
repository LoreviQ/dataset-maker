"""Scrape images from source"""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import CONFIG


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


def get_json(url: str) -> dict:
    """Get json from url"""
    with urlopen(
        Request(url, headers={"User-Agent": CONFIG["scraping"]["user_agent"]})
    ) as page:
        return json.load(page)


def filter_images(data):
    """Filter images from json"""
    return [
        (
            p["file_url"]
            if p["width"] * p["height"] <= CONFIG["files"]["max_resolution"] ** 2
            else p["sample_url"]
        )
        for p in data["post"]
        if (p["parent_id"] == 0 or CONFIG["scraping"]["include_posts_with_parent"])
        and p["file_url"].lower().endswith(CONFIG["files"]["supported_types"])
    ]


def download_images() -> None:
    """Download images from source"""
    tags = get_tags()
    url = CONFIG["scraping"]["source"].format(tags)
    data = get_json(url)
    count = data["@attributes"]["count"]

    if count == 0:
        print("📷 No results found")
        return

    print(f"🎯 Found {count} results")
    test_url = f"https://gelbooru.com/index.php?page=post&s=list&tags={tags}"
    print(f"🔎 Check url in browser: {test_url}")

    # Create dataset directory if it doesn't exist
    images_folder = os.path.join(os.getcwd(), "dataset")
    os.makedirs(images_folder, exist_ok=True)

    print(f"🔽 Will download to {images_folder}. Are you sure? [y/n]")
    answer = input()
    if answer.lower() != "y":
        print("❌ Download cancelled")
        return
    print("📩 Grabbing image list...")

    image_urls = set()
    image_urls = image_urls.union(filter_images(data))
    for i in range(CONFIG["scraping"]["total_limit"] // CONFIG["scraping"]["limit"]):
        count -= CONFIG["scraping"]["limit"]
        if count <= 0:
            break
        time.sleep(0.1)
        image_urls = image_urls.union(filter_images(get_json(url + f"&pid={i+1}")))

    current_dir = os.path.basename(os.getcwd())
    scrape_file = os.path.join(os.getcwd(), f"scrape_{current_dir}.txt")
    with open(scrape_file, "w", encoding="utf-8") as f:
        f.write("\n".join(image_urls))

    print(f"🌐 Saved links to {scrape_file}\n\n🔁 Downloading images...\n")
    old_img_count = len(
        [
            f
            for f in os.listdir(images_folder)
            if f.lower().endswith(CONFIG["files"]["supported_types"])
        ]
    )

    for url in image_urls:
        try:
            filename = os.path.join(images_folder, url.split("/")[-1])
            if not os.path.exists(filename):
                print(f"Downloading {url}")
                with urlopen(
                    Request(
                        url, headers={"User-Agent": CONFIG["scraping"]["user_agent"]}
                    )
                ) as response:
                    with open(filename, "wb") as f:
                        f.write(response.read())
                time.sleep(0.5)  # Be nice to the server
        except (URLError, HTTPError) as e:
            print(f"Failed to download {url}: {e}")
        except OSError as e:
            print(f"Failed to save {filename}: {e}")

    new_img_count = len(
        [
            f
            for f in os.listdir(images_folder)
            if f.lower().endswith(CONFIG["files"]["supported_types"])
        ]
    )
    print(f"\n✅ Downloaded {new_img_count - old_img_count} images.")
