from scraping.scraper import Scraper
from utils.link_saver import LinkSaver
from downloader.downloader import Downloader
import yaml

def main():
    with open("./config.yaml", "r") as file:
        config = yaml.safe_load(file)

    search_queries = config['search_queries']
    images_limit = config['images_limit']
    csv_path = config['csv_path']
    image_path = config['image_path']

    print("Scraping: ", search_queries)
    scraper = Scraper(num_threads=5, show_ui=True)
    link_saver = LinkSaver(path=csv_path)
    downloader = Downloader(path=image_path)

    for query in search_queries:
        scraped_links = scraper.scrape(query=query, count=images_limit)
        link_saver.save_to_csv(links=scraped_links, filename=f"{query}.csv")
        downloader.download(list(scraped_links), query)

    print("All scraping tasks completed successfully!")

if __name__ == "__main__":
    main()
