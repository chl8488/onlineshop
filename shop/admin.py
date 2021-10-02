from django.contrib import admin
from .models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug']
    prepopulated_fields = {'slug':['name',]}
    # 자바스크립 동작하는 부분(관리자페이지에서 addCatrgory Name에 글자를쓰면 slug부분에 자동으로 똑같이
    # 써지는게 prepopulated_fields가 동작하는것이다.)

admin.site.register(Category, CategoryAdmin)# 1번째방법

@admin.register(Product) # 어너테이션 기법(2번째방법)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug','category','price','stock',
                    'available_display','available_order','created','updated']
    list_filter = ['available_display','created','updated','category']
    prepopulated_fields = {'slug':('name',)}
    list_editable = ['price','stock','available_display','available_order']#목록에서 자주바꾸는건 여기서바꾸겟다 ex)가격,재고