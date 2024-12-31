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
        print(f"Driver initialized: {type(self.driver)}")
        self.actions = ActionChains(self.driver)
        self.urls = [
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=3040&choiceLevel=4&subJobCode=3040", # 간호사
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=0112&choiceLevel=4&subJobCode=0112", # 최고경영자
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=1211&choiceLevel=4&subJobCode=1211", # 생물공학연구원
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=4161&choiceLevel=4&subJobCode=4161", # 방송연출가
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=1332&choiceLevel=4&subJobCode=1332", # 컴퓨터공학자
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=5114&choiceLevel=4&subJobCode=5114", # 메이크업아티스트
            "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode=5221&choiceLevel=4&subJobCode=5221", # 비행기승무원
        ]

    def run(self):
        
        try:

            for url in self.urls:
                self.driver.get(url)
                time.sleep(WORK_TERM_SLEEP)

                selected_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.btn.full.bd-no.on")

                selected_texts = [button.text.strip() for button in selected_buttons]

                class_1 = selected_texts[0]
                class_2 = selected_texts[1]
                class_3 = selected_texts[2]
                paragraph = self.driver.find_element(By.CSS_SELECTOR, "p.mg00.pd20.bdb-1")
                extracted_text = paragraph.text


                links = self.extract_links('ul.basic-list.float.col-2', 'a')
                job_data = []

                for link in links:
                    job_detail = self.crawl_data(link)
                    job_detail['고용직업분류직업분류_1'] = class_1
                    job_detail['고용직업분류직업분류_2'] = class_2
                    job_detail['고용직업분류직업분류_3'] = class_3
                    job_detail['고용직업분류직업분류_3_설명'] = extracted_text

                    job_data.append(job_detail)
                    time.sleep(WORK_TERM_SLEEP)
                    
                self.save_to_json(job_data, f"worknet_job_data_{class_3[class_3.find('.'):].replace(' ','').replace('.','')}.json")

        except Exception as e:
            raise Exception(f"크롤링 실행 중 에러: {e}")

    def save_to_json(self, data, filename):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"데이터가 {filename} 파일로 저장되었습니다.")
        except Exception as e:
            print(f"JSON 저장 중 에러: {e}")


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
        try:
            ul_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
            )
            a_elements = ul_element.find_elements(By.CSS_SELECTOR, a_selector)

            links = [a.get_attribute("href") for a in a_elements if a.get_attribute("href")]
            return links

        except Exception as e:
            raise Exception(f"링크 추출 중 에러: {e}")


    def crawl_data(self, url):
        self.driver.get(url)
        time.sleep(1)

        try:
            job_name = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tit-job"))
            ).text.strip()

            outline = self.driver.find_element(By.XPATH, "//h3[text()='직무개요']/following-sibling::div").text.strip()

            duty = self.driver.find_element(By.XPATH, "//h3[text()='수행직무']/following-sibling::div").text.strip()

            detail_elements = self.driver.find_elements(By.CSS_SELECTOR, "ul.dash-list li")
            details = {}

            for li in detail_elements:
                text = li.text.strip()
                if ":" in text:
                    key, value = map(str.strip, text.split(":", 1))
                    details[key] = "" if value == '-' else value

            return {
                "직업명": job_name,
                "직업설명": outline,
                "수행직무/하는일": duty,
                "detail": details,
            }
        except Exception as e:
            print(f"Error while processing {url}: {e}")
            return None