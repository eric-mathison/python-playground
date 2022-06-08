from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
import json

def scrape_url(url):

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
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

    webdriver_service = Service("./chromedriver/stable/chromedriver")
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    listing = {}

    browser.get(url)

    page_source = browser.page_source
    browser.quit()

    doc = BeautifulSoup(page_source, "html.parser")
    listing_details = doc.select_one("script#hdpApolloPreloadedData").text
    listing_json = json.loads(listing_details)['apiCache']
    listing_zpid = json.loads(listing_details)['zpid']
    variant_json = json.loads(listing_json)['VariantQuery{"zpid":%s,"altId":null}' % (listing_zpid)]
    
    status = variant_json['property']['homeStatusForHDP']

    if status == 'OTHER':
        property_json = json.loads(listing_json)['NotForSaleShopperPlatformFullRenderQuery{"zpid":%s,"contactFormRenderParameter":{"zpid":%s,"platform":"desktop","isDoubleScroll":true}}' % (listing_zpid, listing_zpid)]
    else: 
        property_json = json.loads(listing_json)['ForSaleShopperPlatformFullRenderQuery{"zpid":%s,"contactFormRenderParameter":{"zpid":%s,"platform":"desktop","isDoubleScroll":true}}' % (listing_zpid, listing_zpid)]

    street_address = variant_json['property']['streetAddress']
    city = variant_json['property']['city']
    state = variant_json['property']['state']
    zipcode = variant_json['property']['zipcode']
    country = variant_json['property']['country']

    latitude = variant_json['property']['latitude']
    longitude = variant_json['property']['longitude']

    price = variant_json['property']['price']
    year_built = variant_json['property']['yearBuilt']

    bedrooms = property_json['property']['bedrooms']
    bathrooms = property_json['property']['bathrooms']

    sq_ft = property_json['property']['livingArea']
    living_area_unit = property_json['property']['livingAreaUnitsShort']

    lot_area_value = variant_json['property']['lotAreaValue']
    lot_area_unit = variant_json['property']['lotAreaUnit']

    description = property_json['property']['description']
    listing_url = property_json['property']['hdpUrl']

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    title = f"{street_address}, {city}, {state} {zipcode}"
    slug = f"{street_address.replace(' ', '-').lower()}-{city.replace(' ', '-').lower()}-{state.replace(' ', '-').lower()}-{zipcode}"

    map_url = f"https://www.google.com/maps/place/{street_address.replace(' ', '+')}+{city.replace(' ', '+')}+{state}+{zipcode}"
    map_image_list = property_json['property']['staticMap']['sources']
    for i in map_image_list:
        if i['width']: map_image = i['url']

    images = []
    image_list = property_json['property']['responsivePhotosOriginalRatio']
    for i in image_list: 
            jpeg = i['mixedSources']['jpeg']
            for j in jpeg:
                if j['width'] == 1536:
                    images.append(j['url'])

    listing = {
        "created_at": created_at,
        "title": title,
        "slug": slug,
        "status": status,
        "address": street_address,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "country": country,
        "latitude": latitude,
        "longitude": longitude,
        "year": year_built,
        "price": price,
        "beds": bedrooms,
        "baths": bathrooms,
        "sq_ft": sq_ft,
        "sq_ft_unit": living_area_unit,
        "lot_size": lot_area_value,
        "lot_size_unit": lot_area_unit,
        "description": description,
        "map_url": map_url,
        "map_image": map_image,
        "listing_domain": 'zillow.com',
        "listing_url": listing_url,
        "images": images
    }
    
    return listing

url = input('Enter URL:')
listing = scrape_url(url)
print(listing)