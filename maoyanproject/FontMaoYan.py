import requests
from requests.exceptions import ConnectionError
import re
import base64
from fake_useragent import UserAgent
from fontTools.ttLib import TTFont
from pyquery import PyQuery as pq


ua = UserAgent(use_cache_server=False).random
headers = {
    'User-Agent': ua
}


def get_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(1)
            return response.text
        else:
            return get_page(url)
    except ConnectionError:
        print('ERROR')
        return get_page(url)


def ttf_font(response):
    try:
        font = re.findall(r"src:url\(data:application/font-woff;charset=utf-8;base64,(.*?)\) format", response)[0]
        fontdata = base64.b64decode(font)
        with open('请求字体.ttf', 'wb') as f:
            f.write(fontdata)
        font = TTFont('请求字体.ttf')
        basefont = TTFont('映射字体.ttf')
        uni_list = font['cmap'].tables[0].ttFont.getGlyphOrder()
        num_list = []
        base_list = ['.', '7', '8', '9', '3', '2', '4', '0', '1', '6', '5']
        base_code = ['x', 'uniEF7E', 'uniF47D', 'uniF53F', 'uniE5DE', 'uniE2F4', 'uniEEC7', 'uniEF40', 'uniEA32',
                     'uniF79B', 'uniF60F']
        for i in range(1, 12):
            maoyanGlyph = font['glyf'][uni_list[i]]
            for j in range(11):
                baseGlyph = basefont['glyf'][base_code[j]]
                if maoyanGlyph == baseGlyph:
                    num_list.append(base_list[j])
        ttf_dict = dict(zip([r.lower() for r in uni_list[1:]], num_list))
        if ttf_dict:
            return ttf_dict
    except Exception as e:
        print(e)
        return ttf_font(response)


def get_detail(response, ttf_dict):
    text = re.sub(';', '', re.sub('&#x', 'uni', response))
    for i in ttf_dict.items():
        if i[0] != 'x':
            text = re.sub(i[0], i[1], text)
    html = pq(text)
    movie_bor_list = html('#ticket_tbody ul')
    for item in movie_bor_list.items():
        movie_name = item('li.c1 b').text()
        if item('li.c1 em:nth-child(3)').text():
            movie_day = item('li.c1 em:nth-child(3)').text()
        else:
            movie_day = item('li.c1 > i').text()
        total_bor = item('li.c1 > em:nth-child(4) > i').text()
        real_time_bor = item('li.c2 > b > i').text()
        accounting_bor = item('li.c3 > i').text()
        accounting_platter = item('li.c4 > i').text()
        attendance_rate = item('li.c5 > span:nth-child(1) > i').text()
        print({
            '电影名称': movie_name,
            '上映天数': movie_day,
            '当前总票房': total_bor,
            '实时票房(万元)': real_time_bor,
            '票房占比': accounting_bor,
            '排片占比': accounting_platter,
            '上座率': attendance_rate
        })


def main():
    url = 'http://piaofang.maoyan.com/?ver=normal'
    response = get_page(url)
    ttf_dict = ttf_font(response)
    get_detail(response, ttf_dict)


if __name__ == '__main__':
    main()