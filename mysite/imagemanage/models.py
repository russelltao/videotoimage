from django.db import models

# Create your models here.
class TopSubject(models.Model):
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=50)
    price = models.IntegerField()
        
    def __unicode__(self):  
        return self.name  
    
    class Meta:
        ordering = ['price']