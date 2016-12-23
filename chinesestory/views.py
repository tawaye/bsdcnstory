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

errmsg = [
	'Success', # errcode = 0
	'The gathering date is not valid', # errcode = 1
	'The start_time is not valid', # errcode = 2
	'The end_time is not valid', # errcode = 3
	'The end_time cannot be earlier than start_time', # errcode = 4
	'The max group size is not valid', # errcode = 5
	'Invalid registration start date', # errcode = 6
	'Invalid registartion start time', # errcode = 7
	'', # errcode = 8
	'Unspecified error', # errcode = 9
]

def adminlogin(request):
	context = {}
	if request.user.is_authenticated:
		context['authenticated'] = True
		context['username'] = request.user.username
		context['heading'] = '管理员功能'
		return render(request, 'adminlogin.html', context)
		
	elif request.POST:
		if 'adminlogin' in request.POST:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				context['authenticated'] = True
				context['heading'] = '管理员功能'
				context['username'] = request.user.username
				return render(request, 'adminlogin.html', context)
			else:
				context['authenticated'] = False
				context['errmsg'] = '用户名或密码错误，请重新登录。'
				return render(request, 'adminlogin.html', context)
	else:
		context['authenticated'] = False
		context['heading'] = '管理员登录'
		return render(request, 'adminlogin.html', context)


def adminlogout(request):
	logout(request)
	return redirect('/chinesestory/admin/')

def viewregistration(request):
	context = {}
	if request.user.is_authenticated:
		context['authenticated'] = True
		context['username'] = request.user.username
		notice = read_current_notice()
		regData = readRegistrationData()
		context['gathering_date'] = notice['gathering_date']
		context['registration_count'] = regData['count']	
		context['registration_list'] = regData['regList']	
		
		return render(request, 'viewregistration.html', context)
	else:
		return render(request, 'notloggedin.html')
		
def createnotice(request):
	current_notice = {}
	context = {}
	if not request.user.is_authenticated:
		return render(request, 'notloggedin.html')
	elif request.POST:
		if 'previewnotice' in request.POST:
			context['isadmin'] = True
			context['isactive'] = True	
			current_notice['gathering_date'] = request.POST['gathering_date']
			current_notice['gathering_starttime'] = request.POST['gathering_starttime']
			current_notice['gathering_endtime'] = request.POST['gathering_endtime']
			current_notice['gathering_place'] = request.POST['gathering_place']
			current_notice['gathering_address'] = request.POST['gathering_address']
			current_notice['gathering_moderator'] = request.POST['gathering_moderator']
			current_notice['gathering_topic'] = request.POST['gathering_topic']
			current_notice['max_groupsize'] = request.POST['max_groupsize']
			current_notice['registration_date'] = request.POST['registration_date']
			current_notice['registration_time'] = request.POST['registration_time']
			errmsgs = checknotice(current_notice)
			if len(errmsgs) == 0: 
				context['isadmin'] = True
				context['isactive'] = True
				context['heading'] = 'Admin function - preview notice'
				context.update(current_notice)
				record_current_notice(current_notice)
				return render(request, 'notice.html', context)
			else:
				context['errmsg'] = errmsgs
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
		default_notice = setdefaultnotice()
		context['heading'] = 'Admin Function - create notice'
		context.update(default_notice)
		return render(request, 'createnotice.html', context)

def shownotice(request):
	context = {}
	context['isadmin'] = False
	current_notice = read_current_notice()
	regData = readRegistrationData()
	gathering_date = current_notice['gathering_date']
	if gathering_date != '' and datetime.strptime(gathering_date, '%Y-%m-%d').date() >= datetime.today().date():
		context['isactive'] = True
		context['title'] = 'Brossard中文故事会 ' + gathering_date	
		context['heading'] = 'Brossard中文故事会 ' + gathering_date	
		regDate = datetime.strptime(current_notice['registration_date'], '%Y-%m-%d').date()
		regTime = datetime.strptime(current_notice['registration_time'], '%I:%M %p').time()
		if checkRegistrationTime(regDate, regTime):
			context['registration_allowed'] = True
		else:
			context['registration_allowed'] = False
		context['registration_count'] = regData['count']
		context['registration_list'] = regData['regList']
		context.update(current_notice)
		return render(request, 'notice.html', context)
	else:
		context['errmsg'] = 'There is no active notice' + gathering_date 
		return render(request, 'notice.html', context)

def registration(request):
	context = {}
	errmsgs = []
	regData = {}
	current_notice = read_current_notice()
	regDate = datetime.strptime(current_notice['registration_date'], '%Y-%m-%d').date()	
	regTime = datetime.strptime(current_notice['registration_time'], '%I:%M %p').time()	
	if not checkRegistrationTime(regDate, regTime):
		errmsgs.append('Too early. Please come back later.')
		context['errmsg'] = errmsgs
		return render(request, 'error.html', context)
	if request.POST:
		regData['parent_name'] = request.POST['parent_name']	
		regData['num_of_children'] = request.POST['num_of_children']	
		regData['child_name_1'] = request.POST['child_name_1']	
		regData['child_name_2'] = request.POST['child_name_2']	
		regData['child_name_3'] = request.POST['child_name_3']	
		if checkRegistrationLimit():
			if checkRegistrationDuplicate(regData['parent_name']):
				saveRegistrationData(regData)
				context['successMsg'] = 'Your registration is accepted.'
				return render(request, 'succeed.html', context)
			else:
				errmsgs.append('The name ' + regData['parent_name'] + 'has already been registered.')	
				context['errmsg'] = errmsgs
				return render(request, 'error.html', context)
		else:
			errmsgs.append('The registration number has reached the limit. New registration is not accpeted')	
			context['errmsg'] = errmsgs
			return render(request, 'error.html', context)
	else:
		context['heading'] = 'Brossard Chinese Story registration'
		return render(request, 'registration.html', context)
	
