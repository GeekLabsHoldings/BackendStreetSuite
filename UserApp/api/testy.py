# # from django.core.mail import send_mail
# # from django.conf import settings

# # send_mail(
# #     'Subject here',
# #     'Here is the message yoyo.',
# #     settings.DEFAULT_FROM_EMAIL,
# #     ['asem23yousry@example.com'],
# #     fail_silently=False,
# # )
# import django
# from django.conf import settings

# # Configure Django settings
# settings.configure(
#     DEBUG=True,
#     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend',
#     EMAIL_HOST = 'smtp.gmail.com',
#     EMAIL_PORT = 587,  # Port for SMTP
#     EMAIL_USE_TLS = True,  # Transport Layer Security is required by Gmail
#     EMAIL_HOST_USER = 'Asemgeeklabs@gmail.com',  # Your Gmail address
#     EMAIL_HOST_PASSWORD = 'ASMB2011asmb@' , # Your Gmail password or app-specific password
#     DEFAULT_FROM_EMAIL = 'Asemgeeklabs@gmail.com' , # Default sender email address
# )


# # Initialize Django
# django.setup()

# # Now you can use send_mail
# from django.core.mail import send_mail

# send_mail(
#     'Subject here',
#     'Here is the message yoyo.',
#     settings.DEFAULT_FROM_EMAIL,
#     ['asem23yousry@example.com'],
#     fail_silently=False,
# )
