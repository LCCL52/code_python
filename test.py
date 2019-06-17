import requests
import random
from lxml import etree
import os
import re
requests.adapters.DEFAULT_RETRIES = 5
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"}
post_url = "http://192.168.4.253/index.php/Login/login"
post_data = [{"username": "luochen", "password": "password"}]
Big_url = "http://192.168.4.253/index.php/Study/studydetail?taskid={}"
post_data = random.choice(post_data)
session = requests.session()
session.post(post_url, data=post_data, headers=headers)
for i in range(1, 3):
    one_url = "http://192.168.4.253/index.php/Study/listunderway?per_page={}"
    first_data = session.get(one_url.format(i), headers=headers)

    html = etree.HTML(first_data.content.decode())
    ret = html.xpath('//div[@class="taskimg"]//a/@taskid')
    Big_url = []
    for i in range(0, len(ret)):
        Big_url.append("http://192.168.4.253/index.php/Study/studydetail?taskid={}".format(ret[i]))
    print(Big_url)

    Bigtit_list = html.xpath('//div[@class="taskimg"]//a/@title')
    print(Bigtit_list)
    for Bigtit in Bigtit_list:
        # print(Bigtit,Bighref)
        if os.path.exists(Bigtit) == False:  # 判断有无此文件夹
            os.mkdir(Bigtit)

    for bigurl, bigtitle in zip(Big_url, Bigtit_list):
        second_data = session.get(bigurl, headers=headers)
        html = etree.HTML(second_data.content.decode())
        Little_title_list = html.xpath('//p[@class="itemTitle" ]//a/text()')
        Little_url_list = html.xpath('//p[@class="itemTitle" ]//a//@href')

        for little_url, little_title in zip(Little_url_list, Little_title_list):
            vedio_page_data = session.get(little_url, headers=headers)
            html = etree.HTML(vedio_page_data.content.decode())
            vedio_url = html.xpath('//video//source/@src')
            if len(vedio_url) > 0:
                # ren = ".*?(:)*?"
                little_title= re.sub(':', " ", little_title)   #替换掉标题中的冒号
                print(bigtitle)
                path = bigtitle + "\\" + little_title + ".mp4"
                try:
                    vedio_data=session.get(vedio_url[0])
                    with open(path, 'wb') as output:
                        while True:
                            buffer = vedio_data.read(1024 * 256);
                            if not buffer:
                                break
                            # received += len(buffer)
                            output.write(buffer)
                        output.close()
                    print(little_title + ".mp4下载成功")

                except Exception as e:
                    print(e)

        else:
            try:
                html_data = vedio_page_data.content
                fail_path = bigtitle + "\\" + little_title + ".html"
                with open(fail_path, "w",encoding="utf-8") as f:
                    f.write(html_data)
                    f.close()
                    print(little_title + ".html下载成功")
            except Exception as e:
                print(e)
