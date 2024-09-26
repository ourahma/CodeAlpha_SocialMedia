from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
# views to reset password
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.forms import *

from django.template.loader import render_to_string
from django.core.mail import send_mail

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q



@login_required
def dashboard(request):
    posts=Post.objects.filter()
    user=request.user
    
    return render(request,'index.html',{
        'user':user,
        'posts':posts,
        
    })
@login_required
def base(request):
    user=request.user
    return render(request,'base.html',{
        'user':user
    })
## log user in
def login_user(request):
    
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        
        
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            request.user.profile.make_profile_online()
            messages.success(request,("You have been logged in "))
            return redirect('dashboard')
        else:
            messages.error(request,"Email or password are wrong ")
            return redirect('login_user')
    else:
        if request.user.is_authenticated:
            return redirect('dashboard')   
        else:
            return render(request, 'login.html')
    
    
## register user

def register_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name= request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        email = request.POST['email']
        profile_picture = request.FILES.get('profile_picture')
        # Check if the username is unique
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')
        try:
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
                
            profile = Profile.objects.get(user=user)
            if profile_picture:
                profile.profile_picture = profile_picture  
            profile.save()

            
            login(request, user)
            request.user.profile.make_profile_online()
            messages.success(request, "Your account has been created successfully!")
            return redirect('dashboard')
        except Exception as e:
                messages.error(request,'User Already exist !')
                return redirect('register')
    else:
        if request.user.is_authenticated:
            return redirect('dashboard')   
        else:
            return render(request, 'login.html')  
    
    
## log out user

def logout_user(request):
    request.user.profile.make_profile_offline()
    logout(request)
    messages.success(request,("You have been log out"))
    return redirect('login_user')



@login_required
def add_post(request):
    
    if request.user.is_authenticated:
        user=request.user
        if request.method == 'POST':
            
            image=request.FILES.get("image")
            content=request.POST["content"]
            video=request.FILES.get("video")
            post= Post.objects.create(user=user,content=content,image=image,video=video)
            post.save()
            messages.success(request,'Posta dded successfully ! ')
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return HttpResponseRedirect(referer)
            else:
                return redirect('dashboard') 
        else:
            return redirect("dashboard")
        
        
        
@login_required
def mark_post_as_viewed(request, post_id):
    if request.is_ajax():
        try:
            post = Post.objects.get(id=post_id)
            action, created = ActionsOnPost.objects.get_or_create(post=post, user=request.user)
            if not action.is_viewed:
                action.is_viewed = True
                action.save()
            return JsonResponse({"success": True}, status=200)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post does not exist"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)



@login_required
@require_POST
def add_comment_ajax(request, post_id):
    
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')

    if content:
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        # Return JSON response for success
        return JsonResponse({
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'error': 'Invalid input.'}, status=400)

@login_required
@require_POST
def like_post(request,post_id):
    
    post= get_object_or_404(Post,id=post_id)
    action, created = ActionsOnPost.objects.get_or_create(user=request.user, post=post)
    action.likePost()
    action.save()    
    return JsonResponse({})

@login_required
@require_POST
def dislike_post(request,post_id):
    
    post= get_object_or_404(Post,id=post_id)
    action, created = ActionsOnPost.objects.get_or_create(user=request.user, post=post)
    action.dislikePost()
    action.save()    
    return JsonResponse({})


@login_required
@require_POST
def delete_comment(request):
    comment_id=request.POST.get('comment_id')
    print(comment_id)
    comment=get_object_or_404(Comment,id=comment_id)
    comment.delete()
    return JsonResponse({"message":'comment deleted successfully : '})

@login_required
@require_POST
def add_reply(request):
    if request.method == "POST" :
        post_id=request.POST.get("post_id")
        comment_id=request.POST.get('comment_id')
        post = get_object_or_404(Post, id=post_id)
        parent_comment = get_object_or_404(Comment, id=comment_id)
        content = request.POST.get('content')
        if parent_comment.user == request.user:
            messages.info(request,"You cannot reply to your own comment.")
            return JsonResponse({'success': False, 'error': 'You cannot reply to your own comment.'}, status=403)
        
        if content:
            
            reply = Comment.objects.create(
                post=post,
                user=request.user,
                content=content,
                parent=parent_comment,  # This sets the parent comment
            )
            return JsonResponse({'success': True, 'content': reply.content, 'created_at': reply.created_at})

    return JsonResponse({'success': False}, status=400)


### display page of friends

def friends(request):
    friends=request.user.profile.get_friends()
    print("firnds",friends)
    nonfriends=request.user.profile.get_non_friends()
    friendsrequest=request.user.profile.get_received_friend_requests()
    excluded_users = FriendRequest.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        status__in=['pending', 'accepted']
    ).values_list('sender_id', 'recipient_id')

    # Flatten the queryset of tuples to get a list of user IDs
    excluded_user_ids = set()
    for sender_id, recipient_id in excluded_users:
        excluded_user_ids.add(sender_id)
        excluded_user_ids.add(recipient_id)

    # Exclude these user IDs from the User queryset
    users = User.objects.exclude(id__in=excluded_user_ids).exclude(id=request.user.id)
    countrequest=users.count()
    sentrequests=request.user.profile.get_sent_friend_requests()
    return render(request,"friends.html",{
        'friends':friends,
        'nonfriends':nonfriends,
        'friendsrequests':friendsrequest,
        "users":users,
        'sentrequests':sentrequests,
        'countrequest':countrequest
    })
    
    
    
### save friends requests

@login_required
@require_POST
def send_friend_request(request):
    user_to_add_id = request.POST.get('user_id')
    user_to_add = User.objects.get(id=user_to_add_id)
    profile = request.user.profile
    existing_request = FriendRequest.objects.filter(sender=request.user, recipient=user_to_add, status='pending').first()
    if existing_request:
        messages.info(request,'You have send your request and it\'s pending!  ')
        return JsonResponse({'success': False, 'message': 'Failed to send friend request.'})
    
    if user_to_add and user_to_add != request.user:
        profile.send_friend_request(user_to_add)
        messages.success(request,'Friend request sent successfully ! ')
        return JsonResponse({'success': True, 'message': 'Friend request sent.'})
    messages.error(request,'Failed to send friend request.')
    return JsonResponse({'success': False, 'message': 'Failed to send friend request.'})


@login_required
@require_POST
def delete_friend_request(request):
    id = request.POST.get('id')
    friendrequest=FriendRequest.objects.get(id=id)
    friendrequest.delete()
    messages.success(request,"Friend Request deleted successffully ! ")
    return JsonResponse({'success':True,'message':'deleted'})

@login_required
@require_POST
def confirm_friend_request(request):
    profile=request.user.profile
    request_id=request.POST.get('id')
    friend_request=FriendRequest.objects.get(id=request_id)
    profile.accept_friend_request(friend_request)
    messages.success(request,"User now is your friend")
    return JsonResponse({'success':True,'message':"confirmed"})



@login_required
def inbox(request):
    notifications=Notification.objects.filter(user=request.user)
    friends=request.user.profile.get_friends()
    
    return render(request,"inbox.html",{
        "notifications":notifications,
        "friends":friends
    })