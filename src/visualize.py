import os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def visualise(points: list[tuple[float]], driver_path: str, center=None):
    ## Open chrome drimer
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service, options=options)

    ## Set center to the first point if not provided
    if not center:
        center = points[0]

    # Open an empty page and execute JS
    html_path = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(html_path, "web", "index.html")
    driver.get(f"file://{html_path}")
    time.sleep(2)
    result = driver.execute_script("initMap(arguments[0], arguments[1])", center, points)
    time.sleep(2)