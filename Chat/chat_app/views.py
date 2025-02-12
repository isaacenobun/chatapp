import asyncio
from datetime import timedelta
import json
import time
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import transaction

from django.contrib.auth import get_user_model
from django.urls import reverse
users = get_user_model()

from .models import Messages, Contacts

# Create your views here.
def sign_in(request):
    if request.user.is_authenticated:
        return redirect('main')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        
    return render(request, 'sign-in.html')

def sign_out(request):
    logout(request)
    return redirect('sign-in')

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('main')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if users.objects.filter(email=email).exists():
            return redirect('sign-up')
        
        with transaction.atomic():
            user = users.objects.create_user(username=username, password=password, email=email)
            user.save()
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('main')
        
    return render(request, 'sign-up.html')

sent_messages = set()

from asgiref.sync import sync_to_async

async def chat_event_stream():
    global sent_messages
    last_id = 0

    while True:
        await asyncio.sleep(1)  # Avoid blocking

        # Fetch messages synchronously and convert to list
        get_messages = sync_to_async(lambda: list(
            Messages.objects.filter(id__gt=last_id)
            .select_related("user_from", "user_to")  # Optimize related objects
            .order_by("created_at")
        ), thread_sensitive=True)

        messages = await get_messages()

        if messages:
            last_id = messages[-1].id  # Get the last message ID
            for msg in messages:
                # Fetch related object fields safely
                user_from_id = await sync_to_async(lambda: msg.user_from.id, thread_sensitive=True)()
                user_to_id = await sync_to_async(lambda: msg.user_to.id, thread_sensitive=True)()

                data = {
                    "from": user_from_id,
                    "to": user_to_id,
                    "message": msg.message,
                    "time": (msg.created_at + timedelta(hours=1)).strftime("%H:%M %p"),
                }
                yield f"data: {json.dumps(data)}\n\n"
                sent_messages.add(msg.id)
                last_id = msg.id

async def chat_stream(request):
    response = StreamingHttpResponse(chat_event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Prevent buffering in Nginx
    return response

def main(request):
    if request.user.is_authenticated:
        user = request.user
        contacts = Contacts.objects.filter(user=user)
        
        incoming_messages = Messages.objects.filter(user_from=request.user)
        outgoing_messages = Messages.objects.filter(user_to=request.user)
        
        all_messages = incoming_messages | outgoing_messages
        all_messages = all_messages.order_by('created_at')
        
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
        
        try:
            del message_groups[user]
        except:
            pass
        
        contact_group = {contact.contact: message_groups[contact.contact][-1] for contact in contacts if contact.contact in message_groups}
        
        contact_group = dict(sorted(contact_group.items(), key=lambda x: x[1].created_at, reverse=True))
        
        message_groups_json = {str(key): [message.message for message in messages] for key, messages in message_groups.items()}
        
        # print(json.dumps(message_groups_json, indent=4))
        # print (message_groups)
        # print (contact_group)
        
        send_url = reverse('send')
        stream_url = reverse('stream')
        
        context = {
            'stream_url': stream_url,
            'send_url': send_url,
            'json_groups': message_groups_json,
            'groups': message_groups,
            'contacts': contact_group,
            'messages': all_messages,
            'user': user
        }
        return render(request, 'main.html', context)
    
    return redirect('sign-in')

def send(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            message = request.POST.get('message-text').strip()
            receiver_id = request.POST.get('receiver')
            receiver = users.objects.get(pk=receiver_id)
            
            with transaction.atomic():
                message_obj = Messages.objects.create(
                    user_from=request.user,
                    user_to=receiver,
                    message=message,
                )
                return JsonResponse({"success": True, "message": "Form submitted successfully!"})
