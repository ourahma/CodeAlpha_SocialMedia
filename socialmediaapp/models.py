from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Q


# Profile model to extend user functionality
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    is_private = models.BooleanField(default=False)  # Option for private accounts
    receive_notifications = models.BooleanField(default=True)  # Notification settings
    theme = models.CharField(max_length=10, default='light')  # Options: 'light' or 'dark'
    friends = models.ManyToManyField('self', symmetrical=False, blank=True,default=None) 
    STATUS_TYPES = [
        ('ON LINE', 'on line'),
        ('OFF LINE', 'off line'),
        
    ]
    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='OFF LINE')
    
    
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
    
    def get_unread_messages_count(self):
        return Message.objects.filter(recipient=self.user, is_read=False).count()
    
    def get_unchecked_notifications_count(self):
        return Notification.objects.filter(user=self.user, is_read=False).count()
    
    def make_profile_online(self):
        self.status='ON LINE'
        self.save()
    def make_profile_offline(self):
        self.status='OFF LINE'
        self.save()
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
    
    def comment_count(self):
        return self.comments.count()

    def like_count(self):
        return self.actions_on_post.filter(is_liked=True).count()

    def dislike_count(self):
        return self.actions_on_post.filter(is_disliked=True).count()
    
    def get_comments(self):
        return self.comments.filter(parent__isnull=True)

    # Method to get all replies for a specific comment
    def get_comment_replies(self, comment):
        return comment.replies.all()

    # Method to get a dictionary of comments with their replies
    def get_comments_with_replies(self):
        comments = self.get_comments()
        comments_with_replies = {}
        for comment in comments:
            comments_with_replies[comment] = self.get_comment_replies(comment)
        return comments_with_replies
    
class Page(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    followers = models.ManyToManyField(User, related_name='following_pages', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.owner.username}"

    def follow_page(self, user):
        self.followers.add(user)

    def unfollow_page(self, user):
        self.followers.remove(user)

    def is_followed_by(self, user):
        return self.followers.filter(id=user.id).exists()


# Comment model for user comments on posts
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post}"
    
    def is_reply(self):
        return self.parent is not None
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_notification()
        
        
    def create_notification(self):
        if self.post.user != self.user:  
            Notification.objects.create(
                user=self.post.user,
                notification_type='comment',
                source_user=self.user,
                post=self.post,
            )
        if self.parent and self.parent.user != self.user:
            Notification.objects.create(
                user=self.parent.user,
                notification_type='comment',
                source_user=self.user,
                post=self.post,
            )

# Message model for direct messaging between users
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 
    
    def __str__(self):
        return f"{self.sender} messaged {self.recipient}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_message()
        
    def create_message(self):
        Notification.objects.create(
                user=self.recipient,
                notification_type="message",
                source_user=self.sender,
                post=None,
            )

# Actions On post model for post 
class ActionsOnPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post,  related_name='actions_on_post',on_delete=models.CASCADE,default=None)
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
        self.create_notification(notification_type='like')
        return "Post is liked"
        
    def dislikePost(self):
        self.is_liked=False
        self.is_disliked=True
        self.save()
        self.create_notification(notification_type='dislike')
        return "Post is disliked"
    
    def viewPost(self):
        self.is_viewed=True
        self.save()
    
    
    def create_notification(self, notification_type):
        if self.post.user != self.user:  
            Notification.objects.create(
                user=self.post.user,
                notification_type=notification_type,
                source_user=self.user,
                post=self.post,
            )
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('friend_request', 'Friend Request'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('dislike', 'Dislike'),
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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)