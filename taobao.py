import requests
import json
import datetime
import random
from fake_useragent import UserAgent
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


class tb_spider(object):
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--headless')
        self.url = 'https://login.taobao.com/member/login.jhtml'
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.get(self.url)
        self.ua = UserAgent()
        self.wait = WebDriverWait(self.browser, 10)
        self.search_goods_name = goods_name
        self.file = open('C:\\Users\\NB70TK1\\PycharmProjects\\taobao\\data\\商品-{}-时间{}.csv'.format(goods_name, datetime.datetime.now().strftime('%m-%d-%H-%M-%S')), 'w+', encoding='utf-8')
        self.file.write('产品名称,产品价格,产地,销量,卖家,是否是金牌卖家,是否是公益宝贝,是否属于天猫,物流评分,描述相符评分,服务评分,总评分,卖家信誉等级,评论数量,评论网址,产品详情,店铺链接\n')

    def webdriverlogin_getcookies(self):
        try:
            self.browser.find_element_by_partial_link_text('密码登录').click()
            sleep(1)
            self.browser.find_element_by_partial_link_text('微博登录').click()
            sleep(1)
            self.browser.find_element_by_css_selector('#pl_login_logged > div > div:nth-child(2) > div > input').send_keys(username)
            sleep(1)
            self.browser.find_element_by_css_selector('#pl_login_logged > div > div:nth-child(3) > div > input').send_keys(passwd)
            sleep(1)
            self.browser.find_element_by_css_selector('#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a').click()
            print('浏览器操作成功，等待校验登录状态...\n')
        except BaseException:
            print('浏览器操作失败')
        try:
            self.username_test = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a')))
            if self.username_test.text == username_tb:
                print('登录成功！\n')
                self.raw_cookies = self.browser.get_cookies()
                if self.raw_cookies:
                    print('获取cookies成功！\n')
                else:
                    print('获取cookies失败！\n')
            self.browser.quit()
        except BaseException:
            print('登录失败！')

    def transfer_cookies(self):
        self.useful_cookies = {}
        for i in self.raw_cookies:
            self.useful_cookies[i['name']] = i['value']

    def init_requests_session(self):
        self.re_tb = requests.session()
        #print('正在使用以下cookies:\n{}'.format(str(self.useful_cookies)))
        self.re_tb.cookies.update(self.useful_cookies)
        print('cookies传递成功')

    def crawl_search_result(self):
        for i in range(0, needed_pages_num*44, 44):
            self.search_url = 'https://s.taobao.com/search?q={}&search_type=item&imgfile=&js=1&suggest_query=&source=suggest&s={}'.format(goods_name, i)
            self.head = {'UserAgent': self.ua.random}
            self.re_tb.headers.update(self.head)
            self.response = self.re_tb.get(self.search_url)
            if self.response.status_code == 200:
                self.page = self.response.text
                self.parse_data(self.page, i/44)
                sleep(10.1)
            else:
                print('请求异常：{}\n'.format(self.response.status_code))

    def parse_data(self, page_content, currently_page):
        try:
            self.json_begin = page_content.find('g_page_config = ') + len('g_page_config = ')
            self.json_end = page_content.find('"shopcardOff":true}') + len('"shopcardOff":true}')
            self.json_data = json.loads(page_content[self.json_begin:self.json_end+1])
        except BaseException:
            print(self.page)
            raise Exception('json解析错误！可能遭遇反爬机制')

        try:
            for i in self.json_data['mods']['itemlist']['data']['auctions']:
                product_name = i['raw_title']
                product_price = i['view_price']
                product_detail_url = 'https:' + i['detail_url']
                product_local = i['item_loc']
                if str(i).find('view_sales') != -1:
                    product_sales = i['view_sales']
                else:
                    product_sales = 'unknow'
                product_comment_count = i['comment_count']
                product_seller = i['nick']
                if str(i).find('shopcard') != -1:
                    product_rate_delivery = i['shopcard']['delivery'][0]/100
                    product_rate_description = i['shopcard']['description'][0]/100
                    product_rate_service = i['shopcard']['service'][0]/100
                    if str(i).find('totalRate') != -1:
                        total_rate = i['shopcard']['totalRate']
                    else:
                        total_rate = 'unknow'
                    if str(i).find('sellerCredit') != -1:
                        seller_Credit = i['shopcard']['sellerCredit']
                    else:
                        seller_Credit = 'unknow'
                    if i['shopcard']['isTmall'] == False:
                        product_is_Tmall = 'no'
                    else:
                        product_is_Tmall = 'yes'
                else:
                    product_is_Tmall = 'unknow'
                product_comment = 'https:' + i['comment_url']
                product_shop_link = 'https:' + i['shopLink']
                if str(i['icon']).find('icon-fest-gongyibaobei') != -1:
                    product_is_commonweal_product = 'yes'
                else:
                    product_is_commonweal_product = 'no'
                if str(i['icon']).find('icon-service-jinpaimaijia') != -1:
                    product_is_Gold_seller = 'yes'
                else:
                    product_is_commonweal_product = 'no'
                    product_is_Gold_seller = 'no'
                self.file.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(product_name, product_price, product_local, product_sales, product_seller, product_is_Gold_seller, product_is_commonweal_product, product_is_Tmall, product_rate_delivery, product_rate_description, product_rate_service, total_rate, seller_Credit, product_comment_count, product_comment, product_detail_url, product_shop_link))
            print('第{}页解析成功'.format(int(currently_page)+1))
        except  AttributeError:
            print('第{}页解析失败！'.format(currently_page))
            pass


if __name__ == '__main__':
    username_tb = input('请输入你的淘宝账号用户名\n')
    username = input('请输入你的微博账号\n')
    passwd = input('请输入你的微博密码\n')
    goods_name = input('请输入要搜索的商品名称\n')
    needed_pages_num = int(input('请输入需要爬取的页面数\n'))

    begin_time = datetime.datetime.now()
    spider = tb_spider()
    spider.webdriverlogin_getcookies()
    spider.transfer_cookies()
    spider.init_requests_session()
    spider.crawl_search_result()
    spider.file.close()
    course_time =(datetime.datetime.now() - begin_time).seconds
    print('运行完毕，共耗时{}分{}秒'.format(course_time//60, course_time%60))

test = {}
