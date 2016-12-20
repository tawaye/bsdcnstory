from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
import os.path
from datetime import datetime
import time
import json
from chinesestory.models import *

# Create your views here.

notice_file_path = '/home/tawayee/6677ba-env/sixsevenba/chinesestory/noticefiles/' 

def adminlogin(request):
	context = {}
	if request.user.is_authenticated:
		context['authenticated'] = True
		context['username'] = request.user.username
		return render(request, 'adminlogin.html', context)
		
	elif request.POST:
		if 'adminlogin' in request.POST:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				context['authenticated'] = True
				context['username'] = request.user.username
				return render(request, 'adminlogin.html', context)
			else:
				context['authenticated'] = False
				context['errmsg'] = '用户名或密码错误，请重新登录。'
				return render(request, 'adminlogin.html', context)
	else:
		context['authenticated'] = False
		context['errmsg'] = ''
		return render(request, 'adminlogin.html', context)


def adminlogout(request):
	logout(request)
	return redirect('/chinesestory/admin/')


def createnotice(request):
	current_notice = {}
	context = {}
	if not request.user.is_authenticated:
		return render(request, 'notloggedin.html')
	elif request.POST:
		if 'previewnotice' in request.POST:
			context['isadmin'] = True
			context['isactive'] = True	
			gathering_date = request.POST['gathering_date']
			if checkdate(gathering_date):
				context['isadmin'] = True
				context['isactive'] = True
				current_notice['gathering_date'] = gathering_date
				current_notice['gathering_starttime'] = request.POST['gathering_starttime']
				current_notice['gathering_endtime'] = request.POST['gathering_endtime']
				current_notice['gathering_place'] = request.POST['gathering_place']
				current_notice['gathering_moderator'] = request.POST['gathering_moderator']
				current_notice['gathering_topic'] = request.POST['gathering_topic']
				current_notice['max_groupsize'] = request.POST['max_groupsize']
				current_notice['registration_date'] = request.POST['registration_date']
				current_notice['registration_time'] = request.POST['registration_time']
				record_current_notice(current_notice)
				context.update(current_notice)
				return render(request, 'notice.html', context)
			else:
				context['errmsg'] = 'Invalid date.'
				return render(request, 'error.html', context)
		elif 'publishnotice' in request.POST:
			current_notice = read_current_notice()
			gathering_date = current_notice['gathering_date']
			notice_file = notice_file_path + gathering_date + '.json'
			pFile = open(notice_file, 'w')
			pFile.write(json.dumps(current_notice))
			pFile.close()
			return render(request, 'succeed.html', {})
		elif 'modifynotice' in request.POST:
			current_notice = read_current_notice()
			return render(request, 'createnotice.html', current_notice) 
		else:
			return render(request, 'error.html', {})
	else:
		return render(request, 'createnotice.html', {})

def shownotice(request):
	context = {}
	context['isadmin'] = False
	current_notice = read_current_notice()
	gathering_date = current_notice['gathering_date']
	if gathering_date != '' and datetime.strptime(gathering_date, '%Y-%m-%d').date() >= datetime.today().date():
		context['isactive'] = True
		context.update(current_notice)
		return render(request, 'notice.html', context)
	else:
		context['errmsg'] = 'There is no active notice' + gathering_date 
		return render(request, 'notice.html', context)


def checkdate(date):
	try:
		pDate = datetime.strptime(date, "%Y-%m-%d")
		if pDate.date() >= datetime.today().date():
			return True
		else:
			return False
	except ValueError:
		return False
	

def record_current_notice(notice):
	current_notice = Current_Notice(
		notice_number = 6677,
		gathering_date = notice['gathering_date'],
		gathering_starttime = notice['gathering_starttime'],
		gathering_endtime = notice['gathering_endtime'],
		gathering_place = notice['gathering_place'],
		max_groupsize = notice['max_groupsize'],
		gathering_moderator = notice['gathering_moderator'],
		gathering_topic = notice['gathering_topic'],
		registration_date = notice['registration_date'],
		registration_time = notice['registration_time'],
		
	)

	current_notice.save()
	
	
def read_current_notice():
	current_notice = {}
	count = Current_Notice.objects.all().count()
	if count >= 1:
		noticeDB = Current_Notice.objects.all()[0]
		current_notice['gathering_date'] = noticeDB.gathering_date
		current_notice['gathering_starttime'] = noticeDB.gathering_starttime
		current_notice['gathering_endtime'] = noticeDB.gathering_endtime
		current_notice['gathering_place'] = noticeDB.gathering_place
		current_notice['max_groupsize'] = noticeDB.max_groupsize
		current_notice['gathering_moderator'] = noticeDB.gathering_moderator
		current_notice['gathering_topic'] = noticeDB.gathering_topic
		current_notice['registration_date'] = noticeDB.registration_date
		current_notice['registration_time'] = noticeDB.registration_time
		
	else:
		current_notice['gathering_date'] = ''
		current_notice['gathering_starttime'] = ''
		current_notice['gathering_endtime'] = ''
		current_notice['gathering_place'] = ''
		current_notice['gathering_moderator'] = ''
		current_notice['gethering_topic'] = ''
		current_notice['registration_date'] = ''
		current_notice['registration_time'] = ''
	
	return current_notice
	
	
	
