from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import json

def get_car_name(listing):
    """Extract car name from listing"""
    try:
        name = listing.find_element(By.CSS_SELECTOR, "h2").text
    except:
        name = ""
    return name

def get_car_price(listing):
    """Extract car price from listing"""
    try:
        # Look for price in orange colored elements or bold text
        price_element = listing.find_element(By.CSS_SELECTOR, ".text-orange-500, .bg-orange-500, .font-bold")
        price_text = price_element.text.strip()
        
        # Only return if it contains numbers (likely a price)
        if re.search(r'\d', price_text) and ('€' in price_text or price_text.replace('.', '').replace(',', '').isdigit()):
            return price_text
        return ""
    except:
        return ""

def get_car_year(listing):
    """Extract car year from listing"""
    try:
        # Find all span elements and look for 4-digit year
        spans = listing.find_elements(By.CSS_SELECTOR, "span")
        for span in spans:
            text = span.text.strip()
            # Match 4-digit year starting with 19xx or 20xx
            if re.match(r'^(19|20)\d{2}$', text):
                return text
        return ""
    except:
        return ""

def get_car_mileage(listing):
    """Extract car mileage from listing"""
    try:
        # Find all span elements and look for mileage (contains 'km' and numbers)
        spans = listing.find_elements(By.CSS_SELECTOR, "span")
        for span in spans:
            text = span.text.strip()
            if 'km' in text.lower() and re.search(r'\d', text):
                return text
        return ""
    except:
        return ""

def get_car_url(listing, driver):
    """Extract car detail URL from listing by clicking and checking for pop-up/modal"""
    try:
        # First, try to find direct links
        href_elements = listing.find_elements(By.CSS_SELECTOR, "a[href]")
        for element in href_elements:
            href = element.get_attribute("href")
            if href and ('vehicle' in href or 'proxy' in href):
                if href.startswith('/'):
                    return "https://www.gaspedaal.nl" + href
                return href
        
        # If no direct link found, try clicking the listing to open pop-up/modal
        original_url = driver.current_url
        original_window_handles = driver.window_handles
        
        # Scroll the element into view and click
        driver.execute_script("arguments[0].scrollIntoView(true);", listing)
        driver.execute_script("arguments[0].click();", listing)
        
        # Wait a moment for any pop-up or new page to load
        import time
        time.sleep(2)
        
        # Check if a new window/tab opened
        new_window_handles = driver.window_handles
        if len(new_window_handles) > len(original_window_handles):
            # Switch to new window and get URL
            driver.switch_to.window(new_window_handles[-1])
            new_url = driver.current_url
            driver.close()
            driver.switch_to.window(original_window_handles[0])
            return new_url
        
        # Check if current URL changed (same tab navigation)
        elif driver.current_url != original_url:
            new_url = driver.current_url
            driver.back()  # Go back to listings page
            time.sleep(1)
            return new_url
        
        # Check for modal/pop-up with links
        else:
            try:
                # Look for modal or pop-up elements that might have appeared
                modal_links = driver.find_elements(By.CSS_SELECTOR, 
                    ".modal a[href*='vehicle'], .popup a[href*='vehicle'], [role='dialog'] a[href*='vehicle']")
                
                if modal_links:
                    url = modal_links[0].get_attribute("href")
                    # Close modal by pressing Escape or clicking close button
                    try:
                        close_button = driver.find_element(By.CSS_SELECTOR, 
                            ".modal-close, .popup-close, [aria-label='close'], .close")
                        close_button.click()
                    except:
                        driver.send_keys(Keys.ESCAPE)
                    
                    if url.startswith('/'):
                        return "https://www.gaspedaal.nl" + url
                    return url
            except:
                pass
        
        return ""
        
    except Exception as e:
        print(f"Error getting URL: {e}")
        # Try to get back to original state
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            elif driver.current_url != original_url:
                driver.back()
        except:
            pass
        return ""

def scrape_gaspedaal_cars():
    """Main function to scrape car listings"""
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service("./chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to the page
        url = "https://www.gaspedaal.nl/toyota/corolla/stationwagon?brnst=25&bmin=2020&pmax=20000&kmax=120000&srt=df-a"
        driver.get(url)
        
        # Wait for listings to load
        wait = WebDriverWait(driver, 10)
        listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='occasion-item']")))
        print(f"Found {len(listings)} car listings")
        
        # Extract data from each listing
        cars = []
        for i, listing in enumerate(listings, 1):
            print(f"Processing car {i}/{len(listings)}")
            
            car_data = {
                "name": get_car_name(listing),
                "price": get_car_price(listing),
                "year": get_car_year(listing),
                "mileage": get_car_mileage(listing),
                "url": get_car_url(listing, driver)
            }
            
            cars.append(car_data)
            
            # Print extracted data for verification
            print(f"  Name: {car_data['name']}")
            print(f"  Price: {car_data['price']}")
            print(f"  Year: {car_data['year']}")
            print(f"  Mileage: {car_data['mileage']}")
            print(f"  URL: {car_data['url']}")
            print("-" * 50)
        
        return cars
    
    finally:
        driver.quit()

def save_to_json(cars, filename="gaspedaal_cars.json"):
    with open(filename, 'w') as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)

# Run the scraper
if __name__ == "__main__":
    cars = scrape_gaspedaal_cars()
    save_to_json(cars)

    