import os
import uuid

from django.db import models
from django.utils.text import slugify

from social_media import settings


def post_media_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.nickname)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = models.ImageField(upload_to=post_media_file_path, null=True, blank=True)
    hashtag = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title + " created by " + self.user.email


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.title + " liked by " + self.user.email


class Comment(models.Model):
    content = models.CharField(max_length=255)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
