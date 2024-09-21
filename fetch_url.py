from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_page_content(url):
    from bs4 import BeautifulSoup as bs

    chrome_options = Options()

    chrome_options.add_argument("--headless=new")  # for Chrome >= 109
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    content = ""

    try:
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Get the page source
        html_content = driver.page_source

        # Parse HTML and extract text without tags
        content = bs(html_content, "lxml").text
        content = f"url: {url} {content}"

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

    return content


def fetch_page_content_for_urls(urls):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup as bs

    contents = []
    chrome_options = Options()

    chrome_options.add_argument("--headless=new")  # for Chrome >= 109
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for url in urls:
            driver.get(url)
            tag = "body"
            by_content = By.TAG_NAME
            if "amazon" in url:
                tag = "centerCol"
                by_content = By.ID
            elif "flipkart" in url:
                tag = "C7fEHH"
                by_content = By.CLASS_NAME
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by_content, tag))
            )

            # Get the page source
            html_content = driver.page_source

            # Parse HTML and extract text without tags
            content = bs(html_content, "lxml").text
            content = f"url: {url} {content}"
            contents.append(content)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

    return contents
