# Script to download portfolio data from Axis MF website
# Uses selenium for automation

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class AxisMFPortfolioDownloader:
    
    def __init__(self, download_dir="downloads"):
        self.base_url = "https://www.axismf.com/statutory-disclosures"
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        self.driver = None
        
    def setup_selenium_driver(self):
        # setup chrome webdriver for automation
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # chrome_options.add_argument("--headless")  # uncomment for headless mode
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✓ Selenium WebDriver initialized successfully")
            return True
            
        except ImportError:
            print("⚠ webdriver-manager not installed. Install it using:")
            print("  pip install webdriver-manager")
            print("\nOr download ChromeDriver manually from:")
            print("  https://chromedriver.chromium.org/")
            return False
        except Exception as e:
            print(f"✗ Error setting up Selenium: {str(e)}")
            return False
    
    def download_with_selenium(self, target_month="December 2025"):
        # download using browser automation
        if not self.setup_selenium_driver():
            return None
        
        try:
            print(f"\n🌐 Navigating to: {self.base_url}")
            self.driver.get(self.base_url)
            
            wait = WebDriverWait(self.driver, 20)
            
            print("🔍 Looking for 'Monthly Scheme Portfolios' section...")
            time.sleep(2)
            
            section_found = False
            
            # try different ways to find the section
            strategies = [
                (By.XPATH, "//h2[contains(text(), 'Monthly Scheme Portfolios')]"),
                (By.XPATH, "//h3[contains(text(), 'Monthly Scheme Portfolios')]"),
                (By.XPATH, "//*[contains(text(), 'Monthly Scheme Portfolios')]"),
            ]
            
            for by, selector in strategies:
                try:
                    element = wait.until(EC.presence_of_element_located((by, selector)))
                    print(f"✓ Found section using: {selector}")
                    section_found = True
                    break
                except:
                    continue
            
            if not section_found:
                print("⚠ Could not automatically locate section")
                print("Manual steps required:")
                print("  1. Scroll to '8. Monthly Scheme Portfolios'")
                print("  2. Select month from dropdown")
                print("  3. Click download button")
                
                input("\nPress Enter after manually downloading the file...")
                return self._get_latest_downloaded_file()
            
            print(f"🔍 Looking for month selector...")
            
            # find select dropdown
            try:
                select_element = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "select"))
                )
                select = Select(select_element)
                
                print("Available months:")
                for option in select.options:
                    print(f"  - {option.text}")
                
                # select target month
                try:
                    select.select_by_visible_text(f"{target_month} – Consolidated")
                    print(f"✓ Selected: {target_month} – Consolidated")
                except:
                    # If exact match fails, try partial match
                    for option in select.options:
                        if target_month in option.text and "Consolidated" in option.text:
                            select.select_by_visible_text(option.text)
                            print(f"✓ Selected: {option.text}")
                            break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠ Could not find dropdown: {str(e)}")
            
            print("🔍 Looking for download link...")
            
            download_selectors = [
                (By.XPATH, "//a[contains(@href, '.xls') or contains(@href, '.xlsx')]"),
                (By.XPATH, "//a[contains(text(), 'Download')]"),
                (By.CLASS_NAME, "download-link"),
            ]
            
            for by, selector in download_selectors:
                try:
                    download_link = wait.until(EC.element_to_be_clickable((by, selector)))
                    print(f"✓ Found download link")
                    download_link.click()
                    print("✓ Download initiated...")
                    break
                except:
                    continue
            
            time.sleep(5)  # wait for download
            downloaded_file = self._wait_for_download()
            
            if downloaded_file:
                print(f"✓ File downloaded: {downloaded_file}")
                return downloaded_file
            else:
                print("✗ Download may not have completed")
                return None
                
        except Exception as e:
            print(f"✗ Error during automation: {str(e)}")
            return None
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ Browser closed")
    
    def download_with_requests(self):
        # simpler download method using requests
        try:
            print(f"\n🌐 Fetching page: {self.base_url}")
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print("🔍 Looking for portfolio file links...")
            excel_links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.xls' in href.lower():
                    # Check if it's for December 2025
                    text = link.get_text().strip()
                    parent_text = link.parent.get_text() if link.parent else ""
                    
                    if 'december' in text.lower() or 'december' in parent_text.lower():
                        if '2025' in text or '2025' in parent_text:
                            excel_links.append({
                                'url': href,
                                'text': text,
                                'parent': parent_text
                            })
            
            if not excel_links:
                print("✗ No suitable Excel file found")
                print("This may require Selenium automation or manual download")
                return None
            
            # Download the first matching file
            target = excel_links[0]
            file_url = target['url']
            
            # Handle relative URLs
            if not file_url.startswith('http'):
                file_url = f"https://www.axismf.com{file_url}"
            
            print(f"📥 Downloading: {file_url}")
            file_response = requests.get(file_url, timeout=60)
            file_response.raise_for_status()
            
            # Save file
            filename = os.path.basename(file_url.split('?')[0])
            if not filename.endswith(('.xls', '.xlsx')):
                filename = f"portfolio_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_response.content)
            
            print(f"✓ File saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"✗ Error with requests method: {str(e)}")
            return None
    
    def _wait_for_download(self, timeout=60):
        # wait for file download to finish
        print(f"⏳ Waiting for download (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = [f for f in os.listdir(self.download_dir) 
                    if f.endswith(('.xls', '.xlsx')) and not f.endswith('.crdownload')]
            
            if files:
                # get most recent file
                latest_file = max(
                    [os.path.join(self.download_dir, f) for f in files],
                    key=os.path.getctime
                )
                return latest_file
            
            time.sleep(1)
        
        return None
    
    def _get_latest_downloaded_file(self):
        # get most recent excel file from downloads
        try:
            files = [f for f in os.listdir(self.download_dir) 
                    if f.endswith(('.xls', '.xlsx'))]
            if files:
                latest_file = max(
                    [os.path.join(self.download_dir, f) for f in files],
                    key=os.path.getctime
                )
                return latest_file
        except:
            pass
        return None


def main():
    print("=" * 80)
    print("QONFIDO ASSIGNMENT - AUTOMATED PORTFOLIO DOWNLOAD")
    print("=" * 80)
    print()
    
    downloader = AxisMFPortfolioDownloader(download_dir="downloads")
    
    print("Select download method:")
    print("  1. Selenium (Full browser automation) - Requires Chrome")
    print("  2. Requests (Simple HTTP download) - May not work for all sites")
    print("  3. Manual (Instructions only)")
    
    choice = input("\nEnter choice (1/2/3) [default: 2]: ").strip() or "2"
    
    if choice == "1":
        downloaded_file = downloader.download_with_selenium(target_month="December 2025")
    elif choice == "2":
        downloaded_file = downloader.download_with_requests()
    else:
        print("\n📋 MANUAL DOWNLOAD INSTRUCTIONS:")
        print("=" * 80)
        print(f"1. Visit: {downloader.base_url}")
        print("2. Scroll to section '8. Monthly Scheme Portfolios'")
        print("3. Select 'December 2025 – Consolidated' from dropdown")
        print("4. Click the download button/link")
        print("5. Save the file to your preferred location")
        print("=" * 80)
        return
    
    if downloaded_file:
        print(f"\n✅ SUCCESS! File downloaded to: {downloaded_file}")
        print("\n📝 Next steps:")
        print("  1. Run consolidation script: python consolidate_portfolio.py")
        print("  2. Output CSV files will be generated in 'output' folder")
    else:
        print("\n⚠ Download failed or could not be verified")
        print("Please try manual download or check error messages above")


if __name__ == "__main__":
    main()
