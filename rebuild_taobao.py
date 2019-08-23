import json
import datetime
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
        self.search_goods_name = goods_name
        self.count_success = 0
        self.count_fail = 0
        self.count_re_try = 0
        self.re_try_wait_time = 0
        self.file = open('C:\\Users\\NB70TK1\\PycharmProjects\\taobao\\data\\商品-{}-时间{}.csv'.format(goods_name, datetime.datetime.now().strftime(
                                                                                                        '%m-%d-%H-%M-%S')),
                         'w+', encoding='utf-8')
        self.file.write('产品名称,产品价格,产地,销量,卖家,是否是金牌卖家,是否是公益宝贝,是否属于天猫,物流评分,描述相符评分,服务评分,总评分,卖家信誉等级,评论数量,评论网址,产品详情,店铺链接\n')

    def webdriver_login(self):
        try:
            self.browser = webdriver.Chrome(options=self.options)
            self.browser.get(self.url)
            self.browser.find_element_by_partial_link_text('密码登录').click()
            sleep(1)
            self.browser.find_element_by_partial_link_text('微博登录').click()
            sleep(1)
            self.browser.find_element_by_css_selector(
                '#pl_login_logged > div > div:nth-child(2) > div > input').send_keys(username)
            sleep(1)
            self.browser.find_element_by_css_selector(
                '#pl_login_logged > div > div:nth-child(3) > div > input').send_keys(passwd)
            sleep(1)
            self.browser.find_element_by_css_selector(
                '#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a').click()
            print('浏览器操作成功，等待校验登录状态...\n')
        except BaseException:
            raise Exception('浏览器操作失败')
        try:
            self.wait = WebDriverWait(self.browser, 10)
            self.username_test = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a')))
            if self.username_test.text == username_tb:
                print('登录成功！\n')
        except BaseException:
            raise Exception('登录失败')

    def webdriver_search(self):
        try:
            self.browser.find_element_by_css_selector('#q').send_keys('{}'.format(self.search_goods_name))
            self.browser.find_element_by_css_selector('#J_TSearchForm > div.search-button > button').click()
        except BaseException:
            raise Exception('搜索操作失败！')

    def webdriver_get_html(self):
        for i in range(needed_pages_num):
            self.parse_data(self.browser.page_source, i)
            sleep(1)
            try:
                self.wait_next = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.next > a')))
                for i in range(2):
                    self.browser.execute_script('window.scrollBy(0,2000)')
                    sleep(2)
                self.browser.find_element_by_css_selector(
                    '#mainsrp-pager > div > div > div > ul > li.item.next > a').click()
            except BaseException:
                print('没有下一页了！\n')
                pass

    def parse_data(self, page_content, currently_page):
        try:
            self.json_begin = page_content.find('g_page_config = ') + len('g_page_config = ')
            self.json_end = page_content.find('"shopcardOff":true}') + len('"shopcardOff":true}')
            self.json_data = json.loads(page_content[self.json_begin:self.json_end + 1])
        except BaseException:
            if self.page.find('亲，小二正忙，滑动一下马上回来') != -1:
                print('遭遇反爬机制！等待重试\n')
                self.re_try(currently_page)
            else:
                raise Exception('json解析错误！\n')

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
                    product_rate_delivery = i['shopcard']['delivery'][0] / 100
                    product_rate_description = i['shopcard']['description'][0] / 100
                    product_rate_service = i['shopcard']['service'][0] / 100
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
                self.file.write(
                    '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(product_name, product_price,
                                                                                  product_local, product_sales,
                                                                                  product_seller,
                                                                                  product_is_Gold_seller,
                                                                                  product_is_commonweal_product,
                                                                                  product_is_Tmall,
                                                                                  product_rate_delivery,
                                                                                  product_rate_description,
                                                                                  product_rate_service,
                                                                                  total_rate,
                                                                                  seller_Credit,
                                                                                  product_comment_count,
                                                                                  product_comment,
                                                                                  product_detail_url,
                                                                                  product_shop_link))
            print('第{}页解析成功'.format(int(currently_page) + 1))
            self.count_success += 1
        except AttributeError:
            print('第{}页解析失败！'.format(int(currently_page) + 1))
            self.count_fail += 1
            pass


if __name__ == '__main__':
    username_tb = input('请输入你的淘宝账号用户名\n')
    username = input('请输入你的微博账号\n')
    passwd = input('请输入你的微博密码\n')
    goods_name = input('请输入要搜索的商品名称\n')
    needed_pages_num = int(input('请输入需要爬取的页面数\n'))

    begin_time = datetime.datetime.now()
    spider = tb_spider()
    spider.webdriver_login()
    spider.webdriver_search()
    spider.webdriver_get_html()
    spider.browser.quit()
    spider.file.close()
    spider.count_total = spider.count_success + spider.count_fail
    course_time = (datetime.datetime.now() - begin_time).seconds
    print('运行完毕，共耗时{}分{}秒, 共解析{}个页面，其中{}个成功，{}个失败'.format(course_time // 60, course_time % 60,
                                                          spider.count_total,
                                                          spider.count_success, spider.count_fail))