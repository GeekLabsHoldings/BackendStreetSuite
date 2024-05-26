from rest_framework import serializers
from BlogApp.models import Post, Tag
from django.utils.text import slugify


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['caption']


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        post = Post.objects.create( **validated_data)
        post.slug = slugify(post.title)
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(caption=tag_data['caption'])
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
    
    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer  
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data
        return ret