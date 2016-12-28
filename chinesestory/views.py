from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
import os.path
from datetime import datetime
import time
import json
from chinesestory.models import *

# Create your views here.

notice_file_path = '/home/tawayee/6677ba-env/sixsevenba/chinesestory/noticefiles/' 
district_name = {
	'bsdadmin': 'Brossard',
	'logadmin': 'Longueuil',
	'mtladmin': 'Montreal',
}

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

def index(request):
	context = {}
	context['title'] = 'Chinese Story Time'
	return render(request, 'chinesestory.html', context)

def adminlogin(request):
	context = {}
	if request.user.is_authenticated:
		context['authenticated'] = True
		username = request.user.username
		context['username'] = username
		context['district_name'] = district_name[username]
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
				context['district_name'] = district_name[username]
				context['heading'] = '管理员功能'
				context['username'] = request.user.username
				return render(request, 'adminlogin.html', context)
			else:
				context['authenticated'] = False
				context['errmsg'] = '用户名或密码错误，请重新登录。'
				return render(request, 'adminlogin.html', context)
	else:
		context['authenticated'] = False
		context['title'] = 'Brossard中文故事会-管理员登录'
		context['heading'] = '管理员登录'
		return render(request, 'adminlogin.html', context)


def adminlogout(request):
	logout(request)
	return redirect('/chinesestory/admin/')

def viewregistration(request):
	context = {}
	if request.user.is_authenticated:
		context['authenticated'] = True
		username = request.user.username
		context['username'] = username
		district = district_name[username] 
		notice = read_current_notice(district)
		regData = readRegistrationData(district)
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
		username = request.user.username
		district = district_name[username]
		context['district_name'] = district
		
		if 'previewnotice' in request.POST:
			context['isadmin'] = True
			context['isactive'] = True	
			current_notice['published'] = False
			current_notice['district'] = district
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
			current_notice['activity_list'] = []	
			for activity_no in range(6):
				this_activity = {}
				activity_name = 'activity_' + str(activity_no+1)
				if request.POST[activity_name] != '':
					this_activity['activity_name'] = '活动内容 ' + str(activity_no+1)
					this_activity['activity_info'] = request.POST[activity_name] 
					this_activity['exist'] = True
					try: 
						activity_img_name = activity_name + '_img'
						imgfile = request.FILES[activity_img_name]
						filename = request.POST['gathering_date'] + '-' + activity_name
						this_activity['activity_img_url'] = upload_activity_img(filename, imgfile)	
						this_activity['activity_img_exist'] = True
					except:
						this_activity['activity_img_url'] = ''
						this_activity['activity_img_exist'] = False
	
				else:
					this_activity['activity_name'] = activity_name
					this_activity['activity_info'] = request.POST[activity_name] 
					this_activity['exist'] = False
					this_activity['activity_img_url'] = ''
					this_activity['activity_img_exist'] = False
	

				current_notice['activity_list'].append(this_activity)


			errmsgs = checknotice(current_notice)
			if len(errmsgs) == 0: 
				context['isadmin'] = True
				context['isactive'] = True
				context['heading'] = '管理员功能 - 预览通知'
				context.update(current_notice)
				record_current_notice(current_notice)
				return render(request, 'notice.html', context)
			else:
				context['errmsg'] = errmsgs
				return render(request, 'error.html', context)
		elif 'publishnotice' in request.POST:
			current_notice = read_current_notice(district)
			current_notice['published'] = True
			record_current_notice(current_notice)
			current_registration = readRegistrationData(district)
			gathering_date = current_notice['gathering_date']
			notice_file = notice_file_path + district + '-' + gathering_date + '.json'
			pFile = open(notice_file, 'w')
			pFile.write(json.dumps(current_notice))
			pFile.write(json.dumps(current_registration))
			clearRegistrationData(district)
			pFile.close()
			return render(request, 'succeed.html', {})
		elif 'modifynotice' in request.POST:
			current_notice = read_current_notice(district)
			return render(request, 'createnotice.html', current_notice) 
		else:
			return render(request, 'error.html', {})
	else:
		username = request.user.username
		context['district_name'] = district_name[username]
		default_notice = setdefaultnotice()
		context['heading'] = '管理员功能 - 创建新故事会通知'
		context.update(default_notice)
		return render(request, 'createnotice.html', context)

