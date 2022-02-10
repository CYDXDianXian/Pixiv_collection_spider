import time
import requests
from pathlib import Path
import traceback

path_config = "Pixiv_个人收藏"  # 设置图片的保存地址

path = Path(__file__).parent / path_config # 拼接路径。__file__，是一个字符串，表示当前文件的绝对路径。若不进行该设置，直接运行py文件图片路径会存到C盘system32文件夹下
Path(path).mkdir(parents = True, exist_ok = True)

# ===需要设置的参数===
page = 1 # 获取到第几页为止

url_pages = []
for r in range(page):
    offset = r * 48
    url_page = f'https://www.pixiv.net/ajax/user/15103058/illusts/bookmarks?tag=&offset={offset}&limit=48&rest=show&lang=zh' # 个人收藏的请求地址，一页48个pid（需要抓包获得地址，非浏览器上直接显示的地址）
    url_pages.append(url_page)
# ===需要设置的参数===


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
    'cookie': ''
}
# 请求失败需重新更换cookie，cookie为个人收藏请求地址bookmarks?下的cookie，不能是别处请求到的cookie

proxy = {
    'http': 'http://localhost:7890',
    'https': 'http://localhost:7890'
}
# 设置代理地址

def get_urls():
    global get_urls_msg
    start_time = time.time()

    urls = {}
    page_num = 0 
    img_url_num = 0
    error_num = 0
    for url in url_pages:
        page_num += 1
        try:
            resp = requests.get(url, headers = headers, proxies = proxy, timeout = 30)
        except:
            print(f'第{page_num}页访问超时，请检查链接地址是否正确，或开启代理！')
            continue
        headers['referer'] = 'https://www.pixiv.net/' # 在请求头中增加一个referer,否则访问图片地址会403
        resp.encodin = 'utf-8'

        data = resp.json()

        try:
            for i in data['body']['works']:
                img_id = i['id']
                url_id = f'https://www.pixiv.net/ajax/illust/{img_id}/pages?lang=zh' # 图片json数据请求地址
                try:
                    data_id = requests.get(url_id, headers = headers, proxies = proxy, timeout = 30).json()
                except:
                    error_num += 1
                    print(f'图片地址爬取失败{error_num}个，ID = {img_id}')
                    continue # 从此结束后继续循环
                for o in data_id['body']:
                    bmk_id = i['bookmarkData']['id']
                    img_url = o['urls']['original']
                    img_name = img_url.split("/")[-1] # 拿到url中的最后一个/以后的内容(图片名)
                    name = f'{bmk_id}_{img_name}'
                    img_url_num += 1
                    urls[name] = img_url
                    print(f'图片地址爬取成功{img_url_num}个')
        except TypeError:
            print('图片数据获取失败，请设置或更换一个cookie！')
        except:
            print(traceback.print_exc())
    
    end_time = time.time()
    use_time = int(end_time - start_time)
    
    print(f'共爬取到{img_url_num}个文件，即将开始下载！')
    
    get_urls_msg = f'共爬取成功{img_url_num}个文件，失败{error_num}个，爬取用时{use_time}秒'

    return urls

def download():
    urls = get_urls()
    start_time = time.time()

    img_url_num = 0
    success_num = 0
    error_num = 0
    for name, img_url in urls.items():
        img_url_num += 1
        if not Path(path, name).exists(): 
            try:
                img_resp = requests.get(img_url, headers = headers, proxies = proxy, timeout = 30)
            except:
                error_num += 1
                print(f'第{img_url_num}个图片下载失败：{name}')
                continue # 从此结束后继续循环
            
            Path(path, name).write_bytes(img_resp.content)
            success_num += 1
            print(f'第{img_url_num}个图片下载成功：{name}')
        else:
            print(f'第{img_url_num}个图片 {name} 已存在，不再进行下载')

    end_time = time.time()
    use_time = int(end_time - start_time)

    print('全部完成！！！')
    print(get_urls_msg)
    print(f'共下载成功{success_num}个文件，失败{error_num}个，下载用时{use_time}秒')

if __name__ == "__main__":
    download()