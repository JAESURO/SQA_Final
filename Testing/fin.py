import os
import logging
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
import base64

# Create directories for logs, screenshots, and reports
os.makedirs("logs", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Configure logging with timestamp in filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    filename=f"logs/test_log_{timestamp}.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

@pytest.fixture(scope="module")
def driver():
    logging.info("=== [Setup] Opening Firefox ===")
    try:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--start-maximized")
        drv = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
        logging.info("✅ Successfully opened Firefox")
    except WebDriverException as e:
        logging.error(f"❌ Failed to open Firefox: {e}")
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
        
        # Try different methods to take screenshot
        try:
            # Method 1: Direct screenshot
            driver.save_screenshot(screenshot_path)
        except WebDriverException:
            try:
                # Method 2: Using base64
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
    logging.info("Open login page")
    driver.get("http://localhost:8080/login.html")
    take_screenshot(driver, "login_page")

    # Generate unique email using timestamp
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    logging.info(f"Using test email: {test_email}")

    logging.info("Register link")
    driver.find_element(By.ID, "registerLink").click()
    take_screenshot(driver, "register_page")

    logging.info("Register form")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(test_email)
    driver.find_element(By.ID, "password").send_keys("Test@1234")
    driver.find_element(By.ID, "confirmPassword").send_keys("Test@1234")
    take_screenshot(driver, "register_form_filled")
    driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()

    # Handle registration alert
    try:
        alert = wait.until(EC.alert_is_present())
        alert_text = alert.text
        assert alert_text == "Registration successful! Please login."
        alert.accept()
        logging.info("✅ Registration alert handled")
        take_screenshot(driver, "registration_success")
    except TimeoutException:
        take_screenshot(driver, "registration_failed")
        logging.error("❌ Registration alert not found")
        raise

    # Wait for redirect to login page
    wait.until(EC.url_contains("login.html"))
    logging.info("✅ Redirected to login page")
    take_screenshot(driver, "redirected_to_login")

    logging.info("Login form")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(test_email)
    driver.find_element(By.ID, "password").send_keys("Test@1234")
    take_screenshot(driver, "login_form_filled")
    driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()

    logging.info("Successful login")
    header = wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'Task Manager')]")))
    assert header.is_displayed(), "login failed"
    logging.info("✅ Login successful")
    take_screenshot(driver, "login_success")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Enhanced screenshot and reporting functionality"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/failure_{item.name}_{timestamp}.png"
                
                # Try different methods to take screenshot
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
                
                logging.error(f"❌ Test failed screenshot saved: {screenshot_path}")
                
                # Add screenshot to the HTML report
                if hasattr(rep, "extra"):
                    rep.extra.append(pytest.html.extras.image(screenshot_path))
            except Exception as e:
                logging.error(f"Failed to handle test failure: {e}")