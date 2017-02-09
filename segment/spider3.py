URLS = ["http://news.xinhuanet.com/politics/2017-02/06/c_1120420090.htm",
        "http://news.xinhuanet.com/science/2017-02/06/c_136031274.htm",
        "http://news.xinhuanet.com/city/2017-02/06/c_129467919.htm",
        "http://news.xinhuanet.com/yuqing/2017-02/06/c_129467889.htm",
        "http://news.xinhuanet.com/fortune/2017-02/06/c_1120415040.htm",
        "http://news.xinhuanet.com/comments/2017-02/06/c_1120419724.htm",
        "http://news.xinhuanet.com/world/2017-02/06/c_1120416156.htm",
        "http://news.xinhuanet.com/info/2017-02/06/c_136034317.htm"]


import re
import requests
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin


user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56."
                            "0.2924.87 Safari/537.36"}


if __name__ == "__main__":
    fout = open("spider3.txt", "w")
    for link in URLS:
        print('trying on %s' % link)
        response = requests.get(link, headers=user_agent)
        response.encoding = 'utf-8'
        content = response.text
        new_soup = BeautifulSoup(content, "lxml")
        for para in new_soup.select('p'):
            try:
                sents = list(filter(lambda x: x != "", re.split(r"\s|\d|《|》|　|，|。|、|！|？", para.string)))
                for sent in sents:
                    new_list = lazy_pinyin(sent, errors='ignore')
                    if new_list:
                        fout.write('%s\n' % ' '.join(new_list))
            except TypeError as e:
                print(e)