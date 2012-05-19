# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see <http://www.gnu.org/licenses/


# 
# A simple script to demo how to make a screen scraping through intranet
#
# 1. Note: Need two files to run this script 
# *) proxy.pac     Automatic proxy configuration
# *) mypassword    A file to store your plain-text password
#
# 2. Works in windows only, but it is easy to modify to run on *nix.
#
# 3. Dependencies
# *) pacparser  (http://code.google.com/p/pacparser/)
# *) python-ntlm (http://code.google.com/p/python-ntlm/)

#coding=utf-8  
import urllib2 
import os
import sys 
import socket

import pacparser
from ntlm.HTTPNtlmAuthHandler import ProxyNtlmAuthHandler 

# Sample User Agent
useragent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.83 Safari/535.11'

# To test proxy 
def isproxyalive(proxy):
  host_port = proxy.split(":")
  if len(host_port) != 2:
    sys.stderr.write('proxy host is not defined as host:port\n')
    return False
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(10)
  try:
    s.connect((host_port[0], int(host_port[1])))
  except Exception, e:
    sys.stderr.write('proxy %s is not accessible\n' % proxy)
    sys.stderr.write(str(e)+'\n')
    return False
  s.close()
  return True

# To find a proxy server (xxxx.xxx.xxx.xxx:port ) from the pac file
def getproxyserver(pac, url):
  try:
    proxy_string = pacparser.just_find_proxy(pac, url)
  except:
    sys.stderr.write('could not determine proxy using Pacfile\n')
    return None
  proxylist = proxy_string.split(";")

  # Choose first proxy server
  while proxylist:
    proxy = proxylist.pop(0).strip()
    if 'DIRECT' in proxy:
      break
    if proxy[0:5].upper() == 'PROXY':
      proxy = proxy[6:].strip()
      if isproxyalive(proxy):
        break

  return proxy

# get http response through proxy server
def geturl(url,user,password,pacfile):       
    
    proxyserver = getproxyserver(pacfile,url)
    proxy = 'http://%s:%s@%s' % (user, password, proxyserver) 
    proxy_handler = urllib2.ProxyHandler({'http':proxy}) 

    passman = urllib2.HTTPPasswordMgrWithDefaultRealm() 
    passman.add_password(None, url, user, password) 
    auth_NTLM = ProxyNtlmAuthHandler(passman) 
    
    # other authentication handlers
    #auth_basic = urllib2.HTTPBasicAuthHandler(passman)
    #auth_digest = urllib2.HTTPDigestAuthHandler(passman)


    #opener = urllib2.build_opener(proxy_handler, auth_NTLM, auth_digest, auth_basic) 
    opener = urllib2.build_opener(proxy_handler, auth_NTLM) 
    opener.addheaders = [('User-agent',useragent)]

    urllib2.install_opener(opener) 
 
    response = urllib2.urlopen(url) 
    print(response.read()) 

if __name__ == '__main__':

    # Get your windows domain account
    user = '%s\%s' % ( os.environ["USERDOMAIN"], os.environ["USERNAME"] )
    # import my password. The format is 
    # password = ''
    from mypassword import password
    pacfile = 'proxy.pac'
    url = sys.argv[1]    
    
    geturl(url,user,password,pacfile) 

