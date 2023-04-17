from core.validators import alphanumeric, letters_only
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import (EmailValidator, MaxValueValidator,
                                    MinLengthValidator, MinValueValidator)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(
            self, email, password, username,
            first_name, last_name, **kwargs):

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **kwargs)
        user.set_password(password)
        user.full_clean()
        user.save()

        return user

    def create_superuser(self, email, password, **kwargs):

        admin = self.create_user(email, password, **kwargs)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        return admin


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model where email is the primary identifier
    """

    first_name = models.CharField(
        max_length=128,
        validators=[letters_only, MinLengthValidator(2)]
    )
    last_name = models.CharField(
        max_length=128,
        validators=[letters_only, MinLengthValidator(2)]
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        validators=[alphanumeric, MinLengthValidator(2)]
    )
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=255,
        validators=[letters_only, MinLengthValidator(2)])
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField()
    description = models.TextField(default='')
    rating = models.PositiveSmallIntegerField(
        default=None,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='carts',
    )
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"Cart | {self.product.name}"

    def save(self, *args, **kwargs):
        self.unit_price = self.product.price
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'product')
