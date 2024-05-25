import requests
import os
import uuid
import random
from pathlib import Path
from threading import Thread
import time
from queue import Queue
import ctypes

API_URL = 'https://api.cracky-drinks.vodka/nsfw'
NUM_THREADS = 50
DOWNLOAD_PATH = Path.cwd() / 'images'
DOWNLOAD_PATH.mkdir(exist_ok=True)

success_count = 0
failure_count = 0

def generate_id():
    return uuid.uuid4().hex

def get_extension(content_type):
    return {
        'jpeg': '.jpg',
        'png': '.png',
        'gif': '.gif'
    }.get(content_type.split('/')[1].split(';')[0], '.jpg')

def get_random_proxy():
    with open('proxies.txt', 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    proxy_url = random.choice(proxies)
    return {
        "http": f"http://{proxy_url}",
        "https": f"http://{proxy_url}"
    }

def fetch_data(url):
    proxy = get_random_proxy()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None

def download_image(image_url):
    response = fetch_data(image_url)
    if response:
        content_type = response.headers['Content-Type']
        image_data = response.content
        file_extension = get_extension(content_type)
        random_id = generate_id()
        image_path = DOWNLOAD_PATH / f'{random_id}{file_extension}'
        with open(image_path, 'wb') as file:
            file.write(image_data)
        update_title(True)
        print(f'Successfully downloaded {image_path}')
    else:
        update_title(False)

def update_title(successful):
    global success_count, failure_count
    if successful:
        success_count += 1
    else:
        failure_count += 1
    ctypes.windll.kernel32.SetConsoleTitleW(f'Success: {success_count}, Failures: {failure_count}')

def worker(api_url):
    while True:
        image_url = get_image_url(api_url)
        if image_url:
            download_image(image_url)

def get_image_url(api_url):
    response = fetch_data(api_url)
    if response:
        return response.json().get('url')
    return None

def main():
    threads = [Thread(target=worker, args=(API_URL,)) for _ in range(NUM_THREADS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
