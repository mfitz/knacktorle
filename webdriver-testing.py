from chromedriver_py import binary_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from movie_clues import parse_clues_from_html

from datetime import datetime


if __name__ == '__main__':
    url = 'https://actorle.com/'
    print("Requesting {} via selenium".format(url))
    service_object = Service(binary_path)
    driver_options = Options()
    # driver_options.headless = True
    driver_options.add_argument('--headless=new')
    driver = webdriver.Chrome(service=service_object, options=driver_options)
    start = datetime.now()
    driver.get(url)
    duration = datetime.now() - start
    print("Retrieved a web page with the title '{}' in {}".format(driver.title, duration))
    # print(driver.page_source)
    print(parse_clues_from_html(driver.page_source))
    driver.quit()
