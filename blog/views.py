from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Post, Comment
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostValidateSerializer,
    CommentSerializer,
    CommentValidateSerializer,
)


class CustomPagination(PageNumberPagination):
    page_size = 5

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class PostListAPIView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self, request):
        if request.user.is_authenticated:
            return Post.objects.all().order_by('-created_at')
        return Post.objects.filter(is_published=True).order_by('-created_at')

    def get(self, request):
        posts = self.get_queryset(request)
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        data = PostListSerializer(paginated_posts, many=True).data
        return paginator.get_paginated_response(data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={'error': 'Authentication required'}
            )

        serializer = PostValidateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        post = Post.objects.create(
            author=request.user,
            title=serializer.validated_data.get('title'),
            body=serializer.validated_data.get('body'),
            is_published=serializer.validated_data.get('is_published'),
        )

        return Response(
            status=status.HTTP_201_CREATED,
            data=PostDetailSerializer(post).data
        )


class PostDetailAPIView(APIView):
    def get_object(self, request, id):
        try:
            if request.user.is_authenticated:
                return Post.objects.get(id=id)
            return Post.objects.get(id=id, is_published=True)
        except Post.DoesNotExist:
            return None

    def get(self, request, id):
        post = self.get_object(request, id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = PostDetailSerializer(post).data
        return Response(data=data)

    def put(self, request, id):
        post = self.get_object(request, id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={'error': 'Only author can update this post'}
            )

        serializer = PostValidateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        post.title = serializer.validated_data.get('title')
        post.body = serializer.validated_data.get('body')
        post.is_published = serializer.validated_data.get('is_published')
        post.save()

        return Response(
            status=status.HTTP_200_OK,
            data=PostDetailSerializer(post).data
        )

    def delete(self, request, id):
        post = self.get_object(request, id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={'error': 'Only author can delete this post'}
            )

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostCommentAPIView(APIView):
    def get_post(self, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

    def get(self, request, id):
        post = self.get_post(id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(
            post_id=id,
            is_approved=True
        ).order_by('-created_at')

        data = CommentSerializer(comments, many=True).data
        return Response(data)

    def post(self, request, id):
        post = self.get_post(id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={'error': 'Authentication required'}
            )

        serializer = CommentValidateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            body=serializer.validated_data.get('body'),
            is_approved=serializer.validated_data.get('is_approved'),
        )

        return Response(
            status=status.HTTP_201_CREATED,
            data=CommentSerializer(comment).data
        )


class CommentDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return None

    def put(self, request, id):
        comment = self.get_object(id)
        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={'error': 'Only author can update this comment'}
            )

        serializer = CommentValidateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        comment.body = serializer.validated_data.get('body')
        comment.is_approved = serializer.validated_data.get('is_approved')
        comment.save()

        return Response(
            status=status.HTTP_200_OK,
            data=CommentSerializer(comment).data
        )

    def delete(self, request, id):
        comment = self.get_object(id)
        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={'error': 'Only author can delete this comment'}
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  