# coding=utf-8

from mole import route, run
import werobot

robot = werobot.WeRoBot(token='K5Dtswpte', enable_session=True)
robot.wsgi

@route('/jone/mole')
def index():
    return 'Hello Mole!'