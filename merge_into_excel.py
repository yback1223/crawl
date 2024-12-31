import json
import pandas as pd
import os

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def process_careernet(data):
    """Process careernet JSON data and return a list of rows."""
    rows = []
    for item in data:
        row = {
            "직업명": item.get("직업명", ""),
            "관련직업": item.get("관련직업", ""),
            "관련학과": item.get("관련학과", ""),
            "관련자격_면허": item.get("관련자격", ""),
            "수행직무/하는일": " ".join(item.get("하는일", [])),
            "적성 및 흥미": " ".join(item.get("적성", []) + item.get("흥미", [])),
            "표준직업분류": item.get("표준직업분류", ""),
            "고용직업분류": item.get("고용직업분류", ""),
            "태그": ", ".join(item.get("태그", [])),
            "출처": "커리어넷",
        }
        rows.append(row)
    return rows

def process_worknet(data):
    """Process worknet JSON data and return a list of rows."""
    rows = []
    for item in data:
        detail = item.get("detail", {})
        row = {
            "직업명": item.get("직업명", ""),
            "고용직업분류직업분류_1": item.get("고용직업분류직업분류_1", ""),
            "고용직업분류직업분류_2": item.get("고용직업분류직업분류_2", ""),
            "고용직업분류직업분류_3": item.get("고용직업분류직업분류_3", ""),
            "고용직업분류직업분류_3_설명": item.get("고용직업분류직업분류_3_설명", ""),
            "직업설명": item.get("직업설명", ""),
            "수행직무/하는일": item.get("수행직무/하는일", ""),
            "정규교육": detail.get("정규교육", ""),
            "숙련기간": detail.get("숙련기간", ""),
            "핵심능력": detail.get("직무기능", ""),
            "작업강도": detail.get("작업강도", ""),
            "육체활동": detail.get("육체활동", ""),
            "작업장소": detail.get("작업장소", ""),
            "작업환경": detail.get("작업환경", ""),
            "유사명칭": detail.get("유사명칭", ""),
            "관련직업": detail.get("관련직업", ""),
            "관련자격_면허": detail.get("자격/면허", ""),
            "고용직업분류": detail.get("고용직업분류", ""),
            "표준직업분류": detail.get("표준직업분류", ""),
            "표준산업분류": detail.get("표준산업분류", ""),
            "조사연도": detail.get("조사연도", ""),
            "비고": detail.get("비고", ""),
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