def shownotice(request):
	context = {}
	context['isadmin'] = False
	
	if 'brossard' in request.path:
		district = 'Brossard'
	elif 'longueuil' in request.path:
		district = 'Longueuil'
	elif 'montreal' in request.path:
		district = 'Montreal'
	else:
		district = 'unspecified'

	current_notice = read_current_notice(district)
	regData = readRegistrationData(district)
	if current_notice['published']:
		gathering_date = current_notice['gathering_date']
		if gathering_date != '' and datetime.strptime(gathering_date, '%Y-%m-%d').date() >= datetime.today().date():
			context['isactive'] = True
			context['title'] = district + '中文故事会 ' + gathering_date	
			context['heading'] = district + '故事会通知 ' + gathering_date	
			regDate = datetime.strptime(current_notice['registration_date'], '%Y-%m-%d').date()
			regTime = datetime.strptime(current_notice['registration_time'], '%I:%M %p').time()
			if checkRegistrationTime(regDate, regTime):
				context['registration_allowed'] = True
			else:
				context['registration_allowed'] = False
			context['registration_count'] = regData['count']
			context['registration_list'] = regData['regList']
			context['district_name'] = district
			context.update(current_notice)
			return render(request, 'notice.html', context)
		else:
			context['district_name'] = district
			context['errmsg'] = 'There is no active notice' + gathering_date 
			return render(request, 'notice.html', context)

	else:
		context['district_name'] = district
		context['errmsg'] = 'There is no active notice'
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
				errmsgs.append(errmsg[errcode])
		except ValueError:
			errcode = 6
			errmsgs.apped(errmsg[errcode])
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
	
def upload_activity_img(filename, imgfile):
	fs = FileSystemStorage()
	ext = os.path.splitext(imgfile.name)[1]
	fname = fs.save(filename+ext, imgfile)
	return fs.url(fname)

def record_current_notice(notice):
	current_notice = Current_Notice(
		published = notice['published'],
		district = notice['district'],
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
		
		activity_1_exist = notice['activity_list'][0]['exist'],
		activity_1_info = notice['activity_list'][0]['activity_info'],
		activity_1_img = notice['activity_list'][0]['activity_img_url'],
		activity_1_img_exist = notice['activity_list'][0]['activity_img_exist'],

		activity_2_exist = notice['activity_list'][1]['exist'],
		activity_2_info = notice['activity_list'][1]['activity_info'],
		activity_2_img = notice['activity_list'][1]['activity_img_url'],
		activity_2_img_exist = notice['activity_list'][1]['activity_img_exist'],

		activity_3_exist = notice['activity_list'][2]['exist'],
		activity_3_info = notice['activity_list'][2]['activity_info'],
		activity_3_img = notice['activity_list'][2]['activity_img_url'],
		activity_3_img_exist = notice['activity_list'][2]['activity_img_exist'],

		activity_4_exist = notice['activity_list'][3]['exist'],
		activity_4_info = notice['activity_list'][3]['activity_info'],
		activity_4_img = notice['activity_list'][3]['activity_img_url'],
		activity_4_img_exist = notice['activity_list'][3]['activity_img_exist'],

		activity_5_exist = notice['activity_list'][4]['exist'],
		activity_5_info = notice['activity_list'][4]['activity_info'],
		activity_5_img = notice['activity_list'][4]['activity_img_url'],
		activity_5_img_exist = notice['activity_list'][4]['activity_img_exist'],

		activity_6_exist = notice['activity_list'][5]['exist'],
		activity_6_info = notice['activity_list'][5]['activity_info'],
		activity_6_img = notice['activity_list'][5]['activity_img_url'],
		activity_6_img_exist = notice['activity_list'][5]['activity_img_exist'],

	)

	current_notice.save()
	
	
