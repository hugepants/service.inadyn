# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import sys
import os
import signal
import xbmc
import xbmcaddon

# DEBUG
DEBUG = True

__addon__ = xbmcaddon.Addon()
__plugin__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__path__ = __addon__.getAddonInfo('path')
__cachedir__ = __addon__.getAddonInfo('profile')
__settings__ = __addon__.getSetting

# Get settings
INADYN_START = __settings__('INADYN_START')
INADYN_SYSTEM = __settings__('INADYN_SYSTEM')
INADYN_UPDATE = int(__settings__('INADYN_UPDATE')) * 60
INADYN_HOST = __settings__('INADYN_HOST')
INADYN_USER = __settings__('INADYN_USER')
INADYN_PWD = __settings__('INADYN_PWD')
INADYN_DBG = __settings__('INADYN_DBG')

INADYN_EXEC = '%s/bin/inadyn' % __path__
INADYN_LOG = '%sinadyn.log' % xbmc.translatePath(__cachedir__)
INADYN_PID = '%sinadyn.pid' % xbmc.translatePath(__cachedir__)


def check(process):
  if os.path.isfile(INADYN_PID):
    pid = int(open(INADYN_PID, 'r').read())
    return True, pid
  else:
    return False, None


def execute(arg):
  p = Popen(arg, shell=False, stdout=PIPE, close_fds=True)
  pid = p.pid + 1
  p.communicate()
  if pid:
    return True, pid


def kill(pid):
  os.kill(int(pid), signal.SIGUSR1)
  os.unlink(INADYN_PID)


def log(description):
  xbmc.log("[SERVICE] '%s v%s': DEBUG: %s" % (__plugin__, __version__, description.encode('ascii', 'ignore')), xbmc.LOGNOTICE)


def notification(title, message, image=__icon__, displaytime=6000):
  xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": {"title": "%s", "message": "%s", "image": "%s", "displaytime": %i}, "id": "%s"}' % \
                      (title, message, image, displaytime, __addon__.getAddonInfo('id')))

inadyn = [INADYN_EXEC, \
          '--period', str(INADYN_UPDATE), \
          '--system', INADYN_SYSTEM, \
          '--alias', INADYN_HOST, \
          '--username', INADYN_USER, \
          '--password', INADYN_PWD, \
          '--logfile', INADYN_LOG, \
          '--pidfile', INADYN_PID, \
          '--verbose', INADYN_DBG, \
          '--background', ]

# if not executable change permission
if not os.access('%s/bin/inadyn' % __path__, os.X_OK):
  os.chmod('%s/bin/inadyn' % __path__, 0755)

# check settings is allowing for service start with xbmc
if INADYN_START == 'true':
  # check if inadyn already running. If running find pid number
  _status, _pid = check('inadyn')
  if not _status:
      # Start service
      status, _pid = execute(inadyn)
      if status:
        if DEBUG:
          log('inadyn starting!')
  else:
    if DEBUG:
      log('inadyn already running!')

  while (not xbmc.abortRequested):
    xbmc.sleep(bool(0.250))

  # kill inadyn before xbmc
  kill(_pid)
  if DEBUG:
    log('inadyn stoping!')
  xbmc.sleep(1)
  sys.exit()
else:
  if DEBUG:
    log('inadyn service disabled from settings!!!')
  #notification(__plugin__, 'inadyn service disabled from settings!!!')