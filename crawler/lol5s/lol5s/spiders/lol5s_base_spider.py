import scrapy
import pdb
import datetime
import requests
import re

from urllib import unquote
from bs4 import BeautifulSoup

class Lol5sBase(scrapy.Spider):
    name = 'lol5s_mv'
    base_url = 'https://www.lol5s.com/'
    site_id = 1801
    type_code = 100
    def start_requests(self):
        urls = [
                'https://www.lol5s.com/tv/2.html',
            ]
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self,response):
        lis = response.xpath('/html/body/div[3]/div[3]/ul/li')
        for li in lis:
            detail_url = li.css('a::attr(href)').extract_first()
            detail_url = self.base_url + detail_url
            img_url = 'https:' + li.css('img::attr(data-original)').extract_first()
            quolity = li.css('.title::text').extract_first()
            name = li.css('.name::text').extract_first()
            #yield {"detail_url":detail_url,"img_url":img_url,"quolity":quolity,"name":name}
            yield scrapy.Request(url=detail_url,callback=self.parse_detail)
        pages = response.xpath('/html/body/div[3]/div[3]/div[2]/a')
        for page in pages:
            cnt = page.css("::text").extract_first()
            if cnt.encode("utf-8") == '\xe4\xb8\x8b\xe4\xb8\x80\xe9\xa1\xb5':
                next_url = page.css('::attr(href)').extract_first()
                if not next_url:
                    continue
                next_url = self.base_url + next_url
                #pdb.set_trace()
                yield scrapy.Request(url=next_url,callback=self.parse)

    def parse_detail(self,response):
        name = response.css('.butte h1::text').extract_first()
        infos = response.css('.bubu')[0]
        mv_status = infos.css('.p-right::text').extract_first()
        actors = infos.css(' dl.dltxt > dd:nth-child(2)::text').extract_first()
        mv_type = infos.css('div > dl:nth-child(1) > dd:nth-child(1) > a::text').extract_first()
        mv_lgg = infos.css('div.row > dl:nth-child(1) > dd:nth-child(2)::text').extract_first()
        mv_update = infos.css('div > dl:nth-child(1) > dd:nth-child(3)::text').extract_first()
        mv_update = datetime.datetime.strptime(mv_update,'%Y-%m-%d %H:%M:%S')
        mv_area = infos.css('div > dl:nth-child(2) > dd:nth-child(1)::text').extract_first()
        mv_year = infos.css('div > dl:nth-child(2) > dd:nth-child(2)::text').extract_first()
        mv_intro = infos.css('dl:nth-child(3) > dd > p::text').extract_first()
        mv_plist = []
        mv_real_plist = []
        _plist = response.css('#m3u8 > div > ul > li')
        if not _plist or len(_plist) == 0:
            _plist = response.css('.labe2.cur')
        if _plist:
            for _p in _plist:
                _p_title = _p.css('a::text').extract_first()
                _p_url = _p.css('a::attr(href)').extract_first()
                _p_url = self.base_url + _p_url
                mv_plist.append((_p_title,_p_url))
        if len(mv_plist) > 0:
            purl1 = mv_plist[0][1]
            mv_real_plist = self.parse_plist(purl1)
        mv_dlist = []
        _dlist = response.css('#downlist_1 > div.down_list > ul > li')
        if _dlist:
            for _d in _dlist:
                _d_title = _d.css('p > strong::text').extract_first()
                _d_url = _d.css('input::attr(value)').extract_first()
                mv_dlist.append((_d_title,_d_url))
        mv_img = response.css('body > div:nth-child(4) > div.color > div:nth-child(4) > div.col-md-3.col-xs-5.ct.m-padding-right > img::attr(data-original)').extract_first()
        if not mv_img.starts_with("http"):
            mv_img = 'https:'+mv_img
        mv = {}
        mv['name'] = name
        mv['mv_status'] = mv_status
        mv['actors'] = actors
        mv['mv_type'] = mv_type
        mv['mv_lgg'] = mv_lgg
        mv['mv_update'] = mv_update
        mv['mv_area'] = mv_area
        mv['mv_year'] = mv_year
        mv['mv_intro'] = mv_intro
        mv['mv_plist'] = mv_plist
        mv["mv_real_plist"] = mv_real_plist
        mv['mv_dlist'] = mv_dlist
        mv['surl'] = response.url
        mv['type_code'] = 100 #common movie type
        mv['mv_img'] = mv_img
        mv["site_id"] = self.site_id
        yield mv

    def parse_plist(self,purl1):
        req = requests.get(purl1)
        soup = BeautifulSoup(req.content)
        scp = soup.select('body > div.heis > div > div > div.col-md-8.col-sm-12.col-xs-12.bg > script') 
        surl = scp[0]["src"]
        surl = self.base_url+surl
        req = requests.get(surl)
        data = req.content
        m = re.search(r"mac_url=unescape\('(.*)'",data)
        if not m:
            return None
        plist_str = m.group(1)
        plist_str = unquote(plist_str)
        plist = plist_str.split('#')
        lst = []
        for p in plist:
            rds = p.split("$")
            name = rds[0].replace("%","\\").decode("unicode_escape")
            lst.append((name,rds[1]))
        return lst
