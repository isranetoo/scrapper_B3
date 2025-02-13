import os
import json
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    return random.choice(user_agents)

class RateLimiter:
    def __init__(self):
        self.last_request = 0
        self.min_interval = 15  
        self.consecutive_403s = 0
        self.requests_count = 0
        self.last_cooldown = time.time()
        self.cooldown_threshold = 10
        
    def wait(self):
        now = time.time()
        
        if self.requests_count >= self.cooldown_threshold:
            cooldown_time = 300  
            print(f"Reached {self.requests_count} requests. Cooling down for {cooldown_time} seconds...")
            time.sleep(cooldown_time)
            self.requests_count = 0
            self.last_cooldown = now
            self.consecutive_403s = 0
        
        wait_time = self.min_interval
        if self.consecutive_403s > 0:
            wait_time = min(600, self.min_interval * (3 ** self.consecutive_403s) + random.uniform(30, 60))
        
        time_to_wait = max(0, wait_time - (now - self.last_request))
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        
        self.last_request = time.time()
        self.requests_count += 1

def create_browser_session():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--user-agent={get_random_user_agent()}')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def save_progress(companies_data, last_cnpj):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'empresas_dados_partial_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump({
            'last_cnpj': last_cnpj,
            'data': companies_data
        }, f, ensure_ascii=False, indent=4)

rate_limiter = RateLimiter()

def get_company_data(cnpj, driver, max_retries=3):
    url = f'https://cnpj.biz/{cnpj}'
    retries = 0
    
    while retries < max_retries:
        try:
            rate_limiter.wait()
            driver.get(url)
            
            WebDriverWait(driver, 20).until( 
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'container')]"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            data = {}
            paragraphs = soup.select('div.container p')
            for i, p in enumerate(paragraphs[1:12], start=1):  
                if p:
                    key = f'info_{i}'
                    data[key] = p.text.strip()
            
            rate_limiter.consecutive_403s = 0 
            return data
        
        except TimeoutException:
            retries += 1
            print(f"Timeout while processing CNPJ {cnpj} (Attempt {retries}/{max_retries})")
            if retries < max_retries:
                print(f"Waiting 30 seconds before retry...")
                time.sleep(30)
                driver.quit()  
                driver = create_browser_session()
            else:
                rate_limiter.consecutive_403s += 1
                return None
        
        except WebDriverException as e:
            print(f"Browser error for CNPJ {cnpj}: {str(e)}")
            if "ERR_ACCESS_DENIED" in str(e):
                rate_limiter.consecutive_403s += 1
            return None
        
        except Exception as e:
            print(f"Unexpected error for CNPJ {cnpj}: {str(e)}")
            return None

def main():
    driver = None
    try:
        try:
            with open('cnpj_list.json', 'r', encoding='utf-8') as f:
                cnpj_data = json.load(f)
                if not isinstance(cnpj_data, dict) or 'cnpjs' not in cnpj_data:
                    raise ValueError("JSON file must contain a 'cnpjs' array")
                cnpj_list = cnpj_data['cnpjs']
        except FileNotFoundError:
            raise ValueError("Could not find cnpj_list.json file")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in cnpj_list.json")

        driver = create_browser_session()
        companies_data = []
        last_processed = None
        
        progress_files = [f for f in os.listdir('.') if f.startswith('empresas_dados_partial_')]
        if progress_files:
            latest_file = max(progress_files)
            with open(latest_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                last_processed = progress['last_cnpj']
                print(f"Resuming from CNPJ: {last_processed}")

        resume = bool(last_processed)
        for cnpj in cnpj_list:
            clean_cnpj = ''.join(filter(str.isdigit, str(cnpj)))
            
            if resume and clean_cnpj != last_processed:
                continue
            elif resume and clean_cnpj == last_processed:
                resume = False
                continue

            if len(clean_cnpj) < 14:
                print(f"Skipping invalid CNPJ: {cnpj}")
                continue

            data = get_company_data(clean_cnpj, driver)
            if data:
                data['cnpj'] = clean_cnpj
                companies_data.append(data)
                save_progress(companies_data, clean_cnpj)
            
        if not companies_data:
            print("Warning: No data was collected")
            return

        with open('empresas_dados.json', 'w', encoding='utf-8') as f:
            json.dump(companies_data, f, ensure_ascii=False, indent=4)
            
        print("Data collection completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check if your JSON file is properly formatted")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()

