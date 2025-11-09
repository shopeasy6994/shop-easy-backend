from django.contrib import admin
from .models import ItemRequest

@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('item_name', 'customer__username')