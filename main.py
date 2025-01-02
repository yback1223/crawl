from worknet_seven_jobs_crawler import WorknetCrawler  # WorknetCrawler 클래스가 정의된 파일 import
from careernet_seven_jobs_crawler import CareernetCrawler  # WorknetCrawler 클래스가 정의된 파일 import

def main():
    try:
        crawler = CareernetCrawler()

        crawler.run()
    except Exception as e:
        print(f"작업 중 오류가 발생했습니다: {e}")
    finally:
        if crawler and crawler.driver:
            crawler.driver.quit()

if __name__ == "__main__":
    main()
