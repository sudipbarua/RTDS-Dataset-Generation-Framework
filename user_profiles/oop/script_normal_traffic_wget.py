import yaml
import random
import time
import os

def download_files():
    # reading data (weblinks) from config file
    with open('bot_config_parameters.yml', 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
        links = data['browsing']['websites']

    # An infinite loop for random link selection and wget at random intervals
    while True:
        link = random.choice(links)
        if isinstance(link, dict):
            link = random.choice(link['browse_search'])
        else:
            link = link
        print(f"Selecting a random link: {link}")
        delay = random.randint(60, 300)
        print(f"waiting for {delay} seconds before next wget")
        os.system(f'wget -c --read-timeout=5 --tries=0 {link}')
        time.sleep(delay)

if __name__ == '__main__':
    download_files()
