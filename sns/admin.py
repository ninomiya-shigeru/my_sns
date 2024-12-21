from django.contrib import admin
from .models import Message,Friend,Group,Good,Joinfriend,Video
#from .models import CustomUser

admin.site.register(Message)
admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Good)
admin.site.register(Joinfriend)
admin.site.register(Video)
