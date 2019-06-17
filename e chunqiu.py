import re
import requests
import random
from lxml import etree
import os
class Spider():
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"}
        self.post_url = "http://192.168.4.253/index.php/Login/login"
        self.post_data = [{"username": "luochen", "password": "l18482929029c"}]
        self.Big_url = "http://192.168.4.253/index.php/Study/studydetail?taskid={}"

    def load(self):  # 登录获取第一页内容
        post_data = random.choice(self.post_data)
        session = requests.session()
        session.post(self.post_url, data=post_data, headers=self.headers)
        for i in range(1, 3):
            one_url="http://192.168.4.253/index.php/Study/listunderway?per_page={}"
            response =session.get(one_url.format(i), headers=self.headers)
        return response.content.decode()

    def Big_url(self,first_data):  # 提取TaskID构造下一级url
        html = etree.HTML(first_data.content.decode())
        ret=html.xpath('//div[@class="taskimg"]//a/@taskid')
        Big_url=[]
        for i in range(0, len(ret)):
            Big_url.append("http://192.168.4.253/index.php/Study/studydetail?taskid={}".format(ret[i]))
        return Big_url

    def Big_title(self,first_data):
        html = etree.HTML(first_data.content.decode())
        Bigtit_list=html.xpath('//div[@class="taskimg"]//a/@title')
        return Bigtit_list


    def crate_big_file(self,Bigtit_list):       #创建相应文件夹
        for Bigtit in Bigtit_list:
            #print(Bigtit,Bighref)
            if os.path.exists(Bigtit)==False:#判断有无此文件夹
                os.mkdir(Bigtit)          #创建文件夹

    def load_little_url(self, bigurl):#进入二级url，得到课程的详细信息
        post_data = random.choice(self.post_data)
        session = requests.session()
        session.post(self.post_url, data=post_data, headers=self.headers)
        response = session.get(bigurl, headers=self.headers)
        return response.content.decode()

    # 获取三级url地址
    def Little_url(self,second_data):
        html = etree.HTML(second_data.content.decode())
        Little_url_list=html.xpath('//p[@class="itemTitle" ]//a//@href')
        return Little_url_list

    def Little_title(self,second_data):
        html = etree.HTML(second_data.content.decode())
        Little_title_list=html.xpath('//p[@class="itemTitle" ]//a/text()')
        return Little_title_list

    def load_third_url(self,little_url): #进入视频播放页面，发送请求获取数据
        post_data = random.choice(self.post_data)
        session = requests.session()
        session.post(self.post_url, data=post_data, headers=self.headers)
        response = session.get(little_url, headers=self.headers)
        return response.content.decode()

    def vedio_url(self,vedio_page_data):
        html = etree.HTML(vedio_page_data.content.decode())
        vedio_url=html.xpath('//vedio//source/@src')
        return vedio_url

    def save_vedio(self,vedio_url,bigtitle,little_title):
        post_data = random.choice(self.post_data)
        session = requests.session()
        session.post(self.post_url, data=post_data, headers=self.headers)
        response = session.get(vedio_url, headers=self.headers)
        little_title = re.sub(':', " ", little_title)  # 替换掉标题中的冒号
        path = bigtitle + "\\" + little_title + ".mp4"
        if os.path.exists(path) == False:
            with open(path,"wb") as f:
                f.write(response.content)
                f.close()

    def seve_page(self,vedio_page_data,little_title,bigtitle):
        little_title = re.sub(':', " ", little_title)  # 替换掉标题中的冒号
        path = bigtitle + "\\" + little_title + ".html"
        with open(path,"w",encoding="utf-8") as f:
            f.write(vedio_page_data)
            f.close()

    def run(self):
        # 登录发送请求获取响应
        first_data = self.load()
        # 爬取所有课程名字和url
        Bigurl_list=self.Big_url(first_data)
        Bigtit_list=self.Big_title(first_data)
        # 创建相应课程文件夹
        self.crate_big_file(Bigtit_list)
        #进入二级url
        for bigurl,bigtitle in zip(Bigurl_list,Bigtit_list):
            second_data=self.load_little_url(bigurl)
            # 获取每一小节名字和url
            Little_url_list=self.Little_url(second_data)
            Little_title_list=self.Little_title(second_data)
            print(Little_title_list,Little_url_list)
        #进入视频播放
            for little_url,little_title in zip(Little_url_list,Little_title_list):
                vedio_page_data=self.load_third_url(little_url)
                vedio_url=self.vedio_url(vedio_page_data)
                # 判断是视频还是文本教程
                if len(vedio_url)>0:
                    try:
                    # 若是视频，提取视频地址，下载保存
                        self.save_vedio(vedio_url[0],bigtitle,little_title)
                    except Exception as e:
                        print(e)
                else:
                    try:
                    # 若是网页教程，保存为HTML格式文件
                        self.seve_page(vedio_page_data,bigtitle,little_title)
                    except Exception as e:
                        print(e)

if __name__ == '__main__':
    spider=Spider()
    spider.run()

