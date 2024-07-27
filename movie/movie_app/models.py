from django.contrib.auth.models import User
from uuid import uuid4
from pytils.translit import slugify
from .validators import validate_file_extension
from django.db import models
from django.urls import reverse

def unique_slugify(instance, slug):
    # Генератор уникальных SLUG для моделей, в случае существования такого SLUG.
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug

class Movie(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    films = models.FileField(upload_to='films/', validators=[validate_file_extension])
    time_create = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='movies', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('movie', kwargs={'movie_slug': self.slug})

    def save(self, *args, **kwargs):
        # Сохранение полей модели при их отсутствии заполнения
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Фильмы'
        verbose_name_plural = 'Фильмы'
        ordering = ['-time_create', 'title']

class Category(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def save(self, *args, **kwargs):
        # Сохранение полей модели при их отсутствии заполнения
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'
        ordering = ['id']


class CommentMovie(models.Model):
    post = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)

    class Meta():
        db_table = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'