#!/usr/bin/env python  
#coding=utf8 
'''
Created on Jul 15, 2013

@author: pitty <pitty.xu@gmail.com>
'''
try:
    import os
    import sys
    import time
    import random
    import urllib
    import urllib2
    import threading  
    import analysis.WeiboSearchAnalysis as Analysis
    import util.WeiboSearchService as Service
except ImportError:
        print >> sys.stderr, """\
    There was a problem importing one of the Python modules required.
    The error leading to this problem was:

    %s

    Please install a package which provides this module, or
    verify that the module is installed correctly.

    It's possible that the above module doesn't match the current version of Python,
    which is:

    %s

    """ % (sys.exc_info(), sys.version)
        sys.exit(1)
reload(sys)
sys.setdefaultencoding('utf-8')
  
pagesContent = []           #html content of downloaded pages  
textContent = []            #main text content of downloaded pages  
triedKw = []               #all tried urls, including failed and success  
toTryKw = []                #keyWord to search
failedKw = []              #urls that fails to download  
service = None
  
class WebCrawl:  
    "WebCrawl class  爬取微博内容"  
  
    def __init__(self, keyWords, searchUrl = "http://s.weibo.com", maxSearchPage = 50, maxThreadNum = 1,
                  thLifetime = 1000, database = 'weibo_search', host='localhost', 
                  port=3306, user='root', pwd='tester', pref='ws', sleepTime = 1):
        "Initialize the class WebCrawl"  
        global toTryKw
        global service
        
        service = Service.WeiboSearchService(host=host, user=user, passwd=pwd,
                port=port, database=database, pref=pref);
        
        self.searchUrl = searchUrl  
        if isinstance(keyWords, list):
            toTryKw = keyWords
        else:
            toTryKw.append(keyWords)
        self.maxThreadNum = maxThreadNum  
        self.maxSearchPage = maxSearchPage
        self.thLifetime = thLifetime
        self.threadPool = []
        self.sleepTime = sleepTime
  
    def Crawl(self):  
        """
        启动抓取程序
        """
        global toTryKw
        global service
        iDownloaded = 0  
        while iDownloaded < len(toTryKw):  
            iThread = 0  
            while iThread < self.maxThreadNum and iDownloaded + iThread < len(toTryKw):  
                iCurrentUrl = iDownloaded + iThread  
                self.DownloadUrl(toTryKw[iCurrentUrl], self.maxSearchPage, self.sleepTime)
                iThread += 1  
                  
            iDownloaded += iThread  
              
            for th in self.threadPool:  
                th.join(self.thLifetime)  
                  
            self.threadPool = []  
              
        toTryKw = [] 
        service.close()
  
    def DownloadUrl(self, keyword, pageNum = 50, sleepTime = 1):
        "Download a single url and save"  
        cTh = CrawlThread(keyword, pageNum, self.searchUrl, sleepTime)
        self.threadPool.append(cTh)  
        cTh.start()  
  
class CrawlThread(threading.Thread):  
    "抓取线程"  
    thLock = threading.Lock()  
    def __init__(self, keyword, pageNum = 50, url = 'http://s.weibo.com', sleep_time = 1):
        "Initialize the CrawlThread"  
        threading.Thread.__init__(self)
        self.k_id = 0
        self.maxPage = pageNum 
        self.kw = keyword
        self.keyword = self.encode_url(keyword)
        self.url = url + '/weibo/' + self.keyword
        self.sleep_time = sleep_time
  
    def encode_url(self, keyword):
        keyword = keyword.decode(sys.stdin.encoding).encode("utf-8")
        return urllib.quote(urllib.quote(keyword))
    
    def insert_weibos(self, ana, service, k_id):
        #ana = Analysis.Analysis(htmlContent)
        #last = service.get_last_by_kids(k_ids)
        #print last
        weibo_info = ana.get_weibo_feedlist()
        values = []
        for wb in weibo_info:
            if not service.is_weibo_exist(wb['user'], wb['push_date']):
                values.append((k_id, wb['user'], wb['content'], wb['approve'], 
                    wb['reply'], wb['retweet'], wb['favorite'], wb['push_date']))
        if len(values):
            service.insert_weibos(values)
                
    def run(self):
        "rewrite the run() function"
        global service
        global failedKw  
        global triedKw  
        try:
            #if random.randint(0, 100) % 6:
            #    print "Account index..."
            #    urllib2.urlopen('http://account.weibo.com/set/index')
            #elif random.randint(0, 100) % 5:
            #    print "Account..."
            #    urllib2.urlopen('http://account.weibo.com')
            print self.url # + '&page=' + page.__str__()
            htmlContent = urllib2.urlopen(self.url).read()
            ana = Analysis.Analysis(htmlContent)
            while not ana.flag:
                com = raw_input('出现验证码,请确认已经手动输入过验证码(y):')
                if com == 'y':
                    htmlContent = urllib2.urlopen(self.url).read()
                    ana = Analysis.Analysis(htmlContent)
                else:
                    continue
            sub = 0
            #keys = None
            maxP = self.maxPage
            if self.k_id == 0:    
                sub, self.k_id, keys = service.insert_keyword([self.kw, ana.get_weibo_totalshow()]);
            print self.kw, '比上次新增加:', sub, '条记录, 新关键字id:', self.k_id
            maxP = int((sub + 19) / 20)
            if maxP > 50:
                maxP = 50
            if self.maxPage > maxP:
                self.maxPage = maxP
            page = self.maxPage
            #k_ids = None
            #if keys:
            #    for k in keys:
            #        if k_ids:
            #            k_ids = k_ids + k['id'].__str__() + ','
            #        else:
            #            k_ids = k['id'].__str__() + ','
            #if k_ids:
            #    k_ids = k_ids[0:-1]
            #print k_ids
            print 'Catch page number:' + page.__str__()

            while 0 < page:        
                try:
                    time.sleep(random.uniform(self.sleep_time, self.sleep_time * 2))
                    print self.url + '&page=' + page.__str__()
                    htmlContent = urllib2.urlopen(self.url + '&page=' + page.__str__()).read()
                    ana = Analysis.Analysis(htmlContent)
                    while not ana.flag:
                        com = raw_input('出现验证码,请确认已经手动输入过验证码(y):')
                        if com == 'y':
                            htmlContent = urllib2.urlopen(self.url + '&page=' + page.__str__()).read()
                            ana = Analysis.Analysis(htmlContent)
                        else:
                            continue
                    self.insert_weibos(ana, service, self.k_id)
                    page -= 1
                except Exception, e:
                    print e
                    self.thLock.acquire()  
                    service.commit()
                    failedKw.append(self.kw + page.__str__())  
                    self.thLock.release() 
                    page -= 1
                self.thLock.acquire()   
                service.commit()
                self.thLock.release()
        except Exception, e:
            print 'Init Error:', e + self.kw + ' not begin.'
            self.thLock.acquire() 
            service.commit() 
            failedKw.append(self.kw)  
            self.thLock.release()