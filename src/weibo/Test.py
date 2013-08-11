#!/usr/bin/env python  
#coding=utf8 
'''
Created on Jul 15, 2013

@author: labuser
'''
#import analysis.WeiboSearchAnalysis as Analysis
import util.WeiboSearchService as Service
if __name__ == '__main__':  
    ser = Service.WeiboSearchService()
    sub, a, b =  ser.insert_keyword(['你好', '1077899386'])
    maxP = int((sub + 19) / 20)
    print maxP
    #print ser.insert_keyword(['你好', '177899386'])
    #print ser.insert_keyword(['你好', '343498761'])
    
    #ser.commit()
    
    #fOut = open('CrawledPages/chao_1.html', 'r')  
    
    #text = fOut.read(); 
    #fOut.close()
    
    #ana = Analysis.Analysis(text)
    #service = Service.WeiboSearchService()
    #k_id = 0
    #if k_id == 0:        
    #    k_id = service.insert_keyword(['chao', ana.get_weibo_totalshow()]);
    #weibo_info = ana.get_weibo_feedlist()
    #values = []
    #for wb in weibo_info:
    #    values.append((k_id, wb['user'], wb['content'], wb['approve'], 
    #        wb['reply'], wb['retweet'], wb['favorite'], wb['push_date']))
    #service.insert_weibos(values)
    #service.commit()
    #a.get_weibo_feedlist()
    #aText = []
    
    #lines = text.splitlines()
    #for line in lines:  
     #   if line.startswith('<script>STK && STK.pageletM && STK.pageletM.view('):  
    #        aText.append(line[49:-10])
    #for text in aText:
    #    s = json.loads(text)
        #print dict(pid='pl_common_searchTop')
        #print s.keys()
       # print s['pid']