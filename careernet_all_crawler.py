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

    def run(self):
        
        try:
            self.driver.get(self.url)
            time.sleep(WORK_TERM_SLEEP)
            self.set_job_list()
            
            all_job_links = []

            for _ in range(1, 20):
                job_links = self.get_job_links()
                all_job_links.extend(job_links)
                self.move_to_next_page()
                    
            print(f'all_job_links: {all_job_links}')

            job_details = []

            for job_link in all_job_links:
                self.driver.get(job_link)
                print(f'job_link: {job_link}')
                time.sleep(WORK_TERM_SLEEP)
                extracted_job_data = self.extract_job_data(job_link)

                job_details.append(extracted_job_data)

                self.save_to_json(job_details, "careernet_job_data.json")

        except Exception as e:
            raise Exception(f"크롤링 실행 중 에러: {e}")


    def move_to_next_page(self):
        try:
            pagination_buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"div#pagination.pagination"))
            )

            strong_number = WebDriverWait(pagination_buttons, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"strong"))
            )

            if int(strong_number.text) == 10:
                next_page_button = WebDriverWait(pagination_buttons, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"a.pageBtn img[alt='다음']"))
                )
                next_page_button.click()

            else:
                next_number_button = WebDriverWait(pagination_buttons, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'a[onclick="fn_page({int(strong_number.text) + 1});return false; "]'))
                )
                next_number_button.click()
            time.sleep(WORK_TERM_SLEEP)
        except Exception:
            pass

    def extract_job_data(self, url):
        time.sleep(WORK_TERM_SLEEP)

        try:
            self.driver.get(url)

            job_data = {}

            try:
                job_name = self.driver.find_element(By.CSS_SELECTOR, "h3.job_name").text.strip()
            except Exception:
                job_name = "N/A"
            job_data["직업명"] = job_name
            
            try:
                container = self.driver.find_element(
                    By.XPATH,
                    "//div[@class='cont'][h4[text()='관련직업명']]"
                )
                # p.cont_txt 요소 직접 찾기
                related_jobs_element = container.find_element(
                    By.CSS_SELECTOR,
                    "p.cont_txt"
                )
                # 텍스트 추출
                job_data["관련직업"] = related_jobs_element.text.strip()
            except Exception:
                job_data["관련직업"] = "N/A"

            container = self.driver.find_element(
                By.XPATH,
                "//div[@class='cont'][h4[text()='관련학과 및 관련자격']]"
            )

            # 2) 관련학과: 첫 번째 dl 내 a 태그들
            try:
                major_elements = container.find_elements(
                    By.CSS_SELECTOR,
                    "dl:nth-of-type(1) dd a"
                )
                related_majors = [m.text.strip() for m in major_elements]
                job_data["관련학과"] = related_majors
            except Exception:
                job_data["관련학과"] = "N/A"


            # 3) 관련자격: 두 번째 dl 내 dd 텍스트 (쉼표로 나눌 수도 있음)
            try:
                cert_dd = container.find_element(
                    By.CSS_SELECTOR,
                    "dl:nth-of-type(2) dd"
                )
                related_certificates = cert_dd.text.strip()
                job_data["관련자격"] = related_certificates
            except Exception:
                job_data["관련자격"] = "N/A"

            # 하는일
            try:
                doing_tasks = self.driver.find_elements(By.CSS_SELECTOR, "ul.dash_ul li")
                doing_tasks = [task.text.strip() for task in doing_tasks]
            except Exception:
                doing_tasks = "N/A"
            job_data["하는일"] = doing_tasks

            # 적성
            try:
                aptitude = self.driver.find_elements(By.XPATH, "//dl[dt[text()='적성']]/dd")
                aptitude = [apt.text.strip() for apt in aptitude]
            except Exception:
                aptitude = "N/A"
            job_data["적성"] = aptitude

            # 흥미
            try:
                interests = self.driver.find_elements(By.XPATH, "//dl[dt[text()='흥미']]/dd")
                interests = [interest.text.strip() for interest in interests]
            except Exception:
                interests = "N/A"
            job_data["흥미"] = interests

            # 표준직업분류
            try:
                standard_classification = self.driver.find_element(By.XPATH, "//p[contains(text(),'표준직업분류')]").text.split(" : ")[1].strip()
            except Exception:
                standard_classification = "N/A"
            job_data["표준직업분류"] = standard_classification

            # 고용직업분류
            try:
                employment_classification = self.driver.find_element(By.XPATH, "//p[contains(text(),'고용직업분류')]").text.split(" : ")[1].strip()
            except Exception:
                employment_classification = "N/A"
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
        

    def set_job_list(self):
        try:
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
            with open(f'extracted_json_data/{filename}', "w", encoding="utf-8") as f:
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