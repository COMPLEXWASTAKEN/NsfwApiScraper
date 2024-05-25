import requests
import uuid
import random
from pathlib import Path
from threading import Thread, Event
import ctypes

API_URLS = {
    '1': 'https://api.cracky-drinks.vodka/nsfw',
    '2': 'https://nekobot.xyz/api/image?type=',
    '3': 'https://nsfwhub.onrender.com/nsfw?type=',
    '4': 'https://api.night-api.com/images/nsfw/'
}
NUM_THREADS = 0
DOWNLOAD_PATH = Path.cwd() / 'images'
DOWNLOAD_PATH.mkdir(exist_ok=True)

success_count = 0
failure_count = 0
stop_event = Event()

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

def fetch_data(url, headers=None):
    proxy = get_random_proxy()
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    if headers:
        default_headers.update(headers)
    try:
        response = requests.get(url, headers=default_headers, proxies=proxy, timeout=10)
      
        return response
    except requests.RequestException as e:
        print(f"Request exception for {url}: {e}")
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
        imagename = image_path.name
        print(f'Successfully downloaded image: {imagename}')
    else:
        update_title(False)

def update_title(successful):
    global success_count, failure_count
    if successful:
        success_count += 1
    else:
        failure_count += 1
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(f'Success: {success_count}, Failures: {failure_count}')
    except:
        pass

def worker(api_url, headers=None):
    while not stop_event.is_set():
        image_url = get_image_url(api_url, headers)
        if image_url:
            download_image(image_url)

def get_image_url(api_url, headers=None):
    response = fetch_data(api_url, headers)
    if response:
        try:
            data = response.json()
        except ValueError as e:
            print(f"Failed to parse JSON response from {api_url}: {e}")
            return None
        if isinstance(data, dict):
            if 'cracky-drinks' in api_url:
                url = data.get('url')
            elif 'nekobot' in api_url:
                url = data.get('message')
            elif 'nsfwhub' in api_url:
                url = data.get('image', {}).get('url')
            elif 'night-api' in api_url:
                try:
                    url = data.get('content', {}).get('url')
                except:
                    print(f"Failed to get image URL from {api_url}: {data}")
                    return None
            return url
        else:
            print(f"Unexpected response format from {api_url}: {data}")
    return None

def main():
    global NUM_THREADS
    print("Select API to fetch images from:")
    print("1. Cracky Drinks NSFW API (FAST)")
    print("2. Nekobot API (FAST)")
    print("3. NSFWHub API (SLOW)")
    print("4. Night API (MEDIUM)")
    choice = input("Enter the number of the API you want to use: ")

    api_url = API_URLS.get(choice)
    if not api_url:
        print("Invalid choice. Exiting.")
        return

    NUM_THREADS = int(input("Enter the number of threads: "))

    headers = None
    if choice == '2':
        tags = [
            'hass', 'hmidriff', 'pgif', '4k', 'hentai', 'holo', 'hneko', 'neko', 'hkitsune', 'kemonomimi', 
            'anal', 'hanal', 'gonewild', 'kanna', 'ass', 'pussy', 'thigh', 'hthigh', 'gah', 'coffee', 
            'food', 'paizuri', 'tentacle', 'boobs', 'hboobs', 'yaoi', 
            'cosplay', 'swimsuit', 'pantsu', 'nakadashi'
        ]
        print("Available tags: " + ", ".join(tags))
        tag = input("Enter the tag you want to search for: ")
        if tag not in tags:
            print("Invalid tag. Exiting.")
            return
        api_url += tag
    elif choice == '3':
        tags = [
            'ass', 'sixtynine', 'pussy', 'dick', 'anal', 'boobs', 'ass', 'bdsm', 'black', 'easter',
            'bottomless', 'blowjub', 'collared', 'cum', 'cumsluts', 'dp', 'dom', 'extreme', 'feet',
            'finger', 'fuck', 'futa', 'gay', 'gif', 'group', 'hentai', 'kiss', 'lesbian', 'lick',
            'pegged', 'phgif', 'puffies', 'real', 'suck', 'tattoo', 'tiny', 'toys', 'xmas'
        ]
        print("Available tags: " + ", ".join(tags))
        tag = input("Enter the tag you want to search for: ")
        if tag not in tags:
            print("Invalid tag. Exiting.")
            return
        api_url += tag
    elif choice == '4':
        api_token = input("Enter your API token for Night API: ")
        headers = {
            'authorization': api_token
        }
        tags = ['ass', 'hboobs', 'yaoi', 'thigh', 'pussy', 'paizuri', 'neko', 'hthigh', 'hneko', 'hmidriff', 'hkitsune', 'hass', 'hanal', 'gonewild', 'boobs', 'anal']
        print("Available tags: " + ", ".join(tags))
        tag = input("Enter the tag you want to search for: ")
        if tag not in tags:
            print("Invalid tag. Exiting.")
            return
        api_url += tag

    threads = [Thread(target=worker, args=(api_url, headers)) for _ in range(NUM_THREADS)]
    for thread in threads:
        thread.start()
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Stopping threads...")
        stop_event.set()
        for thread in threads:
            thread.join()
        print("All threads stopped. Exiting.")

if __name__ == "__main__":
    main()