def checknotice(notice):
	errmsgs = []
	try:
		pDate = datetime.strptime(notice['gathering_date'], "%Y-%m-%d")
		if pDate.date() < datetime.today().date():
			errcode = 1
			errmsgs.append(errmsg[errcode])
		try:
			pRegDate = datetime.strptime(notice['registration_date'], '%Y-%m-%d')
			if pRegDate >= pDate:
				errcode = 6
				errmsgs.apped(errmsg[errocode])
		except ValueError:
			errocode = 6
			errmsgs.apped(errmsg[errocode])
	except ValueError:
		errcode = 1
		errmsgs.append(errmsg[errcode])
	try:
		pStartTime = datetime.strptime(notice['gathering_starttime'], "%I:%M %p")
	except ValueError:
		errcode = 2
		errmsgs.append(errmsg[errcode])
	try:
		pEndTime = datetime.strptime(notice['gathering_endtime'], "%I:%M %p")
	except ValueError:
		errcode = 3
		errmsgs.append(errmsg[errcode])

	try:
		pSize = int(notice['max_groupsize'])
		if pSize <= 0:
			errcode = 5
			errmsgs.append(errmsg[errcode])
	except ValueError:
		errcode = 5
		errmsgs.append(errmsg[errcode])

	try:
		pRegTime = datetime.strptime(notice['registration_time'], "%I:%M %p")
	except ValueError:
		errcode = 7
		errmsgs.append(errmsg[errcode])

	return errmsgs
	

def record_current_notice(notice):
	current_notice = Current_Notice(
		notice_number = 6677,
		gathering_date = notice['gathering_date'],
		gathering_starttime = notice['gathering_starttime'],
		gathering_endtime = notice['gathering_endtime'],
		gathering_place = notice['gathering_place'],
		gathering_address = notice['gathering_address'],
		max_groupsize = int(notice['max_groupsize']),
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
		current_notice['gathering_address'] = noticeDB.gathering_address
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
		current_notice['gathering_topic'] = ''
		current_notice['registration_date'] = ''
		current_notice['registration_time'] = ''
	
	return current_notice
	
	
def setdefaultnotice():
	default_notice = {}
	default_notice['gathering_topic'] = ''
	default_notice['gathering_moderator'] = ''
	default_notice['max_groupsize'] = '15'
	default_notice['gathering_date'] = ''
	default_notice['gathering_starttime'] = '10:00 AM'
	default_notice['gathering_endtime'] = '11:30 AM'
	default_notice['gathering_place'] = 'Bibliotique de Brossard (Brossard图书馆儿童活动区)'
	default_notice['gathering_address'] = '7855 Ave San Francisco, Brossard J4X 2A4'
	default_notice['registration_date'] = ''
	default_notice['registration_time'] = ''
	
	return default_notice
	
	
def checkRegistrationTime(regDate, regTime):
	if datetime.now().date() > regDate:
		return True
	elif (datetime.now().date() == regDate and datetime.now().time() > regTime):
		return True
	else:
		return False

def checkRegistrationLimit():
	noticeData = read_current_notice()
	regLimit = noticeData['max_groupsize']
	regCount = Current_Registration.objects.all().count()
	if regCount >= regLimit:
		return False
	else:
		return True

def checkRegistrationDuplicate(name):
	if Current_Registration.objects.filter(parent_name=name).count() > 0:
		return False
	else:
		return True
	
def saveRegistrationData(regData):
	new_registration = Current_Registration(
		parent_name = regData['parent_name'],
		num_of_children = int(regData['num_of_children']),
		child_name_1 = regData['child_name_1'],
		child_name_2 = regData['child_name_2'],
		child_name_3 = regData['child_name_3']
	)
	new_registration.save()
	return	

def readRegistrationData():
	regData = {}
	regList = []
	regCount = Current_Registration.objects.all().count()
	if regCount >=1:
		ii = 0
		while ii < regCount:
			parent_name = Current_Registration.objects.all()[ii].parent_name		
			num_of_children = Current_Registration.objects.all()[ii].num_of_children
			child_name_1 = Current_Registration.objects.all()[ii].child_name_1
			child_name_2 = Current_Registration.objects.all()[ii].child_name_2
			child_name_3 = Current_Registration.objects.all()[ii].child_name_3
			record = {
				'parent_name': parent_name,
				'num_of_children': num_of_children,
				'child_name_1': child_name_1,
				'child_name_2': child_name_2,
				'child_name_3': child_name_3
			}
			regList.append(record)
			ii = ii + 1

	regData['count'] = regCount
	regData['regList'] = regList	
	return regData


	
	
