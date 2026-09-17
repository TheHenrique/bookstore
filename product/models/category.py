from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title
