from django.contrib import admin
from cores.models import (
    CustomUser,
    Book,
    Discussion,
    Comment,
    UserFavoriteBook,
    UserLikedCategories,
    UserProfile
)


admin.site.register(CustomUser)
admin.site.register(Book)
admin.site.register(Discussion)
admin.site.register(Comment)
admin.site.register(UserFavoriteBook)
admin.site.register(UserLikedCategories)
admin.site.register(UserProfile)