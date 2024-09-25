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



@login_required
def dashboard(request):
    posts=Post.objects.filter(user=request.user)
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
            messages.error(request,"There was an error, please try again ")
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