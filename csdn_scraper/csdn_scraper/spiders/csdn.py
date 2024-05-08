import csv
import os
import re


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import scrapy
from scrapy_splash import SplashRequest

from ..items import CsdnScraperItem


class CsdnSpider(scrapy.Spider):
    name = 'csdn'
    allowed_domains = ['csdn.net']

    def read_search_urls(self):
        current_file_path = os.path.abspath(__file__)
        # 获取当前脚本文件所在的目录
        current_dir = os.path.dirname(current_file_path)
        # 构造searchData.csv文件的绝对路径
        csv_file_path = os.path.join(current_dir, 'searchData.csv')
        # csv_file_path = 'searchData.csv'
        search_datas = []
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                search_datas.append(row[0])
        return search_datas


    def scrape_and_store_seach_data(self, search_data):
        # 配置 ChromeOptions
        options = Options()
        options.add_argument("--disable-javascript")
        # 如果需要的话添加其他选项
        # options.add_argument("--headless")  # 无界面模式
        # 创建 ChromeDriver 服务，Service 要指定 chromedriver 的位置
        service = Service('/Users/enermyfree/Downloads/chromedriver-mac-arm64/chromedriver')

        # 创建浏览器驱动对象
        driver = webdriver.Chrome(service=service, options=options)

        # 存储文章信息的数组
        articles_data = []

        try:
            # 打开目标网页
            driver.get('https://so.csdn.net/so/search?q=' + search_data)

            # 滚动到页面底部以加载全部内容
            last_height = driver.execute_script("return document.body.scrollHeight")

            # 初始化计数器
            click_count = 0
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    try:
                        load_more_button = driver.find_element(By.XPATH, "//div[@class='so-load-data']")
                        if click_count == 0:
                            try:
                                close_button = driver.find_element(By.XPATH,
                                                                   "//img[contains(@style, 'position: absolute')]")
                                close_button.click()
                            except NoSuchElementException:
                                print("The close button was not found on the page.")

                        load_more_button.click()
                        time.sleep(3)
                        click_count += 1

                        if click_count == 1:
                            break
                    except (NoSuchElementException, ElementClickInterceptedException):
                        break
                last_height = new_height

            # 使用XPath查找所有符合条件的元素
            elements = driver.find_elements(By.XPATH, '//h3[@class="title substr"]/a')

            # 遍历元素列表并收集链接和文本
            for element in elements:
                href_value = element.get_attribute('href')
                text_value = element.text
                # 截断链接的"?"之后的部分
                truncated_href_value = href_value.split('?')[0]

                # 将数据添加到数组中
                articles_data.append((truncated_href_value, text_value))

        finally:
            # 关闭浏览器
            driver.quit()

        return articles_data

    def start_requests(self):
        search_datas = self.read_search_urls()
        for search_data in search_datas:
            articles_data = self.scrape_and_store_seach_data(search_data)
            for article in articles_data:
                url, title = article  # 解包每个元组，获取链接和标题
                item = CsdnScraperItem(
                    article_url=url,
                    article_title=title,
                    article_content='',
                    search_data=search_data  # 设置 search_data 字段为当前搜索数据
                )
                yield SplashRequest(
                    url,
                    self.parse,
                    args={'wait': 0.5},
                    meta={
                        'item': item
                    }
                )

    def parse(self, response):
        # 定位到class为"blog-content-box"的<div>标签
        content = response.xpath('//div[contains(@class, "blog-content-box")]').extract_first()
        # 将提取到的内容合并成一个字符串
        content_text = ''.join(content)
        content_text = re.sub(r'<.*?>', '', content_text)

        # 获取传递给parse的Item对象
        item = response.meta['item']
        # 设置 article_content 字段的值
        item['article_content'] = content_text
        yield item






