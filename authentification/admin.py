from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import LoginHistory, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(SimpleHistoryAdmin):
    list_display = ["user", "telefone", "cpf"]
    search_fields = ["user__username", "user__email", "cpf"]
    raw_id_fields = ["user"]


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "ip", "success", "timestamp"]
    list_filter = ["success"]
    search_fields = ["user__username", "ip"]
    readonly_fields = ["user", "ip", "user_agent", "timestamp", "success"]
    date_hierarchy = "timestamp"
