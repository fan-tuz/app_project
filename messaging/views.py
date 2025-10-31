from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post
from .forms import ConversationMessageForm
from .models import Conversation

@login_required
def new_conversation(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    # Can't start a conversation with yourself
    if post.author == request.user:
        return redirect('blog:home')
    
    conversations = Conversation.objects.filter(post=post).filter(members__in=[request.user.id])

    if conversations:
        return redirect('conversation:detail', pk=conversations.first().id)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            # Crucial step.
            conversation = Conversation.objects.create(post=post)
            conversation.members.add(request.user)
            conversation.members.add(post.author)
            conversation.save()

            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('blog:post-detail', pk=post_pk)
    else:
        form = ConversationMessageForm()
    
    return render(request, 'messaging/new.html', {
        'form': form
    })

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])

    return render(request, 'messaging/inbox.html', {
        'conversations': conversations
    })

@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            conversation.save()

            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'messaging/detail.html', {
        'conversation': conversation,
        'form': form
    })