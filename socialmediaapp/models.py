from django.db import models


from django.contrib.auth.models import User
from django.db import models

# Profile model to extend user functionality
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    is_private = models.BooleanField(default=False)  # Option for private accounts
    receive_notifications = models.BooleanField(default=True)  # Notification settings
    theme = models.CharField(max_length=10, default='light')  # Options: 'light' or 'dark'
    friends = models.ManyToManyField('self', symmetrical=False, blank=True) 
    
    def __str__(self):
        return f"{self.user.id} {self.user.username}"
    
    def add_friend(self, friend_profile):
        if not self.is_friends(friend_profile):
            self.friends.add(friend_profile)

    def remove_friend(self, friend_profile):
        if self.is_friends(friend_profile):
            self.friends.remove(friend_profile)

    def is_friends(self, friend_profile):
        return self.friends.filter(id=friend_profile.id).exists()

# Post model to handle user posts
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)  # For images
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)  # For videos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}"

# Comment model for user comments on posts
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post}"

# Message model for direct messaging between users
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.sender} messaged {self.recipient}"

# Actions On post model for post 
class ActionsOnPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)
    is_disliked = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.post.id} "
    def likePost(self):
        self.is_liked=True
        self.is_disliked=False
        self.save()
        return "Post is liked"
        
    def dislikePost(self):
        self.is_liked=False
        self.is_disliked=True
        self.save()
        return "Post is disliked"
    
    def viewPost(self):
        self.is_viewed=True
        self.save()
    
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('friend_request', 'Friend Request'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who will receive the notification
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    source_user = models.ForeignKey(User, related_name='notifications_source', on_delete=models.CASCADE)  # User who triggered the notification
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # The post related to the notification
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for the notification
    is_read = models.BooleanField(default=False)  # Track whether the notification has been read

    def __str__(self):
        return f"{self.source_user} {self.notification_type} to {self.user}"

