import requests

def generate_b_roll_asset(prompt_text, clip_index):
    """Generates an image framework asset via Pollinations AI based on B-roll prompt details."""
    cleaned_prompt = requests.utils.quote(prompt_text)
    image_url = f"https://image.pollinations.ai/p/{cleaned_prompt}?width=1024&height=1024&model=turbo&enhance=true"

    response = requests.get(image_url)
    if response.status_code == 200:
        filename = f"broll_asset_{clip_index}.jpg"
        with open(filename, "wb") as file:
            file.write(response.content)
        return filename
    return None