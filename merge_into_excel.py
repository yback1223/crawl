import json
import pandas as pd
import os

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def process_careernet(data):

    rows = []
    for item in data:
        related_jobs = item.get("관련직업", "N/A")
        if related_jobs != "N/A":
            processed_jobs = related_jobs.replace(" ", "").replace(",", " ").strip()
        else:  # 리스트가 아닌 경우 기본값 사용
            processed_jobs = "N/A"

        related_majors = item.get("관련학과", "N/A")
        if isinstance(related_majors, list):  # 리스트일 경우만 처리
            processed_majors = " ".join([major.strip().replace(" ", "") for major in related_majors])
        else:  # 리스트가 아닌 경우 기본값 사용
            processed_majors = "N/A"

        related_certs = item.get("관련자격", "N/A")
        if related_certs != "N/A":
            processed_certs = related_certs.replace(" ", "").replace(",", " ").strip()
        else:
            processed_certs = "N/A"

        standard_job_classification = item.get("표준직업분류", "N/A")
        if "(세분류" in standard_job_classification:
            extracted_code = standard_job_classification[
                standard_job_classification.find("(세분류") + len("(세분류") + 1:
                -1
            ].strip()
        else:
            extracted_code = "N/A"  # "(세분류"가 없을 경우 기본값

        recruit_job_classification = item.get("표준직업분류", "N/A")
        if "(세분류" in recruit_job_classification:
            extracted_recruit_code = recruit_job_classification[
                recruit_job_classification.find("(세분류") + len("(세분류") + 1:
                -1
            ].strip()
        else:
            extracted_recruit_code = "N/A"  # "(세분류"가 없을 경우 기본값

        row = {
            "직업명": item.get("직업명", "N/A").replace(" ", ""),
            "관련직업": processed_jobs,
            "관련학과": processed_majors,
            "관련자격_면허": processed_certs,
            "수행직무/하는일": " ".join(item.get("하는일", [])),
            "적성 및 흥미": " ".join(item.get("적성", []) + item.get("흥미", [])),
            "표준직업분류": extracted_code,
            "고용직업분류": extracted_recruit_code,
            "태그": ", ".join(item.get("태그", [])),
            "출처": "커리어넷",
        }
        rows.append(row)
    return rows

def process_worknet(data):
    rows = []
    for item in data:
        detail = item.get("detail", {})

        related_abilities = detail.get("직무기능", "N/A")
        if related_abilities != "N/A":
            processed_abilities = related_abilities.replace(" ", "").replace("/", " ").strip()
        else:
            processed_abilities = "N/A"

        related_names = detail.get("유사명칭", "N/A")
        if related_names != "N/A":
            processed_names = related_names.replace(" ", "").replace(",", " ").strip()
        else:
            processed_names = "N/A"

        related_jobs = detail.get("관련직업", "N/A")
        if related_jobs != "N/A":
            processed_jobs = related_jobs.replace(" ", "").replace(",", " ").strip()
        else:
            processed_jobs = "N/A"

        related_certs = detail.get("자격/면허", "N/A")
        if related_certs != "N/A":
            processed_certs = related_certs.replace(" ", "").replace(",", " ").strip()
        else:
            processed_certs = "N/A"

        standard_job_classification = detail.get("표준직업분류", "N/A")
        if "[" in standard_job_classification:
            extracted_code = standard_job_classification[1:standard_job_classification.find("]")].strip()
        else:
            extracted_code = "N/A"

        recruit_job_classification = detail.get("고용직업분류", "N/A")
        if "[" in recruit_job_classification:
            extracted_recruit_code = recruit_job_classification[1:recruit_job_classification.find("]")].strip()
        else:
            extracted_recruit_code = "N/A"

        industry_classification = detail.get("표준산업분류", "N/A")
        if "[" in industry_classification:
            extracted_industry_code = industry_classification[1:industry_classification.find("]")].strip()
        else:
            extracted_industry_code = "N/A"

        row = {
            "직업명": item.get("직업명", "N/A"),
            "고용직업분류직업분류_1": item.get("고용직업분류직업분류_1", "N/A"),
            "고용직업분류직업분류_2": item.get("고용직업분류직업분류_2", "N/A"),
            "고용직업분류직업분류_3": item.get("고용직업분류직업분류_3", "N/A"),
            "고용직업분류직업분류_3_설명": item.get("고용직업분류직업분류_3_설명", "N/A"),
            "직업설명": item.get("직업설명", "N/A"),
            "수행직무/하는일": item.get("수행직무/하는일", "N/A"),
            "정규교육": detail.get("정규교육", "N/A"),
            "숙련기간": detail.get("숙련기간", "N/A"),
            "핵심능력": processed_abilities,
            "작업강도": detail.get("작업강도", "N/A"),
            "육체활동": detail.get("육체활동", "N/A"),
            "작업장소": detail.get("작업장소", "N/A"),
            "작업환경": detail.get("작업환경", "N/A"),
            "유사명칭": processed_names,
            "관련직업": processed_jobs,
            "관련자격_면허": processed_certs,
            "고용직업분류": extracted_code,
            "표준직업분류": extracted_recruit_code,
            "표준산업분류": extracted_industry_code,
            "조사연도": detail.get("조사연도", "N/A"),
            "비고": detail.get("비고", "N/A"),
            "출처": "워크넷"
        }
        rows.append(row)
    return rows

def save_to_excel(rows, file_name):
    """Save rows to an Excel file."""
    columns = [
        "직업명", "고용직업분류직업분류_1", "고용직업분류직업분류_2", "고용직업분류직업분류_3", "고용직업분류직업분류_3_설명",
        "표준직업분류_1", "표준직업분류_2", "표준직업분류_3", "표준산업분류_1", "표준산업분류_2", "표준산업분류_3",
        "직업설명", "수행직무/하는일", "정규교육", "숙련기간", "직무기능", "핵심능력", "적성 및 흥미", "작업강도",
        "육체활동", "작업장소", "작업환경", "유사명칭", "관련직업", "관련학과", "관련자격_면허", "고용직업분류",
        "표준직업분류", "표준산업분류", "조사연도", "비고", "태그", "출처"
    ]

    try:
        df = pd.DataFrame(rows, columns=columns)
        if df.empty:
            print("No data to save. Exiting...")
            return
        df.to_excel(file_name, index=False)
        print(f"Excel file saved as {file_name}")
    except Exception as e:
        print(f"Error saving Excel file: {e}")



def process_folder(folder_path, process_function):
    """Process all JSON files in a folder."""
    rows = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")  # 디버깅용
            data = load_json(file_path)
            rows.extend(process_function(data))
    return rows


def main():
    # Process careernet folder
    careernet_folder = "extracted_json_data/careernet"
    worknet_folder = "extracted_json_data/worknet"

    careernet_rows = process_folder(careernet_folder, process_careernet)
    worknet_rows = process_folder(worknet_folder, process_worknet)

    # Combine rows
    all_rows = careernet_rows + worknet_rows
    # Save to Excel
    save_to_excel(all_rows, "./yback_data_excel.xlsx")

if __name__ == "__main__":
    main()
