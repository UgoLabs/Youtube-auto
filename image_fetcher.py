import os
import requests

def fetch_images_unsplash(query: str, count: int = 4, download_folder: str = "images") -> list:
    """
    Fetches images from Unsplash based on the query.
    Requires the environment variable UNSPLASH_ACCESS_KEY to be set.
    Returns a list of local file paths for the downloaded images.
    """
    os.makedirs(download_folder, exist_ok=True)
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise Exception("Please set the UNSPLASH_ACCESS_KEY environment variable.")
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page={count}&client_id={access_key}"
    response = requests.get(url)
    data = response.json()
    image_paths = []
    for i, result in enumerate(data.get("results", [])):
        image_url = result["urls"]["regular"]
        img_data = requests.get(image_url).content
        file_path = os.path.join(download_folder, f"{query}_{i}.jpg")
        with open(file_path, "wb") as img_file:
            img_file.write(img_data)
        image_paths.append(file_path)
    return image_paths
