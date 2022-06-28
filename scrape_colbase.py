import argparse
import os
import time
import re
import urllib
from io import BytesIO
from zipfile import ZipFile

from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_binary
import pandas as pd
from tqdm import tqdm


def remove_html_tags(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def extract_from_table(table):
    dict = {}
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        key = row.find_element(By.TAG_NAME, "th").text
        value = row.find_element(By.TAG_NAME, "td").text
        dict[key] = remove_html_tags(value).replace("\n", " ")
    return dict


def get_zip_and_extract_all(zip_url, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    try:
        resp = urllib.request.urlopen(zip_url)
        zip_file = ZipFile(BytesIO(resp.read()))
        for info in zip_file.infolist():
            info.filename = info.orig_filename.encode('cp437').decode('cp932')
            if os.sep != "/" and os.sep in info.filename:
                info.filename = info.filename.replace(os.sep, "/")
            zip_file.extract(info, path=dest_dir)
    except Exception as e:
        print(e)
            
    
def build_url(keyword):
    base = "https://colbase.nich.go.jp/collection_items?"
    payload = {
        "locale": "ja",
        "limit": 100,
        "with_image_file": 1,
        "only_parent": 0,
        "free_word": keyword
    }
    url_query = base + urllib.parse.urlencode(payload)
    return url_query


def get_url_list(driver, keyword):

    driver.get(build_url(keyword))

    time.sleep(5)

    url_list = []
    more = True
    while(more):
        ul_items = driver.find_element(By.XPATH, "//div[@class='item-list show']/ul")
        list_items = ul_items.find_elements(By.CLASS_NAME, "item")
        for item in list_items:
            item_anchor = item.find_element(By.TAG_NAME, "a")
            url = item_anchor.get_attribute("href")
            url_list.append(url)
            
        next = driver.find_elements(By.CLASS_NAME, "next")
        if next:
            more = True
            next[0].find_element(By.TAG_NAME, "button").click()
            time.sleep(3)
        else:
            more = False
        
    return url_list


def download_files(driver, output_dir, url_list):
    os.makedirs(output_dir, exist_ok= True)
    df = pd.DataFrame(columns=['機関名', '機関管理番号', '名称', '説明', '種別',
                            '文化財指定', '員数', '作者', '時代世紀', '制作地', '出土地', 
                            '品質形状', '法量', '銘文等', '寄贈者', '所蔵者', '分類', 'URL'])

    for url in tqdm(url_list):
        driver.get(url)
        time.sleep(3)
        orgnanization = url.split("/")[4]
        name = driver.find_element(By.XPATH, "//div[@class='item-main']/h1").text
        descriptions = driver.find_elements(By.CLASS_NAME, "work-detail-text")
        table = driver.find_element(By.XPATH, "//div[@class='work-detail work-detail-info']/table")
        data = extract_from_table(table)
        download_div = driver.find_element(By.CLASS_NAME, "work-detail-download")
        download_url = download_div.find_element(By.CLASS_NAME, "link-box").get_attribute("href")
        data["機関名"] = orgnanization
        data["名称"] = name.replace("\n", " ")
        data["説明"] = " ".join([desc.text.replace("\n", " ") for desc in  descriptions])
        data["URL"] = url
        output_path = os.path.join(output_dir, data["機関名"], data["機関管理番号"])
        get_zip_and_extract_all(download_url, output_path)
        new_df = pd.DataFrame(data, index=[0])
        df = pd.concat([df, new_df], ignore_index=True)
        
    csv_path = os.path.join(output_dir, "download_list.csv")
    df.to_csv(csv_path, index=False, encoding="utf_8_sig")

def get_args():
    parser = argparse.ArgumentParser(description='Scrape Colbase')
    parser.add_argument('--keyword',
                        type=str,
                        required=True,
                        help='Search Keyword')
    parser.add_argument('--output_dir',
                        type=str,
                        default=".",
                        help='Output Directory')
    args = parser.parse_args()
    return args
    

if __name__ == "__main__":
    args = get_args()
    output_dir = os.path.join(args.output_dir, args.keyword)
    driver = webdriver.Chrome()
    url_list = get_url_list(driver, args.keyword)
    download_files(driver, output_dir, url_list)
    driver.close()

