from rest_framework import serializers
from BlogApp.models import Post, Category
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','text']
        ref_name = 'BlogAppCategory'
class PostListSerializer(serializers.ModelSerializer):
    post_detail = serializers.HyperlinkedIdentityField(
        view_name='post-detail',
        lookup_field='slug',
        read_only=True
    )

    categories = CategorySerializer(many=True)
    author = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'date_posted', 'author', 'image_url', 'time_reading', 'post_detail', 'categories', 'slug', ]
    
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
    categories = CategorySerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField()
    contentimage_url = serializers.SerializerMethodField()
    class Meta:
        model = Post
        exclude =['slug']
    
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
        categories_data = validated_data.pop('categories')
        post = Post.objects.create( **validated_data)
        post.slug = slugify(post.title)
        post.time_reading
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(text=category_data['text'])
            post.categories.add(category)
        return post
    
    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        if categories_data:
            instance.categories.clear()
            for category_data in categories_data:
                category = Category.objects.get_or_create(text=category_data['text'])
                instance.categories.add(category)
        return super().update(instance, validated_data)

        
    def to_representation(self, instance):
        from UserApp.api.serializers import UserSerializer  
        ret = super().to_representation(instance)
        ret['author'] = UserSerializer(instance.author).data 
        return ret