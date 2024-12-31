from driver import Driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import clipboard, time
import pandas as pd
import math, random, json

COMCON = Keys.CONTROL
WORK_TERM_SLEEP = 1

class WorknetCrawler():

    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)

    def run(self):
        try:
            self.driver.get(
                "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap"
            )
            time.sleep(WORK_TERM_SLEEP)

            self.click_buttons_and_extract_third()



        except Exception as e:
            raise Exception(f"크롤링 실행 중 에러: {e}")



    def click_buttons_and_extract_third(driver):
        time.sleep(WORK_TERM_SLEEP)

        try:
            main_links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[target='_self']"))
            )

            for main_link in main_links:
                try:
                    classification_text = main_link.text.strip()

                    main_link.click()
                    time.sleep(WORK_TERM_SLEEP)

                    first_buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#jobFirst button"))
                    )
                    for first_button in first_buttons:
                        try:
                            first_class_text = first_button.text.strip()

                            first_button.click()
                            time.sleep(WORK_TERM_SLEEP)

                            second_buttons = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#jobSecond button"))
                            )

                            for second_button in second_buttons:
                                try:
                                    second_class_text = second_button.text.strip()

                                    second_button.click()
                                    time.sleep(WORK_TERM_SLEEP)

                                    third_buttons = WebDriverWait(driver, 10).until(
                                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#jobThird button"))
                                    )

                                    for third_button in third_buttons:
                                        try:
                                            third_button.click()
                                            time.sleep(WORK_TERM_SLEEP)

                                            third_class_text = third_button.text.strip()

                                            print(f'{classification_text}, {first_class_text}, {second_class_text}, {third_class_text}')
                                            


                                            return True
                                        except Exception as e:
                                            print(f"세 번째 버튼 클릭 실패: {e}")
                                except Exception as e:
                                    print(f"두 번째 버튼 클릭 실패: {e}")
                        except Exception as e:
                            print(f"첫 번째 버튼 클릭 실패: {e}")

                except Exception as e:
                    print(f"링크 클릭 실패: {e}")

        except Exception as e:
            print(f"첫 번째 버튼 찾기 실패: {e}")


    def get_links(self):
        
        links = self.extract_links('ul.basic-list.float.col-2', 'a')
        
        crawled_data = []

        for link in links:
            crawled_data_one = self.crawl_data(self.driver, link)
            print(f'crawled_data_one: {crawled_data_one}')
            crawled_data.append(crawled_data_one)
        print(crawled_data)

        return crawled_data
    

    def extract_links(self, ul_selector, a_selector):
        """
        주어진 UL 요소에서 모든 A 태그의 href를 추출하는 함수
        """
        try:
            ul_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
            )
            a_elements = ul_element.find_elements(By.CSS_SELECTOR, a_selector)

            links = [a.get_attribute("href") for a in a_elements if a.get_attribute("href")]
            return links

        except Exception as e:
            raise Exception(f"링크 추출 중 에러: {e}")


    def crawl_data(self, driver, url):
        driver.get(url)
        time.sleep(1)

        try:
            job_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tit-job"))
            ).text.strip()

            outline = driver.find_element(By.XPATH, "//h3[text()='직무개요']/following-sibling::div").text.strip()

            duty = driver.find_element(By.XPATH, "//h3[text()='수행직무']/following-sibling::div").text.strip()

            detail_elements = driver.find_elements(By.CSS_SELECTOR, "ul.dash-list li")
            details = {}

            for li in detail_elements:
                text = li.text.strip()
                if ":" in text:
                    key, value = map(str.strip, text.split(":", 1))
                    details[key] = value

            return {
                "job": job_name,
                "outline": outline,
                "duty": duty,
                "detail": details,
            }
        except Exception as e:
            print(f"Error while processing {url}: {e}")
            return None