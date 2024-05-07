from django.db import models
from django.core.validators import MinValueValidator, EmailValidator, MinLengthValidator

class UserProfile(models.Model):
    name = models.CharField(max_length=100, validators=[MinLengthValidator(1)])
    email = models.EmailField(validators=[EmailValidator()])
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)
    age = models.PositiveIntegerField(validators=[MinValueValidator(16)])
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Credit(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Credit - {self.amount} - {self.category}"

class Debit(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    

    def __str__(self):
        return f"Debit - {self.amount} - {self.category}"


