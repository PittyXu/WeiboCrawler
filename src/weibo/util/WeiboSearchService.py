#!/usr/bin/env python  
#coding=utf8 
'''
Created on Aug 4, 2013

@author: xuexu <xuexu@adobe.com>
'''
try:
    import sys 
    import MySQLdb as mdb
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
        
class WeiboSearchService:
    '''
    数据库操作类
    '''

    def __init__(self, host='localhost', user='root', passwd='tester', \
                port=3306, database='weibo_search', charset='utf8', pref='ws'):
        '''
        Constructor
        '''
        try:
            self.conn = mdb.Connect(host=host, user=user, passwd=passwd, port=port, charset=charset)
        except mdb.Error, e:
            print "MySQL Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        self.pref = pref
        self.database = database
        self.keywordsT = "`" + self.database + "`.`" + self.pref + "_keywords`"
        self.weiboT = "`" + self.database + "`.`" + self.pref + "_weibo`"
        self.cur = self.get_cursor('dict')
        self.cur.execute('CREATE DATABASE IF NOT EXISTS `' + database + "` ;")
        self.conn.select_db(database)
        self.cur.execute("CREATE TABLE IF NOT EXISTS `" + self.pref + """_keywords` (
                `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '关键词id',
                `keyword` varchar(255) NOT NULL COMMENT '关键词',
                `result` int(11) NOT NULL COMMENT '结果数',
                `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '抓取时间',
                PRIMARY KEY (`id`),
                KEY `keyword` (`keyword`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ; """)
        self.cur.execute(""" CREATE TABLE IF NOT EXISTS `""" + self.pref + """_weibo` (
                `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '记录id',
                `k_id` int(11) NOT NULL COMMENT '关键词id',
                `userName` varchar(255) NOT NULL COMMENT '用户',
                `weibo` text NOT NULL COMMENT '微博内容',
                `approve` int(11) NOT NULL COMMENT '赞',
                `reply` int(11) NOT NULL COMMENT '回复',
                `retweet` int(11) NOT NULL COMMENT '转发',
                `favorite` int(11) NOT NULL COMMENT '收藏',
                `pushDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
                `getDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '抓取时间',
                PRIMARY KEY (`id`),
                KEY `userName` (`userName`),
                KEY `k_id` (`k_id`),
                KEY `pushDate` (`pushDate`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ; """)
    
    def get_cursor(self, type):
        if type == 'dict':
            return self.conn.cursor(cursorclass = mdb.cursors.DictCursor)
        return self.conn.cursor()
    
    def insert_keyword(self, values=[]):
        if len(values):
            #self.cur = self.get_cursor('dict')
            res = self.get_keywords_by_ky(values[0])
            if res:
                sub = int(values[1]) - int(res[0]['result'])
            else:
                sub = int(values[1])
            if sub > 0:
                self.cur.execute("""INSERT INTO """ + self.keywordsT + """ (
                    `id`, `keyword`, `result`, `date`) VALUES (
                    NULL, %s, %s, CURRENT_TIMESTAMP);""", values)
                self.commit()
                return sub, self.conn.insert_id(), res
            return sub, 0, None
        return 0, 0, None
            #print self.cur.lastrowid
            #print self.conn.insert_id()
            #return (self.conn.insert_id())
            #self.commit()
    
    def get_keywords_by_ky(self, keyword):
        self.cur.execute("SELECT * FROM " + self.keywordsT + """ WHERE 
            `keyword`='""" + keyword + """' ORDER BY result;""")
        re = self.cur.fetchall()
        if len(re):
            return re
        return None
    
    def get_last_by_kids(self, k_ids):
        if k_ids:
            self.cur.execute("SELECT id, userName, UNIX_TIMESTAMP(pushDate) FROM " + self.weiboT + " WHERE k_id IN ("
                    + k_ids.__str__() + ") ORDER BY pushDate DESC LIMIT 1")
            re = self.cur.fetchall()
            if len(re):
                return re[0]
        return None
    
    def is_weibo_exist(self, userName, date):
        self.cur.execute("SELECT * FROM " + self.weiboT + """ WHERE `userName`=
            %s AND `pushDate`=FROM_UNIXTIME(%s)""", [userName, date])
        re = self.cur.fetchall()
        if len(re):
            return True
        return False
    
    def insert_weibos(self, values=[]):
        if len(values) > 0:
            print values
            print self.cur.executemany("""INSERT INTO """ + self.weiboT + """ (
                `id`, `k_id`, `userName`, `weibo`, `approve`, `reply`, `retweet`, `favorite`, 
                `pushDate`, `getDate`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(%s), CURRENT_TIMESTAMP)""", values)
            self.commit()
        else:
            print 'Error insert length is:', len(values)
    
    def insert_weibo(self, values=[]):
        if len(values) > 0:
            self.cur.execute("""INSERT INTO """ + self.weiboT + """ (`id`, `k_id`, 
            `userName`, `weibo`, `approve`, `reply`, `retweet`, `favorite`, 
            `pushDate`, `getDate`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, FROM_UNIXTIME(%s), CURRENT_TIMESTAMP)""", values)
            self.commit()
        else:
            'Error insert length is:', len(values)
            
    def commit(self):
        self.conn.commit()
    
    def close(self):
        """
            关闭数据库连接
        """
        self.commit()
        self.cur.close()
        self.conn.close()
        