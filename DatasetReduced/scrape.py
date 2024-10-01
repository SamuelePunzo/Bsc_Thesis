import sys
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import shutil
import zipfile
import glob

def main(search_term):
    directory = './biogridFile'
    file_extension = '.tab3.txt'

    filename = search_term+'.tab3.txt'
    if filename in os.listdir(directory):
        print("File presente, caricamento in corso...")
        if filename.endswith(file_extension):
            file_path = os.path.join(directory, filename)

            try:
                df = pd.read_csv(file_path, delimiter='\t')[['Official Symbol Interactor A', 'Official Symbol Interactor B']]
                return
            except Exception as e:   
                search_gene(search_term)
    else:
        print("File non presente, scaricamento in corso...")
        search_gene(search_term) 

def search_gene(search_term):
    # Specify the path to chromedriver executable
        chrome_driver_path = './chromedriver'

        # Create a Service object with the chromedriver executable path
        service = Service(chrome_driver_path)

        try:
            # Initialize the WebDriver using the Service object
            driver = webdriver.Chrome(service=service)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return

        try:
            # Open the web page
            driver.get('https://thebiogrid.org/')

            # Find the input field by ID and input the value
            search_input = driver.find_element(By.ID, 'search')
            search_input.send_keys(search_term)

            select_element = driver.find_element(By.NAME, 'organism')
            select = Select(select_element)
            select.select_by_value('9606')

            submit_link = driver.find_element(By.CSS_SELECTOR, 'a[href*="geneSearchForm"]')
            submit_link.click()

            download_button = driver.find_element(By.ID, 'download')
            download_button.click()

            download_button = driver.find_element(By.ID, 'buildGeneButton')
            download_button.click()

            WebDriverWait(driver, 120).until(
                    EC.element_to_be_clickable((By.ID, "customDownloadButton"))
                )

            download_button = driver.find_element(By.ID, 'customDownloadButton')
            download_button.click()

            time.sleep(30)

            download_folder = 'C:\\Users\\samue\\Downloads'

            file_name = f"{search_term}.zip"  # Nome del file desiderato
            downloaded_file = max([os.path.join(download_folder, f) for f in os.listdir(download_folder)], key=os.path.getctime)
            new_file_path = os.path.join(download_folder, file_name)
            os.rename(downloaded_file, new_file_path)

            temp_dir = os.path.join(download_folder, "temp_extracted")
            with zipfile.ZipFile(new_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            tab3_file = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".tab3.txt"):
                        tab3_file = os.path.join(root, file)
                        break
                if tab3_file:
                    break

            new_filename = search_term + ".tab3.txt"
            new_file_path = os.path.join('./biogridFile', new_filename)

            shutil.copy(tab3_file, new_file_path)
        
            # Rimuove la directory temporanea
            shutil.rmtree(temp_dir)

        except Exception as e:
            print(f"Exception occurred during execution: {str(e)}")

        finally:
            # Close the driver
            driver.quit()        

        

if __name__ == "__main__":
    directory = './biogridFile'
    file_extension = '.tab3.txt'
    list = [sys.argv[1]]

    for gene in list:
        main(gene)