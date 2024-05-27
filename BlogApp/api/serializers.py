from rest_framework import serializers
from BlogApp.models import Post, Tag
from django.utils.text import slugify


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['caption']

class PostListSerializer(serializers.ModelSerializer):
    post_detail = serializers.HyperlinkedIdentityField(
        view_name='post-detail',
        lookup_field='slug',
        read_only=True
    )

    tags = TagSerializer(many=True)
    author = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()


    
    class Meta:
        model = Post
        fields = ['title', 'description', 'date_posted', 'author', 'image_url', 'time_reading', 'post_detail', 'tags', 'slug' ]
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None

    def get_author(self, obj):
        return {
            'first_name': obj.author.first_name,
            'last_name': obj.author.last_name
        }

class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField()
    contentimage_url = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = "__all__"
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None
        
    def get_contentimage_url(self, obj):
        if obj.contentimage:
            return obj.contentimage.url
        else:
            return None

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        post = Post.objects.create( **validated_data)
        post.slug = slugify(post.title)
        post.time_reading
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

        return self.time_reading
    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer  
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data
        return ret