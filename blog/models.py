from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image as PILImage


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    # Last kwarg allows me to write post.images.all() to get all images of a post, by creating an inverse relation in DB
    image = models.ImageField(upload_to='post_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    # Resize image on save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = PILImage.open(self.image.path)

        if img.height > 800 or img.width > 800:
            output_size = (800, 800)
            img.thumbnail(output_size)
            img.save(self.image.path)