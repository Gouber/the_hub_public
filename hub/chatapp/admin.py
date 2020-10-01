from django.contrib import admin
from .models import Chat, Conversation


class ConversationAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Chat)
admin.site.register(Conversation, ConversationAdmin)

# Register your models here.
