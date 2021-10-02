from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .forms import AddProductForm
from .cart import Cart
from coupon.forms import AddCouponForm
# decorators는 함수형뷰에 전처리를 해주는 부분
# require_POST post로만 접근할수있게 걸어주는 부분

# Create your views here.
@require_POST
def add(request, product_id):
    cart = Cart(request) #request를 왜 쓰느냐 거기안에 세션 키정보들이 들어있다.
    # 내가 다루는 나만의 공간으로 할당된 세션공간에 작업을 하는것이기때문에 쓴다
    product = get_object_or_404(Product, id=product_id)
    # 지금은 템플릿을 랜더링하는 형태로짜기때문에 이렇게함 API방식으로하면 제품이없습니다 메시지를 띄움

    # 클라이언트 -> 서버로 데이터를 전달
    # 유효성검사(injection 공격에 대한 전처리)를 하기엔 너무 코드가많기때문에 그런직업을 대신해주는 작업이 form이다
    # 노출되는 폼으로도 쓰임(버튼을 노출, 제출받은 데이터), 사용자로부터 뭔가 입력받을때(회원가입,로그인 등등)
    form = AddProductForm(request.POST)

    if form.is_valid(): # 오타 주의 vaild X --> valid
        cd = form.cleaned_data # 내부에 sql인젝션같은 처리가끝난 데이터가 튀어나오게됨
        cart.add(product=product, quantity=cd['quantity'], is_update=cd['is_update'])

    return redirect('cart:detail')

def remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product,id=product_id)
    cart.remove(product)
    return redirect('cart:detail')

def detail(request):
    cart = Cart(request)
    add_coupon = AddCouponForm()
    for product in cart:
        product['quantity_form'] = AddProductForm(initial={
            'quantity':product['quantity'], 'is_update':True})
    return render(request,'cart/detail.html', {'cart':cart,
                                               'add_coupon':add_coupon})

