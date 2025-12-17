from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User

    # 1. Columns to display in the list view
    list_display = ('email', 'phone_number', 'is_staff', 'is_active', 'date_joined')

    # 2. Filters available in the right sidebar
    list_filter = ('is_staff', 'is_active', 'groups')

    # 3. Fields to search for
    search_fields = ('email', 'phone_number')

    # 4. Default ordering
    ordering = ('email',)

    # 5. Layout for the "Edit User" page
    # Note: 'username' is removed, 'email' acts as the identifier
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('phone_number',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # 6. Layout for the "Add User" page
    # This determines what fields appear when you click "Add User"
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password'),
        }),
    )

    # 7. Make date_joined read-only (since it is auto_now_add)
    readonly_fields = ('date_joined', 'last_login')