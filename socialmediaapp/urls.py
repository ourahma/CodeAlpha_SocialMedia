
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    
    path('',views.dashboard,name='dashboard'),
    path('base/',views.base,name='base'),
    
    ## authentication urls
    path("login/",views.login_user,name="login_user"),
    path("register/",views.register_user,name="register"),
    path('logout/',views.logout_user,name='logout_user'),
    
    ## publish a post
    path('post/',views.add_post, name="post"),
    
    ## mark a post as viewed suign ajax
    path('post/<int:post_id>/view/', views.mark_post_as_viewed, name='mark_post_as_viewed'),
    
    ## add a comment
    path('post/<int:post_id>/add_comment/', views.add_comment_ajax, name='add_comment'),
    
    ## like a post
    path('post/<int:post_id>/like_post/', views.like_post, name='like_post'),
    
    ## dislike a post
    path('post/<int:post_id>/dislike_post/', views.dislike_post, name='dislike_post'),
    
    ## delete a comment
    path('post/delete_comment/',views.delete_comment,name="delete_comment"),
] 
