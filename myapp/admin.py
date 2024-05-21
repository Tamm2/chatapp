from django.contrib import admin
from .models import CustomUser,Talk, Inquiry
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Talk)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user','message', 'created_at')
    search_fields = ('name', 'user__username','message')
