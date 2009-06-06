#!/usr/bin/python
'''These program creates a RSS2 xml from a given directory
 20090410 - pmoranga
             Initial Version
 20090415 - pmoranga
             Reads config with ConfigParser

TODO: Config from args

'''


import os
import re
import sys
import time
import PyRSS2Gen
import datetime
import ConfigParser
from stat import *

'''Places where config file can exist'''
configfiles =  [ "./ls2rss.cfg", os.path.expanduser("~")+"/.ls2rss.cfg", "/etc/ls2rss.cfg" ]


'''parameters to read from config file'''
params = [ ('title','s'),  ('description','s'),  ('baseurl','s'),\
               ('root','s'),   ('maxdepth','i'),     ('outfile','s'),\
               ('maxdays','i'),('showleaf','b'),     ('recursive','b'),\
               ('dateformat','s'), ('valid_extension','s') ]
def help():
  print("usage: "+sys.argv[0]+" [file.cfg]\n"+ \
            "  or create config file at:")
  for f in configfiles:
    print ("    "+f)
#  print ("required parameters are:")
#  for  

'''Append fisrt argument to the possible config files'''
if (len(sys.argv) > 1):
  configfiles.insert(0,sys.argv[1])
'''Verifies which config file exists'''
for f in configfiles:
  if (os.path.exists(f)):
    cfgfile=f
    break
if 'cfgfile' not in globals():
  help()
  exit(1)

print "Reading config file: "+cfgfile

try:
  cfgreader = ConfigParser.ConfigParser()
  cfgreader.readfp(open(cfgfile))
  cfg = {}

  for v,type in params:
    if (type == 'i'): 
      cfg[v] = cfgreader.getint('DEFAULT',v)
    elif (type == 'b'): 
      cfg[v] = cfgreader.getboolean('DEFAULT',v)
    else: 
      cfg[v] =  cfgreader.get('DEFAULT',v)

except ConfigParser.NoOptionError, e:
  print "Needed options not set into cfg file: " + e.option
  exit(1)

print cfg

class item:
    '''Class that identify an item'''
    def __init__(self,file,timestamp):
      self.file = file
      self.timestamp = timestamp
    def get_timestamp(self):
      return self.timestamp
    def get_file(self):
      return self.file
    def get_mdate(self):
      return time.strftime(cfg['dateformat'], time.gmtime(self.timestamp))

mintimestamp = time.time() - (cfg['maxdays'] * 60*60*24)
vext = re.compile( cfg['valid_extension'] )

'''The set of items'''
filelist = [ ]

def processDir(dirname,deep):
  '''Process childs from a directory and call itself for each subdir, until "maxdeep.'''
  global cfg, vext
  for file in os.listdir(dirname):
    f = os.path.join( dirname,file )
    if (deep < cfg['maxdepth'] and os.path.isdir(f)):
      processDir(f, deep+1)
    else:
      #print file + " " +  str( vext.match( file ))
      if (vext.match( file ) or (cfg['showleaf'] and os.path.isdir(f) )):
        mtime =  os.stat(f)[ST_MTIME]
        i = item(f,mtime)
        filelist.append(i)


'''First process all files.'''
processDir(cfg['root'],0)

'''Sort the list by timestamp'''
filelist.sort(key=lambda i: i.timestamp)
filelist.reverse()


rss = PyRSS2Gen.RSS2(
    title = "RSS hellraiser",
    link = cfg['baseurl'],
    description = "Hellraiser's Feed",
    lastBuildDate = datetime.datetime.now() )


for i in filelist:
  if (i.get_timestamp() > mintimestamp):
    f = i.get_file()
    print ("%s %s" % ( i.get_mdate(),i.get_file() ))
    f = f.replace(cfg['root'],cfg['baseurl'])
    rss.items.append(
      PyRSS2Gen.RSSItem(
                title = f.replace(cfg['baseurl'] ,'/'),
                #"This is Item 1",
                link = f,
                guid = f,
                pubDate = datetime.datetime.fromtimestamp(i.get_timestamp())    
      ))


rss.write_xml(open(cfg['outfile'],"w"))
rss.write_xml(sys.stdout)
print "\n"
