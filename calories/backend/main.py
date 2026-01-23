import requests #fetches raw data from websites
from bs4 import BeautifulSoup #extracts specific information, imports Beautiful Soup from the bs4 library
import json #imports the json module which lets me save my dictionary as a file
import time
import threading #prevents the code from doing the same thing multiple times. Used for cacheing to prevent two users from running caching_menu() at the same time

def load_full_html():
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url) #Scrapes the HTML from the dining hall menu website
    return response.text

def get_session_cookies():
    #Need cookies to get past the AJAX php file. This gets the cookies using requests
    session = requests.Session() #A session object that exists through multiple HTTP requests
    response = session.get("https://dining.berkeley.edu/menus/") #Makes a get request to the dining hall page to send back cookies found on the network site. The object automatically stores the cookies.
    return session.cookies.get_dict() #Turns the returned cookies into a python dictionary which will be available for future requests.

def get_recipe_nutrition(recipe_id, menu_id, location, session_cookies):
    """
    recipe_id: numeric ID for the recipe
    menu_id: numeric menu ID
    location: full base64 location string from data-location
    session_cookies: dict of cookies from Selenium session
    """
    url = "https://dining.berkeley.edu/wp-admin/admin-ajax.php"
    payload = {
        "action": "get_recipe_details",
        "location": location,
        "id": recipe_id,
        "menu_id": menu_id,
    }
    headers = { #A dictionary of request headers found under inspect needed to make an AJAX call
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://dining.berkeley.edu",
        "Referer": "https://dining.berkeley.edu/menus/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    response = requests.post(url, data=payload, headers=headers, cookies=session_cookies) #Makes the AJAX call

    if response.status_code != 200: #Will tell me or the user if there is an error recieving the nutrititon information
        print(f"Error: Status code {response.status_code} for recipe {recipe_id}")
        return {}

    html_content = response.text #Response is currently an object, .text returns it into a parseable string.
    return parse_nutrition_html(html_content)

def parse_nutrition_html(html_content): #Will extract all the nutrition information that I desire
    soup = BeautifulSoup(html_content, 'html.parser')
    nutrition_data = {} 

    #Serving Size
    serving_size = soup.find("span", class_ = "serving-size") #MUST do class_ because regular class is used to create an object
    if serving_size:
        nutrition_data['serving_size'] = serving_size.get_text(strip=True).replace('Serving Size:', '').strip() #Removes the HTML, removes 'Serving Size', and removes extra space so that it is just number, value (3.28 oz)

    #Nutrition facts
    nutrition_list = soup.find("div", class_= "nutration-details")
    if nutrition_list:
        items = nutrition_list.find_all('li')
        for item in items:
            text = item.get_text(strip=True)
            if ':' in text:
                key, value = text.split(':', 1) #text.split creates a tuple and key is assigned to the first value, with value assigned to the second
                nutrition_data[key.strip()] = value.strip()

    #Allergens
    allergens = soup.find('div', class_='allergens')
    if allergens:
        allergens_span = allergens.find('span')
        if allergens_span:
            nutrition_data['allergens'] = allergens_span.get_text(strip=True)

    return nutrition_data



def clean_name(text):
    return " ".join(text.split()).title()

cache_TTL = 60*60 #Seconds the cache is valid for before refresh (60s * 60) = 1hr
menu_cache = {
    "data": None,  #The actual cached menu dictionary
    "ts": None,     #The timestamp (Seconds since dict was cached)
    "cookies": None # Stores the cookies in cache. This makes it so we do not have to run get_session_cookies that many times (which takes a while)
}
cache_LOCK = threading.Lock() #protects the cache for concurrency

def caching_menu():
    '''url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)'''

    html = load_full_html()
    soup = BeautifulSoup(html, "html.parser") #Soup is a beautifulSoup object that lets you find things like soup.title

    menu = {}
    cafes = soup.find_all("li", class_="location-name")

    session_cookies = get_session_cookies()
    menu_cache["cookies"] = session_cookies

    for cafe in cafes:

        #Gets the Cafe Name
        title_div = cafe.find("div", class_="location-title")
        cafe_span = title_div.find("span", class_="cafe-title")
        cafe_name = clean_name(cafe_span.get_text(strip=True))

        menu[cafe_name] = {} #Nested Dictionary 1

        #Gets the meal periods (Breakfast, Lunch, Dinner)
        periods = cafe.find_all("li", class_="preiod-name")

        for period in periods:
            period_span = period.find("span", recursive=False)
            period_name = clean_name(period_span.get_text(strip=True))

            menu[cafe_name][period_name] = {} #Nested Dictionary 2

            #Gets categories of food(Hot Breakfast, Pastries, Sides, etc.)
            categories = period.find_all("div", class_="cat-name")

            for category in categories:
                category_span = category.find("span", recursive=False)
                category_name = clean_name(category_span.get_text(strip=True))

                #Creates list of food items and puts in in dictionary
                recipe_list = category.find("ul", class_="recipe-name")
                #food_names = []
                menu[cafe_name][period_name][category_name] = {}

                items = recipe_list.find_all("li", class_="recip")

                for item in items:
                    name_span = item.find("span", recursive=False)
                    food_name = clean_name(name_span.get_text(strip=True))
                    
                    recipe_id = item.get("data-id")
                    menu_id = item.get("data-menuid")
                    location = item.get("data-location")

                    menu[cafe_name][period_name][category_name][food_name] = {
                        "recipe_id": recipe_id,
                        "menu_id": menu_id,
                        "location": location,
                        "nutrition_fetched": False
                    }

    return menu
#---------------------------Cache Stuff------------------------------
def get_menu(dining_hall=None, force_refresh = False):
    """
    Parameters are:
    Dining_Hall - returns only the dining hall's function
    force_refresh: If its true, it will re-scrape immediately

    Goal:
    If the cache is empty or older than cache_TTL or the force refresh is True, then it will acquire lock and e-scrape
    It will return either the cached data or the dining_hall
    """
    global menu_cache #Makes the menu_cache dictionary available in main part and in the def
    now = time.time() #The current time
    needs_refresh = False

    if menu_cache["data"] is None:
        needs_refresh = True
    elif (now - (menu_cache["ts"] or 0)) > cache_TTL:
        needs_refresh = True
    elif force_refresh:
        needs_refresh = True

    if needs_refresh:
        with cache_LOCK: #Ensures only one thread performs the scrape at a time during concurrency
            now = time.time()
            if menu_cache["data"] is None:
                do_refresh = True
            elif (now - (menu_cache["ts"] or 0)) > cache_TTL:
                do_refresh = True
            elif force_refresh:
                do_refresh = True
            else:
                do_refresh = False

            if do_refresh:
                menu = caching_menu()
                menu_cache["data"] = menu
                menu_cache["ts"] = time.time()

    cached_menu = menu_cache["data"]
    if cached_menu == None:
        cached_menu = caching_menu()
        menu_cache["data"] = cached_menu
        menu_cache["ts"] = time.time()

    if dining_hall == None:
        return dict(cached_menu) #Dict removes chance for cached data mutation
    else:
        return dict(cached_menu.get(dining_hall, {}))
    
    
def refresh_menu():
    return get_menu(force_refresh = True) #Forces a refresh from an admin standpoint if needed

    
    #Dining hall ----> period ----> category ----> foods

def get_dining_halls(): #Returns a list of the dining hall names
    full_menu = get_menu()
    return list(full_menu.keys())

def get_periods(dining_hall): #Returns a list of the dining hall periods (Breakfast, Lunch, Dinner)
    dining_hall_menu = get_menu(dining_hall)
    return list(dining_hall_menu.keys())

def get_categories(dining_hall, period):
    dining_hall_menu = get_menu(dining_hall)
    return list(dining_hall_menu[period].keys())

def get_food_items(dining_hall, period, category):
    dining_hall_menu = get_menu(dining_hall)
    return list(dining_hall_menu[period][category].keys())

def get_nutrition_info(dining_hall, period, category, food_item):
    dining_hall_menu = get_menu(dining_hall)
    item_data = dining_hall_menu[period][category][food_item]

    if not item_data.get("nutrition_fetched", False): #If nutrition hasn't been fetched yet, fetch it now
        session_cookies = menu_cache.get("cookies")

        if not session_cookies: #Checks if session_cookies has been recieved yet or not. If not, then it gets the session cookies
            session_cookies = get_session_cookies()
            menu_cache["cookies"] = session_cookies
        
        recipe_id = item_data["recipe_id"]
        menu_id = item_data["menu_id"]
        location = item_data["location"]

        nutrition = get_recipe_nutrition(recipe_id, menu_id, location, session_cookies)

        item_data.update(nutrition) #item_data updates with the new nutrition values without removing it from the cache
        item_data["nutrition_fetched"] = True

    return {k: v for k, v in item_data.items() if k not in ["recipe_id", "menu_id", "location", "nutrition_fetched"]} #returns ONLY nutrition information while still keeping the old information apart of the dictionary

if __name__ == "__main__":
    print(get_dining_halls())
    print(get_periods("Clark Kerr Campus"))
    print(get_categories("Clark Kerr Campus", "Spring - Dinner"))
    print(get_food_items("Clark Kerr Campus", "Spring - Dinner", "Plant Forward Entree"))
    print(get_nutrition_info("Clark Kerr Campus", "Spring - Dinner", "Plant Forward Entree", "Brown Rice"))