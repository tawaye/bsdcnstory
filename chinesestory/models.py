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


class Current_Registration(models.Model):
	district = models.CharField(max_length = 12)
	gathering_date = models.CharField(max_length = 12)
	parent_name = models.CharField(max_length = 20)
	num_of_children = models.IntegerField(default = 1)	
	child_name_1 = models.CharField(max_length = 20)
	child_name_2 = models.CharField(max_length = 20)
	child_name_3 = models.CharField(max_length = 20)

