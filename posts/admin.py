from django.contrib import admin

from .models import BlogPost, BlogPostComment, Carousel, CarouselComment

admin.site.register(BlogPost)
admin.site.register(BlogPostComment)
admin.site.register(Carousel)
admin.site.register(CarouselComment)