def read_current_notice(district_name):
	current_notice = {}
	count = Current_Notice.objects.filter(district=district_name).count()
	if count >= 1:
		noticeDB = Current_Notice.objects.filter(district=district_name)[0]
		current_notice['published'] = noticeDB.published
		current_notice['district'] = noticeDB.district
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
		current_notice['activity_list'] = []
		this_activity = {}
		activity_id = 0
		this_activity['exist'] = noticeDB.activity_1_exist
		if this_activity['exist']:
			activity_id = activity_id + 1
			this_activity['activity_name'] = 'Activity ' + str(activity_id)
			this_activity['activity_info'] = noticeDB.activity_1_info 
			this_activity['activity_img_exist'] = noticeDB.activity_1_img_exist 
			this_activity['activity_img_url'] = noticeDB.activity_1_img
			current_notice['activity_list'].append(this_activity)

		this_activity = {}
		this_activity['exist'] = noticeDB.activity_2_exist
		if this_activity['exist']:
			activity_id = activity_id + 1
			this_activity['activity_name'] = 'Activity ' + str(activity_id)
			this_activity['activity_info'] = noticeDB.activity_2_info 
			this_activity['activity_img_exist'] = noticeDB.activity_2_img_exist 
			this_activity['activity_img_url'] = noticeDB.activity_2_img
			current_notice['activity_list'].append(this_activity)

		this_activity = {}
		this_activity['exist'] = noticeDB.activity_3_exist
		if this_activity['exist']:
			activity_id = activity_id + 1
			this_activity['activity_name'] = 'Activity ' + str(activity_id)
			this_activity['activity_info'] = noticeDB.activity_3_info 
			this_activity['activity_img_exist'] = noticeDB.activity_3_img_exist 
			this_activity['activity_img_url'] = noticeDB.activity_3_img
			current_notice['activity_list'].append(this_activity)

		this_activity = {}
		this_activity['exist'] = noticeDB.activity_4_exist
		if this_activity['exist']:
			activity_id = activity_id + 1
			this_activity['activity_name'] = 'Activity ' + str(activity_id)
			this_activity['activity_info'] = noticeDB.activity_4_info 
			this_activity['activity_img_exist'] = noticeDB.activity_4_img_exist 
			this_activity['activity_img_url'] = noticeDB.activity_4_img
			current_notice['activity_list'].append(this_activity)

		this_activity = {}
		this_activity['exist'] = noticeDB.activity_5_exist
		if this_activity['exist']:
			activity_id = activity_id + 1
			this_activity['activity_name'] = 'Activity ' + str(activity_id)
			this_activity['activity_info'] = noticeDB.activity_5_info 
			this_activity['activity_img_exist'] = noticeDB.activity_5_img_exist 
			this_activity['activity_img_url'] = noticeDB.activity_5_img
			current_notice['activity_list'].append(this_activity)

		this_activity = {}
		this_activity['exist'] = noticeDB.activity_6_exist
		if this_activity['exist']:
			activity_id = activity_id + 1
			this_activity['activity_name'] = 'Activity ' + str(activity_id)
			this_activity['activity_info'] = noticeDB.activity_6_info 
			this_activity['activity_img_exist'] = noticeDB.activity_6_img_exist 
			this_activity['activity_img_url'] = noticeDB.activity_6_img
			current_notice['activity_list'].append(this_activity)
		
	else:
		current_notice['published'] = False
		current_notice['district'] = ''
		current_notice['gathering_date'] = ''
		current_notice['gathering_starttime'] = ''
		current_notice['gathering_endtime'] = ''
		current_notice['gathering_place'] = ''
		current_notice['gathering_moderator'] = ''
		current_notice['gathering_topic'] = ''
		current_notice['registration_date'] = ''
		current_notice['registration_time'] = ''
		
		current_notice['activity_list'] = []
						
	return current_notice
	
	
def setdefaultnotice():
	default_notice = {}
	
	default_notice['district'] = ''
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
			
	default_notice['activity_2'] = 'story book'
	default_notice['activity_1'] = '小朋友们自我介绍，然后一起唱故事会开场歌曲《你好歌》\
	曲调：Twinkle Twinkle Little Star \
	词：冯丽丽，汪开娴\ 
	你好，你好，大家好，欢迎你们来这里。\
	唱歌，读书，交朋友，聚在一起多有趣。\你好，你好，大家好，我很高兴认识你！' 
	default_notice['activity_1_img'] = ''
	default_notice['activity_1_img_exist'] = False
	default_notice['activity_2_img'] = ''
	default_notice['activity_2_img_exist'] = False
	default_notice['activity_3'] = 'story book'
	default_notice['activity_3_img'] = ''
	default_notice['activity_3_img_exist'] = False
	default_notice['activity_4'] = ''
	default_notice['activity_4_img'] = ''
	default_notice['activity_4_img_exist'] = False
	default_notice['activity_5'] = ''
	default_notice['activity_5_img'] = ''
	default_notice['activity_5_img_exist'] = False
	default_notice['activity_6'] = ''
	default_notice['activity_6_img'] = ''
	default_notice['activity_6_img_exist'] = False
	
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

def readRegistrationData(district_name):
	regData = {}
	regList = []
	regDB = Current_Registration.objects.filter(district=district_name)
	regCount = regDB.count()
	if regCount >=1:
		ii = 0
		while ii < regCount:
			parent_name = regDB[ii].parent_name		
			num_of_children = regDB[ii].num_of_children
			child_name_1 = regDB[ii].child_name_1
			child_name_2 = regDB[ii].child_name_2
			child_name_3 = regDB[ii].child_name_3
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

def clearRegistrationData(district_name):
	regDB = Current_Registration.objects.filter(district=district_name)
	regDB.delete()
	return

	
	
