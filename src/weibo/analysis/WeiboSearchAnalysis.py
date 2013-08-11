#!/usr/bin/env python  
#coding=utf8 
'''
Created on Jul 31, 2013

@author: xuexu <xuexu@adobe.com>
'''
try:
    import sys
    import json
    from lxml import etree
except ImportError:
        print >> sys.stderr
reload(sys)
sys.setdefaultencoding('utf-8')

class Analysis:
    
    def __init__(self, page):
        self.dic = {}
        lines = page.splitlines()
        for line in lines:  
            if line.startswith('<script>STK && STK.pageletM && STK.pageletM.view('):  
                tJson = json.loads(line[49:-10])
                self.dic.update({tJson['pid']: tJson['html']})
        #pl_common_searchTop 上方搜索条
        #plc_main 搜索 综合 实时 热门 选择
        #pl_weibo_prepareData 为空
        #pl_weibo_direct 找到的人信息，不是用户则为空
        #pl_weibo_directright 相关用户
        #pl_common_ad 为空
        #pl_weibo_hotband 综合热搜榜
        #pl_weibo_subscribe 为空
        #pl_weibo_feedlist 搜索结果
        #pl_weibo_filtertab 筛选 全部或原创
        #pl_common_totalshow 搜索结果数
        #pl_common_pinyinerr 为空
        #pl_weibo_relation 为空
        #pl_common_bottomInput 下方搜索条
        #pl_common_searchHistory 为空
        #pl_common_base 为空
#         print self.dic['pl_weibo_feedlist']
    def get_weibo_totalshow(self):
        text = self.dic['pl_common_totalshow']
        text = text[text.find('<span') : text.find('</span>')]
        return filter(str.isdigit, text.__str__())
        #doc = etree.HTML(self.dic['pl_common_totalshow'].decode('utf-8'))
        #text = doc.xpath("//*[@class='W_textc']")
        #return filter(str.isdigit, text[0].text.__str__())
    
    def get_weibo_feedlist(self):
        doc = etree.HTML(self.dic['pl_weibo_feedlist'].decode('utf-8'))
        feed_list = []
        for content in doc.xpath("//*[@class='content']"):
            feed_list.append(self.get_weibo_feed(content))
        return feed_list
    
    def get_weibo_feed(self, content):
        user = content.xpath("string(.//a[@nick-name])")
        weibo = content.xpath("string(./p/em)") + \
                 content.xpath("string(./dl/dt[@node-type])") + \
                 content.xpath("string(./dl/dd[contains(@class, 'info')])")
        approve = self.get_weibo_num_info(content, 1)
        retweet = self.get_weibo_num_info(content, 2)
        favorite = self.get_weibo_num_info(content, 3)
        reply = self.get_weibo_num_info(content, 4)
        push_date =content.xpath("string(./p[contains(@class, 'info')]/a[@date]/@date)")
        if len(push_date) > 10:
            push_date = push_date[0:-3]
        return {
            'user': user,      #用户
            'content': weibo,   #微博内容
            'approve': approve,   #赞
            'reply': reply,     #回复
            'retweet': retweet,   #转发
            'favorite': favorite,  #收藏
            'push_date': push_date  #发布时间
        }
    
    def get_weibo_num_info(self, content, index):
        '''
            获得微博信息 赞 转发 收藏 评论
        '''
        info = filter(str.isdigit, content.xpath("string(./p[contains(@class, 'info')]/span/a[" + str(index) + "]/text())").__str__())
        if info == '':
            info = 0
        return int(info)