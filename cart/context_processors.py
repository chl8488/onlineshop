# 모든 템플릿에서 필요한 내용이 있을경우에 불러다쓰려고 사용하는 것
# cart 뷰에 def detail 의 'cart':cart 처럼 새로운 뷰를 만들떄마다 작업을해줘야함
# cart메뉴는 글로벌 네비게이션이기때문에
from .cart import Cart

def cart(request):
    cart = Cart(request)
    return {'cart':cart}
# 일반 뷰에서는 render(request,'cart/detail.html', {'cart':cart1})
# 처럼 템플릿파일에 cart':cart 변수들을 적용하지만 context processor 는 변수만 필요
