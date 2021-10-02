from django.shortcuts import redirect
from django.utils import timezone
#timezone을 사용하면 사용자의 국가에맞게 계산
from django.views.decorators.http import require_POST
from .models import Coupon
from .forms import AddCouponForm

# Create your views here.

@require_POST #(if를 사용해서 POST해도됨)
def add_coupon(request):
    now = timezone.now()
    form = AddCouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            # __iexact= 대소문자가리지 않고 일치하는것
            coupon = Coupon.objects.get(code__iexact = code
                                        ,use_from__lte=now, use_to__gte = now,
                                        active=True)
            # use_from__lte 사용할수있는시간이 현재시점(now)보다 작고
            # use from 과 use_to 사이에 현재시간이 있으면된다.
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('cart:detail')