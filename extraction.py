import os
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import csv
import re


def configure_driver():
    """Configures a new Chrome driver instance with options."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Optional: Run headless
    service = Service(ChromeDriverManager().install())
    #driver = webdriver.Chrome(service=service, options=options)
    return webdriver.Chrome(service=service, options=options)


def extract_data(driver, url):
    """Extracts website speed data from Site24x7 for a given URL."""
    try:
        # Find elements and extract data
        driver.get("https://www.site24x7.com/tools/web-page-analyzer.html")
        wait = WebDriverWait(driver, 5)
        element = wait.until(ec.presence_of_element_located((By.ID, "urlLink")))
        element.send_keys(url.strip())
        element_click = wait.until(ec.presence_of_element_located((By.ID, "testBtn")))
        element_click.click()
        label = "benign"        # use to label when extracting good websites data
        #label = "maliious"     # use to label when extracting phishing websites data

        # Wait and extract data
        time.sleep(35)  # Wait timer added to wait until elements are visible

        date_string = driver.find_element(By.ID, "currentTime").text
        # regex to extract the date and time components
        match = re.search(r'(\w+ \w+ \d+ \d+).*?(\d+:\d+:\d+)', date_string) #Fri Oct 11 2024 20:34:33 GMT+0530 (India Standard Time)
        if match:
            date_part = match.group(1)  # 'Fri, Oct 11 2024'
            time_part = match.group(2)  # '20:34:33'
        else:
            date_part, time_part = None, None  # Handle cases where regex fails
        data = {
            "Website_URL": urlparse(url).geturl(),
            "Page_Size": driver.find_element(By.ID, "pageSize").text,
            "Request": driver.find_element(By.ID, "request").text,
            "Page_Load_Time": driver.find_element(By.ID, "pageLoadTime").text,
            "DNS_Time": driver.find_element(By.ID, "dnsTime").text,
            "Connection_Time": driver.find_element(By.ID, "connTime").text,
            "Start_Render_Time": driver.find_element(By.ID, "startRenderTime").text,
            "Document_Complete_Time": driver.find_element(By.ID, "docCompTime").text,
            "First_Byte_Time": driver.find_element(By.ID, "fbTime").text,
            "CSS_Count": driver.find_element(By.ID, "cssCount").text,
            "JavaScripts_Count": driver.find_element(By.ID, "scriptscount").text,
            "Image_Count": driver.find_element(By.ID, "imageCount").text,
            "Total_Objects": driver.find_element(By.ID, "totalObjects").text,
            "Date": date_part,  # extracted date
            "Time": time_part,  # extracted time
            "Label":label
        }
        return data
    except TimeoutException:
        print(f"Failed to retrieve data for URL: {url}")
        return None


def web_page_speed_test(filename, output_csv):
    """
    Loads URLs from a text file, opens a new Chrome browser for each URL,
    extracts website performance data using Site24x7's Web Page Analyzer,
    and writes the results to a CSV file.

    Args:
        filename (str): The name of the text file containing the URLs.
        output_csv (str): The name of the CSV file to store results.
    """
    results = []

    with open(filename, 'r') as f:
        urls = f.readlines()

    driver = configure_driver()  # Create a single driver instance
    try:
        for url in urls:
            data = extract_data(driver, url)
            if data:
                results.append(data)
                print("Extracted successfully :", data["Website_URL"])

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser after all extractions
        print("Data saved to csv")

        # Write results to a CSV file
        file_exists = os.path.isfile(output_csv)  # Check if the file already exists

        with open(output_csv, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = results[0].keys()  # Get field names from the first result

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()  # Write the header only if the file doesn't exist
            writer.writerows(results)  # Write the data

web_page_speed_test("testurls.txt", "output.csv")