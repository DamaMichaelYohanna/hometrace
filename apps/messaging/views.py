from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q
from properties.models import Property
from notifications.models import send_system_notification, Notification
from .models import Conversation, Message, Enquiry


@login_required
def inbox_view(request):
    """
    Unified messaging inbox showing all conversation threads.
    """
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(agent=request.user)
    ).select_related('buyer', 'agent', 'property').prefetch_related('messages').order_by('-updated_at')

    # Calculate unread counts
    for conv in conversations:
        conv.user_unread_count = conv.unread_count_for_user(request.user)
        conv.other_participant = conv.agent if request.user == conv.buyer else conv.buyer

    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail_view(request, conversation_id):
    """
    Active conversation thread view and message sender.
    """
    conversation = get_object_or_404(
        Conversation.objects.select_related('buyer', 'agent', 'property'),
        id=conversation_id
    )

    if request.user != conversation.buyer and request.user != conversation.agent and not request.user.is_administrator:
        return HttpResponseForbidden("You do not have access to this conversation.")

    # Mark incoming unread messages as read
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            msg = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body
            )
            conversation.save()  # Updates updated_at

            # Send notification to the other party
            recipient = conversation.agent if request.user == conversation.buyer else conversation.buyer
            send_system_notification(
                user=recipient,
                title=f"New message from {request.user.full_name}",
                message=body[:100] + ("..." if len(body) > 100 else ""),
                notification_type=Notification.NotificationType.MESSAGE,
                target_url=f"/messages/{conversation.id}/"
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message_id': str(msg.id),
                    'body': msg.body,
                    'created_at': msg.created_at.strftime('%H:%M'),
                    'sender_name': msg.sender.full_name,
                    'is_me': True
                })

            return redirect('conversation_detail', conversation_id=conversation.id)

    chat_messages = conversation.messages.select_related('sender').order_by('created_at')
    other_party = conversation.agent if request.user == conversation.buyer else conversation.buyer

    context = {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'other_party': other_party,
    }
    return render(request, 'messaging/conversation.html', context)


@login_required
def send_enquiry_view(request, property_slug):
    """
    Creates an Enquiry and establishes a Conversation thread between buyer and agent.
    """
    prop = get_object_or_404(Property, slug=property_slug)

    if request.user == prop.agent:
        messages.warning(request, "You cannot send an enquiry on your own property listing.")
        return redirect('property_detail', slug=property_slug)

    if request.method == 'POST':
        subject = request.POST.get('subject', f"Inquiry regarding {prop.title}").strip()
        message_body = request.POST.get('message', '').strip()

        if not message_body:
            messages.error(request, "Please enter an inquiry message.")
            return redirect('property_detail', slug=property_slug)

        # 1. Create Enquiry record
        enquiry = Enquiry.objects.create(
            buyer=request.user,
            agent=prop.agent,
            property=prop,
            subject=subject,
            message=message_body,
            status='pending'
        )

        # 2. Get or create conversation thread
        conversation, created = Conversation.objects.get_or_create(
            buyer=request.user,
            agent=prop.agent,
            property=prop
        )

        # 3. Add inquiry as first/new message in conversation
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=f"[ENQUIRY: {subject}]\n{message_body}"
        )
        conversation.save()

        # 4. Notify agent
        send_system_notification(
            user=prop.agent,
            title=f"New Property Enquiry on '{prop.title}'",
            message=f"{request.user.full_name}: {message_body[:120]}...",
            notification_type=Notification.NotificationType.ENQUIRY,
            target_url=f"/messages/{conversation.id}/"
        )

        messages.success(request, f"Your inquiry has been sent to {prop.agent.full_name}. You can track responses in your inbox.")
        return redirect('conversation_detail', conversation_id=conversation.id)

    return redirect('property_detail', slug=property_slug)


@login_required
def poll_messages_api(request, conversation_id):
    """
    Lightweight JSON polling endpoint for live chat experience.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user != conversation.buyer and request.user != conversation.agent and not request.user.is_administrator:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_id = request.GET.get('last_id')
    new_messages_query = conversation.messages.select_related('sender').order_by('created_at')

    if last_id:
        try:
            last_msg = Message.objects.get(id=last_id)
            new_messages_query = new_messages_query.filter(created_at__gt=last_msg.created_at)
        except Message.DoesNotExist:
            pass

    # Mark incoming as read
    new_messages_query.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    items = []
    for m in new_messages_query:
        items.append({
            'id': str(m.id),
            'sender_id': str(m.sender.id),
            'sender_name': m.sender.full_name,
            'body': m.body,
            'is_me': m.sender == request.user,
            'created_at': m.created_at.strftime('%H:%M')
        })

    return JsonResponse({'messages': items})
