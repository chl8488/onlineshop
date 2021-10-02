from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    use_from = models.DateTimeField()# 쿠폰사용기한 (며칠부터 며칠까지)
    use_to = models.DateTimeField()
    # 쿠폰가격대 조정 (0원부터~ 100,000 쿠폰까지)
    amount = models.IntegerField(validators=[MinValueValidator(0)
        , MaxValueValidator(100000)])
    active = models.BooleanField()#쿠폰 사용가능 여부

    def __str__(self):
        return self.code
