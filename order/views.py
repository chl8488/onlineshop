from django.shortcuts import render,get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import OrderCreateForm

# Create your views here.
# 주문정보입력받고 완료하는페이지, 자바스크립이 동작하지않는 환경에선 이뷰가 호출
# 링크(버튼)를 클릭해서 페이지가 전환됬을때 order정보를 만들어주는 뷰
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        #입력받은 정보를 후처리
        form = OrderCreateForm(request.POST)
        if form.is_valid():# 폼이멀쩡하다면
            order = form.save()
            if cart.coupon:
                order.coupon = cart.coupon
                # 해당주문에 할인금액이 해당카트에들어가있는 쿠폰에 amount만큼들어가있도록되있음
                #order.discount = cart.coupon.amount 이건 할인가격이 확실할때
                # 할인가격이 확실하지 않을떄(더 안전함)
                order.discount = cart.get_discount_total()
                order.save() # 자바스크립이안될때 동작
            for item in cart:
                OrderItem.objects.create(order=order,product=item['product'],
                                         price=item['price'],quantity=item['quantity'])
            cart.clear() #주문완료되면 장바구니 비우기
            return render(request,'order/created.html'
                          ,{'order':order})

    else:# get방식 주만자 정보를 입력받는 페이지
        form = OrderCreateForm()
    return render(request,'order/create.html',{'cart':cart
        ,'form':form})

# 자바스크립트가 동작하지 않는 환경에서도 주문이 가능해야한다. ex)해외
# 완료 로직이 있느냐없느냐 차이
def order_complete(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id)# get_object_or_404 해도 상관없음
    #get_object_or_404(Order, id=order_id)
    return render(request,'order/created.html', {'order':order})


from django.views.generic.base import View
from django.http import JsonResponse
# 버튼을눌러서 호출하는게 아니고 화면전환없이 자바스크립을 통해 호출될 뷰
class OrderCreateAjaxView(View):
    # 클래스뷰같은경우 디스패치:(post,get(http method)따라 분기를해주는것)
    # 함수형 뷰에서는 if문을써서 post일때,아닐때 이렇게햇엇는데 클래스형 뷰에서는 디스패치에서 분기를해줌
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated:# 로그인하지 않았을때
            return JsonResponse({'authenticated':False},status=403)

        cart = Cart(request)
        #여기서부턴 위에 order_create 메소드의 form부터 cart.clear까지 로직똑같음
        form = OrderCreateForm(request.POST)
        if form.is_valid():  # 폼이멀쩡하다면
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.get_discount_total()
            order.save()  # 자바스크립이안될때 동작
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'],
                                         price=item['price'], quantity=item['quantity'])
            cart.clear()  # 주문완료되면 장바구니 비우기
            data = {
                'order_id':order.id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=404)

# 트랜잭션을 생성해주는 뷰
class OrderCheckoutAjaxView(View):
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated:# 로그인하지 않았을때
            return JsonResponse({'authenticated':False},status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        amount = request.POST.get('amount')

        try:# 트랜잭션 생성
            merchant_order_id = OrderTransaction.objects.create_new(
                order=order,
                amount=amount
            )
        except:
            merchant_order_id = None

        if merchant_order_id is not None:
            data= {
                'works':True,
                'merchant_id':merchant_order_id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({},status=401)

#결제 완료된 이후에 후처리하는 부분
class OrderImpAjaxView(View):# 제대로된 결제금액으로된게있는지 확인하는 과정
    def post(self,request, *args, **kwargs):
        if not request.user.is_authenticated:  # 로그인하지 않았을때
            return JsonResponse({'authenticated': False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)

        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            trans = OrderTransaction.objects.get(
                order=order,
                merchant_order_id=merchant_id,
                amount=amount
            )
        except:
            trans = None

        if trans is not None:
            trans.transaction_id = imp_id
            #trans.success = True
            trans.save()
            order.paid = True
            order.save()# 여기까지되면 드디어 결제완료,주문완료라고 여길 수 있음

            data = {
                'works':True
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)


# admin detail view(관리자만 접속할 수 있게)
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required #파이썬 코드
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/admin/detail.html', {
        'order':order})

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint # WeasyPrint를 이용해 HTML을 PDF로 저장하기

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('order/admin/pdf.html', {'order':order})
    # 지금부터 pdf내용이 시작이될거라고 브라우저한테 알림
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATICFILES_DIRS[0]+'/css/pdf.css')])
    # css적용을 하지않을거면 stylesheets 필요없음
    return response