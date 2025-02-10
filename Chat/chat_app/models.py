from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    contact_list = models.ManyToManyField('User', through='Contacts', blank=True, related_name='user_contacts')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
class Contacts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='user')
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact')
    
    def __str__(self):
        return f"{self.user} -> {self.contact}"
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        unique_together = ('user', 'contact')

    
class Messages(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='UserFrom')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='UserTo')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'