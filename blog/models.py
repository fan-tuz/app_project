from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image as PILImage

class Category(models.Model):
    name = models.CharField(max_length=255, default='General')
    # Set a default for Category.name to populate existing records
    # To be removed in production as cactegory is a required field

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Post(models.Model):
    # Adding extra fields to transform posts into products.
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, default=1)
    price = models.FloatField(default=0) # null=True, blank=True kwargs necessary to populate pre-existing rows in DB.
    is_sold = models.BooleanField(default=False)
    
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.pk})
    
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