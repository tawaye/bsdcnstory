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

# Create your views here.

current_notice = {}
active_notice = '2016-12-31'
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
	if not request.user.is_authenticated:
		return render(request, 'notloggedin.html')
	elif request.POST:
		context = {}
		if 'previewnotice' in request.POST:
			gathering_date = request.POST['gathering_date']
			if checkdate(gathering_date):
				context['isadmin'] = True
				current_notice['gathering_date'] = gathering_date
				current_notice['gathering_place'] = 'xxx'
				context.update(current_notice)
				return render(request, 'notice.html', context)
			else:
				context['errmsg'] = 'Invalid date.'
				return render(request, 'error.html', context)
		elif 'publishnotice' in request.POST:
			gathering_date = current_notice['gathering_date']
			notice_file = notice_file_path + gathering_date + '.json'
			pFile = open(notice_file, 'w')
			pFile.write(json.dumps(current_notice))
			pFile.close()
			active_notice = current_notice['gathering_date']
			return render(request, 'succeed.html', {})
		elif 'modifynotice' in request.POST:
			return render(request, 'createnotice.html', current_notice) 
		else:
			return render(request, 'error.html', {})
	else:
		return render(request, 'createnotice.html', {})

def shownotice(request):
	context = {}
	context['isadmin'] = False
	if active_notice != '' and datetime.strptime(active_notice, '%Y-%m-%d').date() >= datetime.today().date():
		context['isactive'] = True
		context.update(current_notice)
		return render(request, 'notice.html', context)
	else:
		context['errmsg'] = 'There is no active notice' + active_notice
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
	
