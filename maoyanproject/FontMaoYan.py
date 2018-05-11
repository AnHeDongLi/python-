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

url = 'http://piaofang.maoyan.com/?ver=normal'

try:
    response = requests.get(url, headers=headers).text
except ConnectionError:
    response = requests.get(url, headers=headers).text


def ttf_font():
    try:
        font = re.findall(r"src:url\(data:application/font-woff;charset=utf-8;base64,(.*?)\) format", response)[0]
        fontdata = base64.b64decode(font)
        with open('2.ttf', 'wb') as f:
            f.write(fontdata)
        font = TTFont('2.ttf')
        basefont = TTFont('1.ttf')
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
        return ttf_font()


def map_dict(x):
    str3 = ''
    for i in x:
        if i in ttf_font().keys():
            str3 += ttf_font()[i]
    if re.findall('([\u4e00-\u9fa5]+|%)', ''.join(x)):
        return str3 + x[-1]
    else:
        return str3


def get_detail():
    html = pq(re.sub('&#x', 'uni', response))
    movie_bor_list = html('#ticket_tbody ul')
    for item in movie_bor_list.items():
        movie_name = item('li.c1 b').text()
        if item('li.c1 em:nth-child(3)').text():
            movie_day = item('li.c1 em:nth-child(3)').text()
        else:
            movie_day = item('li.c1 > i').text()
        total_bor = map_dict(item('li.c1 > em:nth-child(4) > i').text().replace('.', 'x;').split(';'))
        real_time_bor = map_dict(item('li.c2 > b > i').text().replace('.', 'x;').split(';'))
        accounting_bor = map_dict(item('li.c3 > i').text().replace('.', 'x;').split(';'))
        accounting_platter = map_dict(item('li.c4 > i').text().replace('.', 'x;').split(';'))
        attendance_rate = map_dict(item('li.c5 > span:nth-child(1) > i').text().replace('.', 'x;').split(';'))
        # bor_list = [total_bor, real_time_bor, accounting_bor, accounting_platter, attendance_rate]
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
    get_detail()


if __name__ == '__main__':
    main()