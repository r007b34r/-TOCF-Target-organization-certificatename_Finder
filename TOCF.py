import requests
import json
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm

class WikipediaScraper:
    # WikipediaScraper类用于从维基百科页面中提取英文名称，并在crt.sh上搜索相关数据

    BASE_URL = "https://zh.wikipedia.org/wiki/"  # 维基百科页面的基础URL
    CRT_SH_URL = "https://crt.sh/?o="  # crt.sh的搜索URL
    LOG_FILE = "scraper.log"  # 日志文件路径

    def __init__(self):
        # 初始化类实例，设置日志记录器
        self.logger = self.setup_logger()

    def setup_logger(self):
        # 设置日志记录器的配置
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 将日志记录到文件
        file_handler = logging.FileHandler(self.LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def fetch_page_content(self, target_name):
        # 获取维基百科页面内容
        search_url = f"{self.BASE_URL}{target_name}"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            # 处理请求异常并记录到日志
            self.logger.error(f"请求错误：{str(e)}")
            raise

    def extract_english_name(self, page_content):
        # 从页面内容中提取英文名称
        soup = BeautifulSoup(page_content, 'html.parser')
        english_name_element = soup.find('span', {'lang': 'en'})
        return english_name_element.text if english_name_element else None

    def process_english_name(self, english_name):
        # 处理英文名称，只保留第一个单词
        if english_name:
            return english_name.split()[0]
        else:
            return None

    def search_crt_sh(self, keyword):
        # 在crt.sh上搜索关键词
        try:
            crt_sh_response = requests.get(f"{self.CRT_SH_URL}{keyword}&output=json")
            crt_sh_response.raise_for_status()
            return crt_sh_response.text
        except requests.exceptions.RequestException as e:
            # 处理请求异常并记录到日志
            self.logger.error(f"请求错误：{str(e)}")
            raise

    def parse_crt_sh_data(self, json_data):
        # 解析crt.sh的JSON数据
        try:
            crt_sh_json = json.loads(json_data)
            # 使用小写和去除空格进行比较
            name_values = {entry['name_value'].strip().lower() for entry in crt_sh_json}
            return name_values
        except json.JSONDecodeError as e:
            # 处理JSON解析错误并记录到日志
            self.logger.error(f"JSON解析错误：{str(e)}")
            raise

    def scrape_and_print_english_name(self, target_name):
        try:
            page_content = self.fetch_page_content(target_name)
            english_name = self.extract_english_name(page_content)
            processed_english_name = self.process_english_name(english_name)

            if processed_english_name:
                print(f"原始英文名称：{english_name}")
                print(f"处理后的英文名称：{processed_english_name}")

                crt_sh_data = self.search_crt_sh(processed_english_name)
                name_values = self.parse_crt_sh_data(crt_sh_data)

                self.write_name_list_to_file(name_values)
                self.print_name_list(name_values)
            else:
                print("未找到英文名称.")
        except Exception as e:
            # 处理其他异常
            print(f"发生错误：{str(e)}")

    def write_name_list_to_file(self, name_values):
        with open("Target-organization-certificate-name-list.txt", "w") as file:
            name_set = set(name_values)
            for name in name_set:
                file.write(name + '\n')

    def print_name_list(self, name_values):
        print("采集的英文名称：")
        for name in name_values:
            print(name)

def main():
    target_name = input("请输入目标中文名称：")
    scraper = WikipediaScraper()
    scraper.scrape_and_print_english_name(target_name)

if __name__ == "__main__":
    main()
