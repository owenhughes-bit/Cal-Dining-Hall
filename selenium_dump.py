"""This code essentially checks if selenium is needed. 
Although we know that we need to use selenium for popups, 
we might not ALWAYS need to use it since it slows down the code"""
from selenium import webdriver #A webdriver is a robot that controls Chrome
from selenium.webdriver.chrome.service import Service #Uses ChromeDriver to import service which tells Selenium where the chromdriver is and other details
from selenium.webdriver.common.by import By #helps selenium find elements on the page like By.CLASS_NAME
import time

#Step 1: Connect Selenium to ChromeDriver
service = Service("./chromedriver") #Creates a Service obkect that knows the path to Chrome Driver. The chromedriver part looks for the file

driver = webdriver.Chrome(service=service) #driver is the robot Chrome Browser. webdriver.Chrome() launches chrome where service is and driver is the controller object Python will use

driver.get("https://caldining.berkeley.edu/menus") #tells the robot to visit this webpage
time.sleep(5) # to give time for javascript loading

html = driver.page_source #The biggest part of selenium. This waits for the javascript to run (unlike requests) and puts all of the code, popups included, into the html.
print(html)

driver.quit() #Closes the chrome window and ends hte chromedriver process