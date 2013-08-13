#!/usr/bin/env python  
#coding=utf8 
'''
Created on Jul 15, 2013

@author: pitty <pitty.xu@gmail.com>
'''
try:
    import os
    import sys
    import urllib
    import urllib2
    import cookielib
    import base64
    import re
    import hashlib
    import json
    import rsa
    import binascii
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
class WeiboLogin:  
    "WeiboLogin class 登入 cookie 等操作"  
      
    def __init__(self, user, pwd, cookie_file = "weibo_cookie.txt"):  
        "Constructor of class WeiboLogin."  
  
        print "Initializing WeiboLogin..."  
        self.userName = user  
        self.passWord = pwd  
        self.cookie_file = cookie_file
        print "UserName:", user  
        print "Password:", pwd  
        print "Cookie file:", cookie_file
          
        self.login_url = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)"  
        self.http_headers = {'Referer':'http://t.sina.com.cn',
                             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1'}  
                        #{'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
                        #'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
  
    def login(self):  
        """"
        登入操作，应用初始的 用户名 密码 cookie
            (1) 如果cookie存在 载入cookie 并验证是否 登入成功
            (2) 如果不存在 或 载入失败 或 cookie登入失败 则正常登入do_login
        """
        #如果cookie file 存在，载入cookie
        if os.path.exists(self.cookie_file):
            try:
                cookie_jar  = cookielib.LWPCookieJar(self.cookie_file)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                loaded = 1
            except cookielib.LoadError:
                loaded = 0
                print 'Loading cookies error'
            #install loaded cookies for urllib2
            if loaded:
                cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
                opener         = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                print 'Loading cookies success'
                if self.is_login():
                    return 1
        #没有找到cookie 或者 cookie 载入失败 或 cookie 登入失败
        return self.do_login()

    def is_login(self):
        """
        验证是否登入成功
        """
        url = urllib2.urlopen('http://account.weibo.com').geturl()
        print url
        if "login" in url:
            print "Login faile! 请确认您登入不需要验证码"
            return False
        if len(url) > 24:
            return True
        print "Login faile! 请确认您登入不需要验证码"
        return False
  
    def do_login(self):
        """"
        执行登入步骤
        @param username: 用户名
        @param pwd: 密码
        @param cookie_file: cookie 文件 
        """
        login_data = {
                      'entry': 'weibo',
                      'gateway': '1',
                      'from': '',
                      'savestate': '7',
                      'userticket': '1',
                      'pagerefer':'',
                      'vsnf': '1',
                      'su': '',
                      'service': 'miniblog',
                      'servertime': '',
                      'nonce': '',
                      'pwencode': 'rsa2',
                      'rsakv': '',
                      'sp': '',
                      'encoding': 'UTF-8',
                      'prelt': '45',
                      'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                      'returntype': 'META'
        }

        cookie_jar2     = cookielib.LWPCookieJar()
        cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
        opener2         = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
        urllib2.install_opener(opener2)

        try:
            servertime, nonce, rsakv = self.get_prelogin_status()
        except:
            print 'Login fail...to get servertime or rsakv'
            return 0
    
        #Fill POST data
        login_data['servertime'] = servertime
        login_data['nonce'] = nonce
        login_data['su'] = self.get_user()
        login_data['sp'] = self.get_pwd_rsa(self.passWord, servertime, nonce)
        login_data['rsakv'] = rsakv
        login_data = urllib.urlencode(login_data)
        req_login  = urllib2.Request(
                                     url = self.login_url,
                                     data = login_data,
                                     headers = self.http_headers
                                     )
        result = urllib2.urlopen(req_login)
        text = result.read()
        p = re.compile('location\.replace\(\"(.*?)\"\)')
    
        try:
            #Search login redirection URL
            login_url = p.search(text).group(1)
        
            data = urllib2.urlopen(login_url).read()
        
            #Verify login feedback, check whether result is TRUE
            patt_feedback = 'feedBackUrlCallBack\((.*)\)'
            p = re.compile(patt_feedback, re.MULTILINE)
        
            feedback = p.search(data).group(1)
        
            feedback_json = json.loads(feedback)
            if feedback_json['result']:
                cookie_jar2.save(self.cookie_file, ignore_discard=True, ignore_expires=True)
                return self.is_login()
            else:
                print 'Login fail...No feedback'
                return 0
        except:
            return 0
           
    def get_prelogin_status(self):  
        """
        Perform prelogin action, get prelogin status, including servertime, nonce, rsakv, etc.
        """
        #prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&client=ssologin.js(v1.4.5)'
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + self.get_user() + \
            '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.5)';
        data = urllib2.urlopen(prelogin_url).read()
        p = re.compile('\((.*)\)')
        try:
            json_data = p.search(data).group(1)
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            rsakv = data['rsakv']
            return servertime, nonce, rsakv
        except:
            print 'Getting prelogin status met error!'
            return None 
  
    def get_user(self):
        username_ = urllib.quote(self.userName)
        username = base64.encodestring(username_)[:-1]
        return username
    
    def get_pwd_wsse(self, pwd, servertime, nonce):
        """
            旧版本的密码加密
        """
        pwd1 = hashlib.sha1(pwd).hexdigest()
        pwd2 = hashlib.sha1(pwd1).hexdigest()
        pwd3_ = pwd2 + servertime + nonce
        pwd3 = hashlib.sha1(pwd3_).hexdigest()
        return pwd3

    def get_pwd_rsa(self, pwd, servertime, nonce):
        """
            Get rsa2 encrypted password, using RSA module
        """
        #n, n parameter of RSA public key, which is published by WEIBO.COM
        #hardcoded here but you can also find it from values return from prelogin status above
        weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
    
        #e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
        weibo_rsa_e = 65537
   
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)
    
        #construct WEIBO RSA Publickey using n and e above, note that n is a hex string
        key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)
    
        #get encrypted password
        encropy_pwd = rsa.encrypt(message, key)

        #trun back encrypted password binaries to hex string
        return binascii.b2a_hex(encropy_pwd)