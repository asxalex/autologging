#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 alex <alex@localhost>
#
# Distributed under terms of the MIT license.

import urllib
import urllib2
import json
import cookielib
import base64
import rsa
import binascii

usr = "12345678901"
pwd = "password"

username = base64.encodestring(usr).rstrip()
password = pwd

# for pre login url
pre_login_uri = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1486694001345" % username
# for login url
login_url = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=1486705366392"
# for pic fetch url
pic_url = "http://login.sina.com.cn/cgi/pin.php?r=29474726&s=0&p=gz-4e6ceedf65baa7c21faf0596621efaac8852"

class MyRequest():
    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

    def __init__(self):
        self.base_headers = {
                "connection": "keep-alive", 
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; \
                        rv:51.0) Gecko/20100101 Firefox/51.0"
                }

    def post(self, uri, data=None, headers=None):
        if headers is not None:
            header = dict(self.base_headers, **headers)
        else:
            header = self.base_headers
        
        req = urllib2.Request(url=uri, data=data, headers=header)
        result = urllib2.urlopen(req).read()
        return result

    def get(self, uri, headers=None):
        if headers is not None:
            header = dict(self.base_headers, **headers)
        else:
            header = self.base_headers

        req = urllib2.Request(uri, headers=header)
        result = urllib2.urlopen(req).read()
        return result


class LoginSina():
    def __init__(self):
        self.prelogin_data = None
        self.conn = MyRequest()

    def get_prelogin_data(self):
        if self.prelogin_data is None:
            result = self.conn.get(pre_login_uri)
            r = result[result.index('(')+1:result.index(')')]
            result = json.loads(r)
            self.prelogin_data = result
            return result
        return self.prelogin_data

    def get_pic(self):
        res = self.conn.get(pic_url)
        fp = open("pic.png", "w")
        fp.write(res)
        fp.close()

    def get_login_pwd(self):
        data = self.get_prelogin_data()
        pubkey = int(data["pubkey"], 16)
        servertime = data["servertime"]
        nonce = data["nonce"]
        
        key = rsa.PublicKey(pubkey, 65537)
        message = str(servertime) + "\t" + str(nonce) + "\n" + str(password)
        passwd = rsa.encrypt(message, key)
        passwd = binascii.b2a_hex(passwd)
        return passwd

    def gather_login_info(self):
        data = self.get_prelogin_data()
        postdata = {}
        postdata["servertime"] = data["servertime"]
        postdata["nonce"] = data["nonce"]
        postdata["rsakv"] = data["rsakv"]
        postdata["su"] = username
        postdata["sp"] = self.get_login_pwd()
        return postdata

    def login(self):
        self.get_pic()
        door = raw_input("enter the code in pic pic.png: ")
        data = self.gather_login_info()
        data["cdult"] = "2"
        data["domain"] = "weibo.com"
        data["door"] = door
        data["entry"] = "weibo"
        data['encoding'] = 'UTF-8'
        data["from"] = ""
        data["gateway"] = "1"
        data["pagerefer"] = "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F"
        data["pcid"] = "gz-4e6ceedf65baa7c21faf0596621efaac8852"
        data['prelt'] = '126'
        data['pwencode'] = 'rsa2'
        data["resumetype"] = "TEXT"
        data['service'] = 'miniblog'
        data['useticket'] = '1'
        data['vsnf'] = '1'

        headers = {"referer": "http://weibo.com/"}
        data = urllib.urlencode(data)
        result = self.conn.post(login_url, data, headers)
        return result

    def headfor(self, method, uri, body=None, headers=None):
        if method.lower() == "get":
            return self.conn.get(uri, headers)
        if method.lower() == "post":
            return self.conn.post(uri, body, headers)

if __name__ == "__main__":
    sina = LoginSina()
    sina.get_prelogin_data()
    print sina.login()
