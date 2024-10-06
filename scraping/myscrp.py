from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread, Lock
from urllib import parse
import time

class Scraper:
    
    def __init__(self, num_threads=1, show_ui=True) -> None:
        self.num_threads = num_threads
        self.show_ui = show_ui
        self.drivers = []

        self._initialize_scraper()

    def _initialize_scraper(self):
        pool = []
        for _ in range(self.num_threads):
            thread = Thread(target=self._create_driver)
            pool.append(thread)
            thread.start()
        
        for thread in pool:
            thread.join()
            
    def _create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("incognito")
        if not self.show_ui:
            options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com/imghp?hl=en")
        self.drivers.append(driver)

    def _load_thumbnails(self, driver):
        print("\nFetching image thumbnails...")
        thumbnails = driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib ViTmJb BUooTd']")
        print(f"🤖: Found {len(thumbnails)} image thumbnails!")
        
        while len(thumbnails) < self.image_limit:
            print("🤖: Scrolling...")
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(3)
            thumbnails = driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib ViTmJb BUooTd']")
            time.sleep(3)

            try:
                if driver.find_element(By.XPATH, "//input[@class='LZ4I']").is_displayed():
                    driver.find_element(By.XPATH, "//input[@class='LZ4I']").click()
            except Exception as e:
                print("\n🔴🔴 No more results to load! 🔴🔴")
                break

        return thumbnails

    def _get_images(self, driver):
        driver.get(self.url)
        thumbnails = self._load_thumbnails(driver)
        
        wait = WebDriverWait(driver, 10)
        print("\nFetching Links...")

        while len(self.images) < self.image_limit:   
            with self.shared_index_lock:
                index = self.shared_index
                self.shared_index += 1
            
            try:
                if index < self.image_limit:
                    wait.until(EC.element_to_be_clickable(thumbnails[index])).click()
                    time.sleep(2)
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//img[@class='sFlh5c pT0Scc iPVvYb']")))
                    img_window = driver.find_element(By.XPATH, "//img[@class='sFlh5c pT0Scc iPVvYb']")
                    link = img_window.get_attribute('src')
                    self.images.add(link)
                    print(link)
                else:
                    print("✔️✔️✔️ Links Scraping complete! ✔️✔️✔️")
                    break
            except Exception as e:
                print("🔴🔴 Error fetching image link: ", str(e))

    @staticmethod
    def create_url(search_query):
        parsed_query = parse.urlencode({'q': search_query})
        url = f"https://www.google.com/search?{parsed_query}&source=lnms&tbm=isch&sa=X"
        return url

    def scrape(self, query, count):
        self.threads_pool = []
        self.shared_index = 0
        self.shared_index_lock = Lock()
        self.images = set()

        self.url = self.create_url(query)
        self.image_limit = count
        start = time.time()

        for driver in self.drivers:
            thread = Thread(target=self._get_images, args=(driver,))
            self.threads_pool.append(thread)
            thread.start()

        for thread in self.threads_pool:
            thread.join()

        end = time.time()
        print(f"Total images fetched: {len(self.images)}")
        print(f"Total elapsed time for {self.image_limit} images is: {(end - start) / 60:.2f} mins")
        return self.images
