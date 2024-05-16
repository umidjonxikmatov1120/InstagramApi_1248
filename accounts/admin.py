from django.contrib import admin

from accounts.models import UserModel, UserConfirmationModel

admin.register(UserModel)
admin.register(UserConfirmationModel)
