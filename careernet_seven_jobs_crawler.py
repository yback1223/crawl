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

class CareernetCrawler():

    def __init__(self):
        self.driver = Driver().set_chrome()
        print(f"Driver initialized: {type(self.driver)}")
        self.actions = ActionChains(self.driver)
        self.url = "https://www.career.go.kr/cnet/front/base/job/jobList.do#tab1"
        self.search_keywords = [
            '간호사', 'CEO', '소프트웨어', '생명과학자', '방송연출가', '메이크업아티스트', '비행기승무원'
        ]

    def run(self):
        
        try:
            
            for search_keyword in self.search_keywords:
                self.driver.get(self.url)
                time.sleep(WORK_TERM_SLEEP)

                self.input_keyword_and_set_list(search_keyword=search_keyword)
                job_links = self.get_job_links()
                print(f'job_links: {job_links}')

                search_keyword_related_jobs = []

                for job_link in job_links:
                    self.driver.get(job_link)
                    time.sleep(WORK_TERM_SLEEP)
                    extracted_job_data = self.extract_job_data(job_link)
                    print(f'extracted_job_data: {extracted_job_data}')
                    search_keyword_related_jobs.append(extracted_job_data)
                
                self.save_to_json(search_keyword_related_jobs, f"careernet_job_data_{search_keyword}.json")

        except Exception as e:
            raise Exception(f"크롤링 실행 중 에러: {e}")

    def extract_job_data(self, url):
        time.sleep(WORK_TERM_SLEEP)

        try:
            self.driver.get(url)

            job_data = {}

            try:
                job_name = self.driver.find_element(By.CSS_SELECTOR, "h3.job_name").text.strip()
            except Exception:
                job_name = "-"
            job_data["직업명"] = job_name
            
            # 관련직업
            try:
                related_jobs = self.driver.find_element(By.CSS_SELECTOR, "p.cont_txt").text.strip()
            except Exception:
                related_jobs = "-"
            job_data["관련직업"] = related_jobs

            # 관련학과
            try:
                related_major = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//dl[dt[text()='관련학과']]/dd/a"))
                ).text.strip()
            except Exception:
                related_major = "-"
            job_data["관련학과"] = related_major

            # 관련자격
            try:
                related_certificates = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//dl[dt[text()='관련자격']]/dd"))
                ).text.strip()
                related_certificates = [cert.strip() for cert in related_certificates.split(",")]
            except Exception:
                related_certificates = "-"
            job_data["관련자격"] = related_certificates

            # 하는일
            try:
                doing_tasks = self.driver.find_elements(By.CSS_SELECTOR, "ul.dash_ul li")
                doing_tasks = [task.text.strip() for task in doing_tasks]
            except Exception:
                doing_tasks = "-"
            job_data["하는일"] = doing_tasks

            # 적성
            try:
                aptitude = self.driver.find_elements(By.XPATH, "//dl[dt[text()='적성']]/dd")
                aptitude = [apt.text.strip() for apt in aptitude]
            except Exception:
                aptitude = "-"
            job_data["적성"] = aptitude

            # 흥미
            try:
                interests = self.driver.find_elements(By.XPATH, "//dl[dt[text()='흥미']]/dd")
                interests = [interest.text.strip() for interest in interests]
            except Exception:
                interests = "-"
            job_data["흥미"] = interests

            # 표준직업분류
            try:
                standard_classification = self.driver.find_element(By.XPATH, "//p[contains(text(),'표준직업분류')]").text.split(" : ")[1].strip()
            except Exception:
                standard_classification = "-"
            job_data["표준직업분류"] = standard_classification

            # 고용직업분류
            try:
                employment_classification = self.driver.find_element(By.XPATH, "//p[contains(text(),'고용직업분류')]").text.split(" : ")[1].strip()
            except Exception:
                employment_classification = "-"
            job_data["고용직업분류"] = employment_classification

            # 태그
            try:
                tags = self.driver.find_elements(By.CSS_SELECTOR, "ul.cont_tag li a")
                tags = [tag.text.strip() for tag in tags]
            except Exception:
                tags = "-"
            job_data["태그"] = tags

            return job_data

        except Exception as e:
            raise Exception(f"직업 세부 데이터 추출 중 에러: {e}")






    def get_job_links(self):
        try:
            search_tbody = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchTbody"))
            )
            links = search_tbody.find_elements(By.TAG_NAME, "a")
            href_list = [link.get_attribute("href") for link in links]
            return href_list

        except Exception as e:
            raise Exception(f"Error while getting job links: {e}")
        

    def input_keyword_and_set_list(self, search_keyword: str):
        try:
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="searchJobNm"][id="searchJobNm"]'))
            )
            search_input.click()
            search_input.send_keys(search_keyword)
            search_input.send_keys(Keys.ENTER)
            time.sleep(WORK_TERM_SLEEP)

            list_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='간편 리스트 보기']"))
            )
            list_button.click()
            time.sleep(WORK_TERM_SLEEP)

            list_count_drop_down = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='pageSize']"))
            )
            list_count_drop_down.click()
            time.sleep(WORK_TERM_SLEEP)


            list_30_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "option[value='30']"))
            )
            list_30_button.click()
            time.sleep(WORK_TERM_SLEEP)

            list_submit_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.list_apply"))
            )
            list_submit_button.click()
            time.sleep(WORK_TERM_SLEEP)


        except Exception as e:
            raise Exception(f"검색 창에 입력 후 리스트 세팅 중 에러: {e}")


    def save_to_json(self, data, filename):
        try:
            with open(f'extracted_json_data/careernet/{filename}', "w", encoding="utf-8") as f:
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