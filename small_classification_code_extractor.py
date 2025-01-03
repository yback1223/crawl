import pandas as pd
from driver import Driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import clipboard, time
import math, random, json, re

class SmallCodeExtractor:
    def __init__(self):
        self.driver = Driver().set_chrome()
        self.actions = ActionChains(self.driver)
        self.url = "https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobCl.do?pageType=jobDicSrchByJobCl&"

    def small_classification_code_extractor(self):
        # Load the Excel file
        file_path = "my_small_code.xlsx"  # Replace with your file path
        df = pd.read_excel(file_path)

        # Extract the '소분류코드' column
        subcategory_codes = [str(code).strip() for code in df['소분류코드'].dropna().unique() if len(str(code).strip()) > 0]

        # subcategory_codes = ['111', '112', '121', '122', '131', '132', '133', '134', '135', '139', '141', '149', '151', '152', 
        #                      '153', '159', '211', '212', '213', '221', '222', '223', '224', '225', '231', '232', '233', '234', 
        #                      '235', '236', '237', '238', '239', '241', '242', '243', '244', '245', '246', '247', '248', '251', 
        #                      '252', '253', '254', '259', '261', '262', '271', '272', '273', '274', '281', '282', '283', '284', 
        #                      '285', '286', '287', '288', '311', '312', '313', '314', '320', '330', '391', '392', '399', '411', 
        #                      '412', '421', '422', '423', '429', '431', '432', '441', '442', '510', '521', '522', '531', '532', 
        #                      '611', '612', '613', '620', '630', '710', '721', '722', '730', '741', '742', '743', '751', '752', 
        #                      '753', '761', '762', '771', '772', '781', '782', '783', '784', '791', '792', '799', '811', '812', 
        #                      '819', '821', '822', '823', '831', '832', '841', '842', '843', '851', '852', '853', '854', '855', 
        #                      '861', '862', '863', '864', '871', '872', '873', '874', '875', '876', '881', '882', '891', '892', 
        #                      '899', '910', '921', '922', '930', '941', '942', '951', '952', '953', '991', '992', '999', 'A01', 
        #                      'A02', 'A09']

        # Display the result
        print("소분류코드 values:", subcategory_codes)

        return subcategory_codes

    def run(self):
        try:
            small_codes: list[str] = self.small_classification_code_extractor()

            for code in small_codes:
                self.driver.get(f"{self.url}choiceCode={code}&choiceLevel=3")
                time.sleep(1)

                selected_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.btn.full.bd-no.on")
                selected_texts = [button.text.strip() for button in selected_buttons]

                standard_job_classification_1 = selected_texts[0]
                standard_job_classification_2 = selected_texts[1]
                standard_job_classification_3 = selected_texts[2]

                # 여러 tbody 요소를 가져옴
                tbodies = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody"))
                )

                link_urls = []
                for tbody in tbodies:
                    links = tbody.find_elements(By.CSS_SELECTOR, "a")
                    link_urls.extend([link.get_attribute("href") for link in links])

                job_data = []

                for url in link_urls:
                    job_detail = self.crawl_standard_job_classification_detail(url)

                    recruit_job_classification = job_detail['detail'].get("고용직업분류", "N/A")
                    recruit_job_classification_code = recruit_job_classification[recruit_job_classification.find("[") + 1:recruit_job_classification.find("]")]
                    standard_industry_classification = job_detail['detail'].get("표준산업분류", "N/A")
                    standard_industry_classification_code = standard_industry_classification[standard_industry_classification.find("[") + 1:standard_industry_classification.find("]")]

                    standard_job_classification = {
                        "표준직업분류_1": standard_job_classification_1,
                        "표준직업분류_2": standard_job_classification_2,
                        "표준직업분류_3": standard_job_classification_3
                    }

                    if recruit_job_classification_code:
                        recruit_job_classification_codes = self.crawl_recruit_job_classification_codes(code=recruit_job_classification_code)
                    else:
                        recruit_job_classification_codes = {}

                    if standard_industry_classification_code:
                        standard_industry_classification_codes = self.crawl_standard_industry_classification_codes(code=standard_industry_classification_code)
                    else:
                        standard_industry_classification_codes = {}

                    job_detail["표준직업분류"] = standard_job_classification
                    job_detail["고용직업분류"] = recruit_job_classification_codes
                    job_detail["표준산업분류"] = standard_industry_classification_codes

                    job_data.append(job_detail)

                self.save_to_json(job_data, f"extracted_json_data/{code}.json")
        except Exception as e:
            print(f"데이터 수집 중 에러: {e}")


    def save_to_json(self, data, filename):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"데이터가 {filename} 파일로 저장되었습니다.")
        except Exception as e:
            print(f"JSON 저장 중 에러: {e}")

    def refactor_text(self, input_text):
        input_text = input_text.replace(" ", "")
        temp_output = re.sub(r"\((.*?)\)", lambda m: "(" + m.group(1).replace(",", "|") + ")", input_text)

        # Replace "," outside parentheses with a space
        temp_output = re.sub(r",", " ", temp_output)

        # Restore the "," inside parentheses
        output_text = re.sub(r"\((.*?)\)", lambda m: "(" + m.group(1).replace("|", ",") + ")", temp_output)
        return output_text

    def crawl_standard_job_classification_detail(self, url):
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
                    details[key] = "N/A" if value == '-' or value == '' else value
                    if details[key] == "N/A":
                        continue
                    if key == "직무기능":
                        details[key] = details[key].replace(" ", "").replace("/", " ")
                    if key == "유사명칭" or key == "관련직업" or key == "자격/면허":
                        details[key] = self.refactor_text(details[key])

            return {
                "직업명": job_name,
                "직업설명": outline,
                "수행직무/하는일": duty,
                "detail": details,
            }
        except Exception as e:
            print(f"Error while processing {url}: {e}")
            return None
        

    def crawl_recruit_job_classification_codes(self, code):
        if not any(one_code.isdigit() for one_code in code):
            return {
                "고용직업분류_1": "N/A",
                "고용직업분류_2": "N/A",
                "고용직업분류_3": "N/A"
            }
        url = f"https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByJobmap.do?pageType=jobDicSrchByJobmap&choiceCode={code}&choiceLevel=4&subJobCode={code}"
        try:
            self.driver.get(url)
            time.sleep(1)

            selected_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.btn.full.bd-no.on")

            selected_texts = [button.text.strip() for button in selected_buttons]

            recruit_job_classification_1 = selected_texts[0]
            recruit_job_classification_2 = selected_texts[1]
            recruit_job_classification_3 = selected_texts[2]

            return {
                "고용직업분류_1": recruit_job_classification_1,
                "고용직업분류_2": recruit_job_classification_2,
                "고용직업분류_3": recruit_job_classification_3
            }
        except Exception as e:
            print(f"Error while processing {url}: {e}")

    def crawl_standard_industry_classification_codes(self, code):
        if not any(one_code.isdigit() for one_code in code):
            return {
                "표준산업분류_1": "N/A",
                "표준산업분류_2": "N/A",
                "표준산업분류_3": "N/A"
            }
        url = f"https://www.work.go.kr/consltJobCarpa/srch/jobDic/jobDicSrchByIndCl.do?pageType=jobDicSrchByIndCl&choiceCode={code}&choiceLevel=4&subJobCode={code}"
        try:
            self.driver.get(url)
            time.sleep(1)

            selected_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.btn.full.bd-no.on")

            selected_texts = [button.text.strip() for button in selected_buttons]

            standard_industry_classification_1 = selected_texts[0]
            standard_industry_classification_2 = selected_texts[1]
            standard_industry_classification_3 = selected_texts[2]

            return {
                "표준산업분류_1": standard_industry_classification_1,
                "표준산업분류_2": standard_industry_classification_2,
                "표준산업분류_3": standard_industry_classification_3
            }
        except Exception as e:
            print(f"Error while processing {url}: {e}")


if __name__ == "__main__":
    crawler = SmallCodeExtractor()
    crawler.run()

