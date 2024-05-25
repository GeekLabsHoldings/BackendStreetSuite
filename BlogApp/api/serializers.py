from rest_framework import serializers
from BlogApp.models import Post, Tag
from UserApp.api.serializers import UserSerializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'caption']


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag_data in tags_data:
            tag = Tag.objects.get_or_create(caption=tag_data['caption'])
            post.tags.add(tag)
        return post
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        if tags_data:
            instance.tags.clear()
            for tag_data in tags_data:
                tag = Tag.objects.get_or_create(caption=tag_data['caption'])
                instance.tags.add(tag)
        return super().update(instance, validated_data)