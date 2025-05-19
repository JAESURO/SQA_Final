import os
import logging
import pytest
import time
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import UnexpectedAlertPresentException

os.makedirs("logs", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)
os.makedirs("reports", exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    filename=f"logs/test_log_{timestamp}.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(f"logs/test_log_{timestamp}.log", mode="w", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
@pytest.fixture(scope="module")
def driver():
    logging.info("=== [Setup] Opening Chrome ===")
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        drv = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        logging.info(" Successfully opened Chrome")
    except WebDriverException as e:
        logging.error(f" Failed to open Chrome: {e}")
        raise

    drv.implicitly_wait(10)
    yield drv
    logging.info("=== [Teardown] Close browser ===")
    drv.quit()

def take_screenshot(driver, name):
    """Helper function to take screenshots with timestamp and error handling"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/{name}_{timestamp}.png"
        try:
            driver.save_screenshot(screenshot_path)
        except WebDriverException:
            try:
                screenshot = driver.get_screenshot_as_base64()
                with open(screenshot_path, "wb") as f:
                    f.write(base64.b64decode(screenshot))
            except Exception as e:
                logging.error(f"Failed to take screenshot using base64 method: {e}")
                return None
        logging.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        return None

def test_register_and_login(driver):
    wait = WebDriverWait(driver, 10)
    driver.get("http://localhost:8080/login.html")
    logging.info(" Opened login page")

    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    logging.info(f"Using test email: {test_email}")

    driver.find_element(By.ID, "registerLink").click()
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(test_email)
    driver.find_element(By.ID, "password").send_keys("Test@1234")
    driver.find_element(By.ID, "confirmPassword").send_keys("Test@1234")
    take_screenshot(driver, "register_success_screen")
    driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()
    logging.info(" Submitted registration form")

    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        logging.info(f"Alert appeared: {alert.text}")
        alert.accept()
    except TimeoutException:
        pytest.fail("No alert appeared after registration")

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("login.html"))
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        logging.info(" Redirected to login page")
    except TimeoutException:
        pytest.fail(" Redirect to login.html did not happen")

    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(test_email)
    driver.find_element(By.ID, "password").send_keys("Test@1234")
    driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()
    logging.info(" Submitted login form")

    header = wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'Task Manager')]")))
    assert header.is_displayed(), "Login failed"
    logging.info(" Login successful")
    time.sleep(1)
    take_screenshot(driver, "login_success_screen")

    



@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/failure_{item.name}_{timestamp}.png"
                try:
                    driver.save_screenshot(screenshot_path)
                except WebDriverException:
                    try:
                        screenshot = driver.get_screenshot_as_base64()
                        with open(screenshot_path, "wb") as f:
                            f.write(base64.b64decode(screenshot))
                    except Exception as e:
                        logging.error(f"Failed to take failure screenshot: {e}")
                        return
                logging.error(f" Test failed screenshot saved: {screenshot_path}")
                if hasattr(rep, "extra"):
                    rep.extra.append(pytest.html.extras.image(screenshot_path))
            except Exception as e:
                logging.error(f"Failed to handle test failure: {e}")
