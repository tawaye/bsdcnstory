from django.db import models

# Create your models here.
class Current_Notice(models.Model):
	published = models.BooleanField()
	district = models.CharField(max_length = 12, primary_key=True) 
	gathering_date = models.CharField(max_length = 12)
	gathering_starttime = models.CharField(max_length = 12)
	gathering_endtime = models.CharField(max_length = 12)
	gathering_place = models.CharField(max_length = 60)
	gathering_address = models.CharField(max_length = 60)
	max_groupsize = models.IntegerField(default=15)
	gathering_moderator = models.CharField(max_length = 20)
	gathering_topic = models.CharField(max_length = 40)
	registration_date = models.CharField(max_length = 12)
	registration_time = models.CharField(max_length = 12)
	activity_1_exist = models.BooleanField()
	activity_1_info = models.CharField(max_length = 300)
	activity_1_img = models.CharField(max_length = 80)
	activity_1_img_exist = models.BooleanField()
	activity_2_exist = models.BooleanField()
	activity_2_info = models.CharField(max_length = 300)
	activity_2_img = models.CharField(max_length = 80)
	activity_2_img_exist = models.BooleanField()
	activity_3_exist = models.BooleanField()
	activity_3_info = models.CharField(max_length = 300)
	activity_3_img = models.CharField(max_length = 80)
	activity_3_img_exist = models.BooleanField()
	activity_4_exist = models.BooleanField()
	activity_4_info = models.CharField(max_length = 300)
	activity_4_img = models.CharField(max_length = 80)
	activity_4_img_exist = models.BooleanField()
	activity_5_exist = models.BooleanField()
	activity_5_info = models.CharField(max_length = 300)
	activity_5_img = models.CharField(max_length = 80)
	activity_6_exist = models.BooleanField()
	activity_5_img_exist = models.BooleanField()
	activity_6_info = models.CharField(max_length = 300)
	activity_6_img = models.CharField(max_length = 80)
	activity_6_img_exist = models.BooleanField()
	



class Current_Registration(models.Model):
	district = models.CharField(max_length = 12)
	gathering_date = models.CharField(max_length = 12)
	parent_name = models.CharField(max_length = 20)
	num_of_children = models.IntegerField(default = 1)	
	child_name_1 = models.CharField(max_length = 20)
	child_name_2 = models.CharField(max_length = 20)
	child_name_3 = models.CharField(max_length = 20)

