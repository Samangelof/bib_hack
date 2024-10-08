from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Менеджер для пользовательской модели, где email используется в качестве уникального идентификатора для аутентификации.
    """
    def create_user(self, email, phone_number, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email должен быть указан'))
        if not full_name:
            raise ValueError(_("Full_name должен быть указан "))
        
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser должен иметь is_superuser=True.'))

        return self.create_user(email, phone_number, full_name, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_ROLE_USER = 'user'
    USER_ROLE_MODERATOR = 'moderator'
    USER_ROLE_SUPERUSER = 'superuser'

    USER_ROLES = [
        (USER_ROLE_USER, _('User')),
        (USER_ROLE_MODERATOR, _('Moderator')),
        (USER_ROLE_SUPERUSER, _('Superuser')),
    ]

    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    full_name = models.CharField(_("full_name"), max_length=255, unique=False, null=False)

    role = models.CharField(
        _('role'),
        max_length=20,
        choices=USER_ROLES,
        default=USER_ROLE_USER
    )
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email
    

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('biography'), blank=True)
    profile_image = models.ImageField(_('profile image'), upload_to='profiles/', blank=True, null=True)
    website = models.URLField(_('website'), blank=True)

    def __str__(self):
        return f'Profile of {self.user.email}'
    
    # получения всех комментариев и избранных книг пользователя
    def get_favorite_books(self):
        return self.user.favorite_books.all()

    # Получение всех комментариев пользователя
    def get_comments(self):
        return Comment.objects.filter(author=self.user)

    # Получение всех лайкнутых категорий
    def get_liked_categories(self):
        return self.user.liked_categories.all()

    # Получение всех лайкнутых авторов
    def get_liked_authors(self):
        return self.user.liked_authors.all()

class Book(models.Model):
    isbn13 = models.CharField(_('ISBN 13'), max_length=13, unique=True)
    isbn10 = models.CharField(_('ISBN 10'), max_length=10, unique=True)
    title = models.CharField(_('Title'), max_length=255)
    subtitle = models.CharField(_('Subtitle'), max_length=255, blank=True, null=True)
    authors = models.CharField(_('Authors'), max_length=255)
    categories = models.CharField(_('Categories'), max_length=255, blank=True, null=True)
    thumbnail = models.URLField(_('Thumbnail URL'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    published_year = models.PositiveIntegerField(_('Published Year'), blank=True, null=True)
    average_rating = models.DecimalField(_('Average Rating'), max_digits=3, decimal_places=2, blank=True, null=True)
    num_pages = models.PositiveIntegerField(_('Number of Pages'), blank=True, null=True)
    ratings_count = models.PositiveIntegerField(_('Ratings Count'), blank=True, null=True)

    def __str__(self):
        return self.title

    
# ----------------
class Discussion(models.Model):
    book = models.ForeignKey(Book, related_name='discussions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# ----------------
class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.author.email} on {self.discussion.title}"

# ----------------

class UserLikedCategories(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='liked_categories')
    category = models.CharField(null=False, max_length=255)

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = _('User Liked Category')
        verbose_name_plural = _('User Liked Categories')

    def __str__(self):
        return f"{self.user.user.email} likes {self.category}"

# ----------------

class UserLikedAuthors(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='liked_authors')
    author = models.CharField(null=False, max_length=255)

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = _('User Liked Author')
        verbose_name_plural = _('User Liked Authors')

    def __str__(self):
        return f"{self.user.email} likes {self.author}"

# ----------------
# избранные
class UserFavoriteBook(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = _('Favorite Book')
        verbose_name_plural = _('Favorite Books')

    def __str__(self):
        return f"{self.user.email} added {self.book.title} to favorites"
