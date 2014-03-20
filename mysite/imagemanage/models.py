#coding:utf-8
from django.db import models
import datetime


# Create your models here.
class TopSubject(models.Model):
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=50)
    descinfo = models.CharField(max_length=100)
    keywords = models.CharField(max_length=30, default="昏迷,公主抱,冰恋")
    price = models.IntegerField()
        
    def __unicode__(self):  
        return self.name  
    
    class Meta:
        ordering = ['price']
        
class VideoFolder(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField()
    parent = models.CharField(max_length=255,db_index=True)
    pathname = models.CharField(primary_key=True, max_length=255)
    descinfo = models.CharField(max_length=300)
    modifyTime = models.DateTimeField(default=datetime.datetime.now())
    keywords = models.CharField(max_length=30, default="昏迷,公主抱,冰恋")
    keywordsEng = models.CharField(max_length=30, default="unconscious,carry,OTS,chloro")
        
    def __unicode__(self):  
        return self.name  
    
    class Meta:
        ordering = ['name']
        
class VideoPhoto(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=300)
    price = models.IntegerField()
    keywords = models.CharField(max_length=30, default="昏迷,公主抱,冰恋")
        
    def __unicode__(self):  
        return self.name  
    
    class Meta:
        ordering = ['price']
        