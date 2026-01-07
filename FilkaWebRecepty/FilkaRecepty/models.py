from django.db import models
from django.db.models import Count
from django.db.models import F, Count

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

from io import BytesIO
import PIL
from PIL import Image

from django.core.files import File
import os
import shutil
from django.db.models.signals import post_delete
from django.dispatch import receiver

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
            
        ('User_edit', 'User_edit'),
        ('Editor', 'Editor'),
        ('Admin', 'Admin'),
        ('User_readOnly', 'User_readOnly'),
    )
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(_("role"),max_length=15, choices=ROLE_CHOICES, default='User_edit')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email




class FoodTags(models.Model):
    foodTag = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.foodTag  

class Steps(models.Model):
    food = models.ForeignKey("Foods", on_delete=models.CASCADE, related_name="steps")
    step = models.CharField(max_length=1500, unique=False)
    position = models.DecimalField(max_digits=10, decimal_places=0)
    # stposition = models.DecimalField(max_digits=10, decimal_places=0)
    
    def __str__(self):
        return self.step           

class Unit(models.Model):
    unit = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.unit    
              
 
class Ingredient(models.Model):
    ingredient = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.ingredient 
    
class Url(models.Model):
    food = models.ForeignKey("Foods", on_delete=models.CASCADE, related_name="urls")
    url = models.URLField(max_length=1000, unique=False)
    
    def __str__(self):
        return self.url 

class Ingredients(models.Model):
    units = models.ManyToManyField(Unit, related_name='units')
    quantity = models.CharField(max_length=60)
    ingredientName = models.ManyToManyField(Ingredient, related_name='ingredientName')
    position = models.DecimalField(max_digits=10, decimal_places=0)
    # ingreposition = models.DecimalField(max_digits=10, decimal_places=0)
    def __str__(self):
        return self.quantity 
  


def get_upload_path(instance, filename):
    return '/'.join(['image', str(instance.upload_folder), filename])

class ImageFood(models.Model):
    food = models.ForeignKey("Foods", on_delete=models.CASCADE, related_name="images")
    upload_folder = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True, upload_to=get_upload_path, verbose_name ="Food image")
    position = models.DecimalField(max_digits=10, decimal_places=0)


    def save(self, * args, **kwargs):
            super().save( * args, **kwargs)
            if self.image:
                img= Image.open(self.image.path)
                fixed_height = 1000
                height_percent = (fixed_height / float(img.size[1]))
                width_size = int( float(img.size[0]) * float(height_percent) )
                img = img.resize((width_size, fixed_height), PIL.Image.NEAREST)
                img.save(self.image.path,optimize=True, quality=80)

                
    def __str__(self):
        return self.upload_folder
    
    def __unicode__(self):
        return self.upload_folder 

    def image_img(self):
        if self.image:
            return u'<img src="%s" width="50" height="50" />' % self.image.url 
        else:
            return '(Sin imagen)'
    image_img.short_description = 'Thumb'
    image_img.allow_tags = True    

    def delete(self, *args, **kwargs):
        """Delete image file and clean up folder if empty"""
        if self.image and os.path.isfile(self.image.path):
            file_path = self.image.path
            folder = os.path.dirname(file_path)

            # delete the file
            os.remove(file_path)

            # if folder is now empty, remove it
            if not os.listdir(folder):
                shutil.rmtree(folder)

        super().delete(*args, **kwargs) 
        
@receiver(post_delete, sender=ImageFood)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        file_path = instance.image.path
        folder = os.path.dirname(file_path)

        os.remove(file_path)

        if not os.listdir(folder):
            shutil.rmtree(folder)         

class Foods(models.Model):
    name = models.CharField(max_length=60)
    # images=models.ManyToManyField(ImageFood, related_name='images',blank=True)
    ingredients = models.ManyToManyField(Ingredients, related_name='ingredients')
    # steps=models.ManyToManyField(Steps, related_name='steps')
    # urls=models.ManyToManyField(Url, related_name='urls',blank=True)
    date = models.DateTimeField()
    foodTags = models.ManyToManyField(FoodTags, related_name='foodTags')
    user = models.ManyToManyField(CustomUser, related_name='user')
    

    def __str__(self):
        return self.name


class PasswordReset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #  return self.user
        return f"Password reset for {self.user.email} at {self.created_when}"



