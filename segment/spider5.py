URLS = ["http://www.xinhuanet.com/xhsd/index.htm",
        "http://www.news.cn/xhjj.htm",
        "http://www.news.cn/politics/",
        "http://www.news.cn/fortune/",
        "http://www.news.cn/local/",
        "http://www.news.cn/science/",
        "http://education.news.cn/",
        "http://ent.news.cn/",
        "http://www.news.cn/fashion/",
        "http://www.news.cn/culture/",
        "http://www.news.cn/sports/",
        "http://www.news.cn/tech/index.htm"]

import requests
from bs4 import BeautifulSoup
import pickle
from pypinyin import lazy_pinyin
from collections import Counter

user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56."
                            "0.2924.87 Safari/537.36"}


def get_features(word, wordlist):
    feature = {'prev_word': word}
    string = ''.join(wordlist)
    for i in range(1, 6):
        feature['next_word_%d' % i] = string[:i]
    return feature


if __name__ == "__main__":
    data = []
    characters = 0
    fetch_list = []
    for url in URLS:
        try:
            html = requests.get(url, headers=user_agent).text
            soup = BeautifulSoup(html, "lxml")
            for link in soup.select("li.clearfix h3 a"):
                print(link['href'])
                fetch_list.append(link['href'])
        except Exception as e:
            print(e)
    print(len(fetch_list))
    print()
    count = 0
    for link in fetch_list:
        print('trying on %s' % link)
        try:
            response = requests.get(link, headers=user_agent)
            response.encoding = 'utf-8'
            content = response.text
            new_soup = BeautifulSoup(content, "lxml")
            for para in new_soup.select('p'):
                try:
                    new_list = lazy_pinyin(para.string, errors='ignore')
                    characters += len(new_list)
                    prev_word = ""
                    for i in range(len(new_list)):
                        data.append((get_features(prev_word, new_list[i:]), len(new_list[i])))
                        prev_word = new_list[i]
                    # print(data)
                except Exception:
                    pass
        except Exception as e:
            print(e)
        print('\t Character number: %d' % characters)
        count += 1
        if count % 500 == 0:
            with open('./spider5.dict', 'wb') as f:
                pickle.dump(data, f)
#
# with open('./spider2.dict', 'rb') as f:
#     data = pickle.load(f)
#     print(data.most_common(10))