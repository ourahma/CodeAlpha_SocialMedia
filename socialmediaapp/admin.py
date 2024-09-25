from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'is_private', 'receive_notifications')
    search_fields = ('user__username',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user','content','image','video','created_at','updated_at')
    search_fields = ('user__username','content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user','post','content','created_at','parent')
    seach_fields = ('content',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'content', 'created_at')
    search_fields = ('content',)

@admin.register(ActionsOnPost)
class ActionsOnPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'is_liked','is_disliked','is_viewed', 'created_at')
    search_fields = ('post','user')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user','notification_type','source_user','post','created_at','is_read')
    search_fields = ('post','notification_type')
    
    
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display=('owner','title','description','created_at')
    search_fields=('owner','title','description')


