
from django.contrib import admin

class ReadOnlyAdmin (admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return False
    def has_delete_permission(self, *args, **kwargs):
        return False
    def has_change_permission(self, *args, **kwargs):
        return False
