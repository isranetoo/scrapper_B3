from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_data():
    driver = setup_driver()
    url = "https://www.idinheiro.com.br/investimentos/cnpj-empresas-listadas-b3/"
    driver.get(url)
    
    time.sleep(5)
    
    data = []
    for i in range(1, 402):
        try:
            empresa = driver.find_element(By.XPATH, f'//*[@id="post-1638668"]/div/figure/table/tbody/tr[{i}]/td[1]').text
            codigo = driver.find_element(By.XPATH, f'//*[@id="post-1638668"]/div/figure/table/tbody/tr[{i}]/td[2]').text
            cnpj = driver.find_element(By.XPATH, f'//*[@id="post-1638668"]/div/figure/table/tbody/tr[{i}]/td[3]').text
            banco = driver.find_element(By.XPATH, f'//*[@id="post-1638668"]/div/figure/table/tbody/tr[{i}]/td[4]').text
            
            data.append([empresa, codigo, cnpj, banco])
            print(f"Processed row {i}: {empresa}")
            
        except Exception as e:
            print(f"Error processing row {i}: {str(e)}")
            continue
    
    driver.quit()
    return data

def save_to_csv(data):
    headers = ['Empresa', 'Código(s)', 'CNPJ', 'Banco escriturador']
    with open('empresas_b3.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)

def main():
    print("Starting web scraping...")
    data = scrape_data()
    save_to_csv(data)
    print("Data saved to empresas_b3.csv")

if __name__ == "__main__":
    main()
