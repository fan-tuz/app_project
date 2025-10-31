from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q # New import to support complex queries
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.db import transaction
from .models import Post, PostImage, Category
from .forms import PostForm, PostImageFormSet

class PostListView(ListView): # Homepage.
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        """Filter posts by search query and category"""
        # Base queryset
        posts = Post.objects.filter(is_sold=False).select_related('author', 'category')
        
        # Search filter
        query = self.request.GET.get('query', '').strip()
        if query:
            posts = posts.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        
        # Category filter
        category_id = self.request.GET.get('category', '').strip()
        if category_id and category_id.isdigit():
            posts = posts.filter(category_id=int(category_id))
        
        return posts.order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Add categories and filter values to context"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['query'] = self.request.GET.get('query', '').strip()
        context['category_id'] = self.request.GET.get('category', '').strip()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create post with formset for images"""
    model = Post
    form_class = PostForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = PostImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = PostImageFormSet()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # Validate both form and formset
        if not formset.is_valid():
            return self.form_invalid(form)
        
        # Save everything in a transaction (atomic)
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()  # Save post first
            
            formset.instance = self.object  # Link formset to post
            instances = formset.save()  # Save images
            
            image_count = len([i for i in instances if i and i.image])
            
            if image_count > 0:
                messages.success(self.request, f'Post creato con {image_count} immagine/i!')
            else:
                messages.success(self.request, 'Post creato!')
        
        return redirect(self.object.get_absolute_url())
    
    def form_invalid(self, form):
        messages.error(self.request, 'Errore nella validazione del form.')
        return super().form_invalid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update post with formset for images"""
    model = Post
    form_class = PostForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = PostImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['formset'] = PostImageFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            return self.form_invalid(form)
        
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()
            
            formset.instance = self.object
            instances = formset.save()
            
            # Count new images (exclude deletions)
            new_images = [i for i in instances if i and i.image and not formset.deleted_forms]
            
            if new_images:
                messages.success(self.request, f'Post aggiornato con {len(new_images)} modifica/e!')
            else:
                messages.success(self.request, 'Post aggiornato!')
        
        return redirect(self.object.get_absolute_url())
    
    def form_invalid(self, form):
        messages.error(self.request, 'Errore nella validazione.')
        return super().form_invalid(form)
    
    def test_func(self):
        return self.request.user == self.get_object().author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object().author


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})