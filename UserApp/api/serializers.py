from rest_framework import serializers
from rest_framework.reverse import reverse
from UserApp.models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    
    password_confirmation = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [ 'username','email', 'first_name', 'last_name', 'password', 'password_confirmation']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
        }
        
    def update(self, instance, validated_data):
        # Update user and profile
        # instance.username = validated_data.get('username', instance.username)
        # instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()

        return instance

    def save(self):
        password = self.validated_data['password']
        password_confirmation = self.validated_data['password_confirmation']
        if password != password_confirmation:
            raise serializers.ValidationError('Passwords do not match.')
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError('email is already exists')

        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.first_name = self.validated_data['first_name']
        account.last_name = self.validated_data['last_name']
        account.set_password(password)
        account.save()
        return account
    
class ProfileSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ['user','About', 'Phone_Number']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        
        # Update the User instance
        if user_data:
            user = instance.user
            user.username = user_data.get('username', user.username)
            # user.email = user_data.get('email', user.email)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        # Update the Profile instance
        instance.About = validated_data.get('About', instance.About)
        instance.Phone_Number = validated_data.get('Phone_Number', instance.Phone_Number)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        from BlogApp.api.serializers import PostListSerializer 
        representation = super().to_representation(instance)
        user_posts = instance.user.posts.all()
        posts_data = []
        request = self.context.get('request')
        for post in user_posts:
            post_data = PostListSerializer(post, context={'request': request}).data
            post_data['url'] = reverse('post-detail', kwargs={'slug': post.slug}, request=request)
            posts_data.append(post_data)
        representation['posts'] = posts_data
        return representation