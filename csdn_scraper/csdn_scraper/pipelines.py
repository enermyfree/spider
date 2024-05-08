import pymysql
from scrapy.utils.project import get_project_settings

class MySQLPipeline(object):
    def __init__(self):
        self.settings = get_project_settings()

    def open_spider(self, spider):
        self.connection = pymysql.connect(
            host=self.settings.get('MYSQL_HOST'),
            user=self.settings.get('MYSQL_USER'),
            password=self.settings.get('MYSQL_PASSWORD'),
            db=self.settings.get('MYSQL_DBNAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        # 检查表是否存在
        table_exists_query = "SHOW TABLES LIKE %s"
        self.cursor.execute(table_exists_query, (item['search_data'],))
        table_exists = self.cursor.fetchone()

        # 如果表不存在，则创建新表
        if not table_exists:
            create_table_query = "CREATE TABLE {} (id INT AUTO_INCREMENT PRIMARY KEY, article_url VARCHAR(255), article_title VARCHAR(255), article_content TEXT)".format(
                item['search_data'])
            self.cursor.execute(create_table_query)
            self.connection.commit()

        # 插入数据
        sql = "INSERT INTO {} (article_url, article_title, article_content) VALUES (%s, %s, %s)".format(
            item['search_data'])
        self.cursor.execute(sql,
                            (item['article_url'], item['article_title'], item['article_content']))
        self.connection.commit()

        return item



