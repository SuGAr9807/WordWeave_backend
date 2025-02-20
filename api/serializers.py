from rest_framework import serializers
from .models import User, BlogPost, Tag, Like, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "username", "profile_picture", "is_active"]

class BlogPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field="name"
    )

    class Meta:
        model = BlogPost
        fields = ["post_id", "user", "title", "content", "tags", "created_at"]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["tag_id", "name"]

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=BlogPost.objects.all())

    class Meta:
        model = Like
        fields = ["like_id", "post", "user"]

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=BlogPost.objects.all())

    class Meta:
        model = Comment
        fields = ["comment_id", "post", "user", "text", "created_at"]
