import requests #fetches raw data from websites
from bs4 import BeautifulSoup #extracts specific information, imports Beautiful Soup from the bs4 library
import json #imports the json module which lets me save my dictionary as a file
import time
import threading
from selenium import webdriver #A webdriver is a robot that controls Chrome
from selenium.webdriver.chrome.service import Service #Uses ChromeDriver to import service which tells Selenium where the chromdriver is and other details
from selenium.webdriver.common.by import By #helps selenium find elements on the page like By.CLASS_NAME

def load_full_html(): #Uses Selenium to load the full HTML, javascript popups included
    service = Service("./chromedriver") #Creates a Service obkect that knows the path to Chrome Driver. The chromedriver part looks for the file

    driver = webdriver.Chrome(service=service) #driver is the robot Chrome Browser. webdriver.Chrome() launches chrome where service is and driver is the controller object Python will use

    driver.get("https://caldining.berkeley.edu/menus") #tells the robot to visit this webpage
    time.sleep(5) # to give time for javascript loading

    html = driver.page_source #The biggest part of selenium. This waits for the javascript to run (unlike requests) and puts all of the code, popups included, into the html.
    driver.quit() #Closes the chrome window and ends hte chromedriver process

    return html
    
def get_recipe_nutrition(recipe_id, menu_id):
    url = "https://dining.berkeley.edu/wp-admin/admin-ajax.php"
    payload = {"action": "get_recipe_details", "id": recipe_id, "menu_id": menu_id}

    response = requests.post(url, data=payload) #post() sends data to the url

    try:
        data = response.json() #Turns the response json file into a python dictionary
    except ValueError: #if file cannot be recieved
        print("Error: Could not parse JSON file for recipe", recipe_id)
        return {}

def get_nutrition_from_fake_api(food_id=None, menu_id=None):
    """
    Simulates Berkeley's nutrition API until campus returns from break.
    Loads data from fake_nutrition.json.
    """
    try:
        with open("fake_nutrition.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("❌ fake_nutrition.json not found!")
        return None


def clean_name(text):
    return " ".join(text.split()).title()

cache_TTL = 60*60 #Seconds the cache is valid for before refresh (60s * 60) = 1hr
menu_cache = {
    "data": None,  #The actual cached menu dictionary
    "ts": None     #The timestamp (Seconds since dict was cached)
}
cache_LOCK = threading.Lock() #protects the cache for concurrency

def caching_menu():
    '''url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)'''
    with open("Menus - Dining HTML.html") as f: #DELETE LATER _ TEMPORARY
        response = f.read()

    soup = BeautifulSoup(response, "html.parser") #Soup is a beautifulSoup object that lets you find things like soup.title

    menu = {}
    cafes = soup.find_all("li", class_="location-name")

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

                    menu[cafe_name][period_name][category_name][food_name] = get_nutrition_from_fake_api() #TEMPORARY - REPLACE WITH REAL NUTRITION INFO


                #menu[cafe_name][period_name][category_name] = food_names

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
    return dining_hall_menu[period][category][food_item]



#menu = get_menu("Crossroads")
#print(menu)

print(get_dining_halls())
print(get_periods("Crossroads"))
print(get_categories("Crossroads", "Fall - Dinner"))
print(get_food_items("Crossroads", "Fall - Dinner", "Grill"))
print(get_nutrition_info("Crossroads", "Fall - Dinner", "Grill", "Cheese Pizza"))