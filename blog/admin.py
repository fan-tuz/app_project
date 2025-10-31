from django.contrib import admin
from .models import Post, PostImage, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class PostImageInline(admin.TabularInline):
    """Mostra le immagini inline nell'admin dei Post"""
    model = PostImage
    extra = 1  # Mostra 1 campo vuoto per aggiungere immagini
    max_num = 5  # Limita a 5 immagini
    fields = ['image', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'date_posted', 'image_count']
    list_filter = ['date_posted', 'author']
    search_fields = ['title', 'content']
    inlines = [PostImageInline]
    
    def image_count(self, obj):
        """Mostra il numero di immagini nella lista"""
        return obj.images.count()
    image_count.short_description = 'Immagini'


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['post', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['post__title']