from django.db import models
from django.db import models
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    meta_description = models.TextField(blank=True)  # 카테고리에 대한 설명 노출(검색했을때 정보노출)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)  # pk대신에 사용

    class Meta:
        ordering = ['name']  # 이름순으로 정렬 이게없으면 id값으로정렬
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name  # 이 카테고리를 출력하면 나타낼 내용을 설정

    def get_absolute_url(self):
        return reverse('shop:product_in_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    # 카테고리가 삭제되도 상품은보존

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)
    # 슬러그는 보통 제목의 단어들을 하이픈으로 연결해 생성하며, URL에서 pk 대신 사용되는 경우가 많다.
    # pk 를 사용하면 숫자로만 되어있고, 그 내용을 유추하기는 어렵지만, 슬러그를 사용하면 보통의 단어들이라서 이해하기 쉽기 때문이다.
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격 intgerfield(한국가격)
    stock = models.PositiveIntegerField()
    # 재고  0과 양수만 표현할 수 있는 숫자형과 음수도 함께 표현할 수 있는 숫자형으로 나뉜다. 위 두 숫자형은 음수도 표현할 수 있는 숫자형이며,
    # 음수는 다루고 싶지 않다면 각 숫자형 이름 앞에 Positive 를 붙임

    available_display = models.BooleanField('Display', default=True)
    available_order = models.BooleanField('Order', default=True)  # 주문 가능여부

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        index_together = [['id', 'slug']]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


