from django import forms
from django.forms import inlineformset_factory
from .models import Post, PostImage

class PostForm(forms.ModelForm):
    """Main form for Post model"""
    
    class Meta:
        model = Post
        # Added new fields
        fields = ['title', 'content', 'category', 'price', 'is_sold']
        labels = {
            'title': 'Titolo',
            'content': 'Contenuto',
            'category': 'Categoria',
            'price': 'Prezzo',
            'is_sold': 'Venduto'
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class PostImageForm(forms.ModelForm):
    """Form for individual PostImage"""
    
    class Meta:
        model = PostImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control'#,
                #'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp'
            })
        }
    
    def clean_image(self):
        """Validate single image - only for NEW uploads"""
        image = self.cleaned_data.get('image')
        
        # Skip validation if no new file uploaded (existing image or empty)
        if not image or not hasattr(image, 'content_type'):
            return image
        
        # Validate only NEW uploads (UploadedFile objects)
        
        # Check file size (max 5MB)
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                f'Il file "{image.name}" è troppo grande. Max 5MB.'
            )
        
        # Check extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        file_extension = image.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise forms.ValidationError(
                f'Formato .{file_extension.upper()} non supportato. '
                f'Usa: JPG, PNG, GIF, WebP'
            )
        
        # Check MIME type
        allowed_mime = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in allowed_mime:
            raise forms.ValidationError(
                f'Il file "{image.name}" non è un\'immagine valida.'
            )
        
        return image


# Formset: gestisce multipli PostImageForm
PostImageFormSet = inlineformset_factory(
    Post,                    # Parent model
    PostImage,               # Child model
    form=PostImageForm,      # Form per ogni immagine
    fields=['image'],        # Campi del form
    extra=5,                 # Mostra 5 form vuoti
    max_num=5,               # Max 5 immagini totali
    validate_max=True,       # Valida il limite
    can_delete=True          # Permette eliminazione
)