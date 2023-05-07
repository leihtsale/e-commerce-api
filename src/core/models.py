import os
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import (EmailValidator, MaxValueValidator,
                                    MinLengthValidator, MinValueValidator)
from django.db import models
from django.utils.text import slugify
from PIL import Image

from core.validators import alphanumeric, letters_only


def product_image_file_path(image, filename):
    """
    Generate a UUID file path for an uploaded image
    """
    extension = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{extension}'

    return os.path.join('uploads', 'product', filename)


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

    def create_superuser(
            self, email, password, username, first_name, last_name, **kwargs):

        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        return self.create_user(
            email, password, username, first_name, last_name, **kwargs)


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
    categories = models.ManyToManyField('Category')
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)])
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[
                                MinValueValidator(50)])
    inventory = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(1)])
    description = models.TextField(default='')
    total_sold = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True, upload_to=product_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            max_size = (600, 600)
            img.thumbnail(max_size, Image.ANTIALIAS)
            img.save(self.image.path)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        default=0,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Category | {self.name}'

    class Meta:
        verbose_name_plural = 'Categories'


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
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return Decimal(self.unit_price * self.quantity)

    def __str__(self):
        return f"Cart | {self.product.name}"

    def save(self, *args, **kwargs):
        self.unit_price = self.product.price
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'product')


class Order(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'

    ORDER_STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (CANCELLED, 'Cancelled'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    shipping_info = models.JSONField(null=True, blank=True)
    is_cancelled = models.BooleanField(null=True, blank=True, default=False)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    stripe_checkout_session_id = models.CharField(
        max_length=128, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order | {self.user}"

    def get_total(self):
        total = 0
        order_items = self.order_items.all()

        for item in order_items:
            total += item.get_total()

        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order | {self.product}"

    def get_product_name(self):
        return self.product.name

    def get_total(self):
        return self.quantity * self.unit_price
