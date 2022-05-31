from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
import re

def scrape_url(url):

    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    ]

    user_agent = random.choice(user_agents)
    PROXY = "p.webshare.io:9999"
    chrome_options = Options()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    chrome_options.add_argument(f'--user-agent={user_agent}')

    webdriver_service = Service("/home/eric/projects/python-playground/scraper/chromedriver/stable/chromedriver")

    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    try:
        browser.get(url)
        sleep(2)
        browser.find_element(By.CLASS_NAME, 'hero-carousel').click()

    except:
        browser.save_screenshot('error.png')

    finally:
        sleep(3)

        images = []
        vertical_gallery = browser.find_element(By.CLASS_NAME, 'vertical-gallery')
        gallery_images = vertical_gallery.find_elements(By.TAG_NAME, 'img')
        for i in gallery_images:
            browser.execute_script("arguments[0].scrollIntoView();", i)
            sleep(1)
            image_src = i.get_attribute('src')
            images.append(image_src)

        page_source = browser.page_source

        doc = BeautifulSoup(page_source, "html.parser")

        listing = {}

        listing_details = doc.find(attrs={'data-testid': 'listing-details-id'})

        published_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        address = listing_details.find(class_="address-value").find("h1").string
        title = address
        slug = address.replace(' ', '-').replace(',', '').lower()
        status = listing_details.find("span", class_='statusText').string
        price = listing_details.find(class_="price-info", text=re.compile("\$\d*[^a-z]\,?\d*")).string.split('$')[1].replace(',', '')

        beds = listing_details.find(attrs={'data-testid': 'property-meta-beds'}).find("span").string if listing_details.find(attrs={'data-testid': 'property-meta-beds'}) else ''
        baths = listing_details.find(attrs={'data-testid': 'property-meta-baths'}).find("span").string if listing_details.find(attrs={'data-testid': 'property-meta-baths'}) else ''
        sq_ft = listing_details.find(attrs={'data-testid': 'property-meta-sqft'}).find("span").find("span").string.replace(',', '') if listing_details.find(attrs={'data-testid': 'property-meta-sqft'}) else ''
        sq_ft_unit = listing_details.find(attrs={'data-testid': 'property-meta-sqft'}).find('span').find(text=True, recursive=False) if listing_details.find(attrs={'data-testid': 'property-meta-sqft'}) else ''
        lot_size = listing_details.find(attrs={'data-testid': 'property-meta-lot-size'}).find("span").find("span").string.replace(',', '') if listing_details.find(attrs={'data-testid': 'property-meta-lot-size'}) else ''
        lot_size_unit = listing_details.find(attrs={'data-testid': 'property-meta-lot-size'}).find("span").find(text=True, recursive=False) if listing_details.find(attrs={'data-testid': 'property-meta-lot-size'}) else ''
        description = listing_details.find(class_='desc').string if listing_details.find(class_='desc') else ''

        listing_provider = doc.find(class_="listing-provider")
        listing_provider_data = listing_provider.find_all('ul')
        realtor = listing_provider_data[0].find_all('li')[1].text.title() if listing_provider_data[0].find_all('li')[1] else ''
        broker = listing_provider_data[1].find_all('li')[1].text.title() if listing_provider_data[1].find_all('li')[1] else ''
        phone = listing_provider_data[1].find_all('li')[2].text.title() if listing_provider_data[1].find_all('li')[2] else ''

        google_map = f"https://www.google.com/maps/place/{address.replace(' ', '+').replace(',', '')}"

        listing = {
            "title": title,
            "slug": slug,
            "published": published_date,
            "updated": '',
            "status": status,
            "address": address,
            "price": price,
            "beds":  beds,
            "baths": baths,
            "sq_ft": sq_ft,
            "sq_ft_unit": sq_ft_unit,
            "lot_size": lot_size,
            "lot_size_unit": lot_size_unit,
            "description": description,
            "realtor": realtor,
            "broker": broker,
            "phone": phone,
            "listing_urls": {
                "realtor.com": url
            },
            "google_map": google_map,
            "images": images
        }


        sleep(5)
        browser.quit()
        return listing

url = input('Enter URL:')
listing = scrape_url(url)
print(listing)