from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.db import transaction

from django.contrib.auth import get_user_model
users = get_user_model()

from .models import Messages, Contacts

# Create your views here.
def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        
    return render(request, 'sign-in.html')

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if users.objects.filter(username=username).exists():
            return redirect('sign-up')
        
        with transaction.atomic():
            user = users.objects.create_user(username=username, password=password, email=email)
            user.save()
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('main')
        
    return render(request, 'sign-up.html')

def main(request):
    if request.user.is_authenticated:
        user = request.user
        contacts = Contacts.objects.filter(user=user)
        
        incoming_messages = Messages.objects.filter(user_from=request.user)
        outgoing_messages = Messages.objects.filter(user_to=request.user)
        
        all_messages = incoming_messages | outgoing_messages
        all_messages = all_messages.order_by('-created_at')
        
        message_groups = {}
        
        for message in all_messages:
            if message.user_from not in message_groups:
                message_groups[message.user_from] = [message]
            else:
                message_groups[message.user_from].append(message)
            
            if message.user_to not in message_groups:
                message_groups[message.user_to] = [message]
            else:
                message_groups[message.user_to].append(message) 
        
        del message_groups[user]
        
        contact_group = {contact.contact: message_groups[contact.contact][0] for contact in contacts if contact.contact in message_groups}
        
        print (contact_group)
        
        context = {
            'groups': message_groups,
            'contacts': contact_group,
            'messages': all_messages,
            'user': user
        }
        return render(request, 'MY CHATS.html', context)
    
    return redirect('sign-in')