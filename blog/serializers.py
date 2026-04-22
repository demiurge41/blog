from rest_framework import serializers
from .models import Post, Comment


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'created_at', 'is_published']


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostValidateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, min_length=2, max_length=255)
    body = serializers.CharField(required=True)
    is_published = serializers.BooleanField(default=True)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'body', 'created_at', 'updated_at', 'is_approved']
        read_only_fields = ['post']


class CommentValidateSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    is_approved = serializers.BooleanField(default=True)