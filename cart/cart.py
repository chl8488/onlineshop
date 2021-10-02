from decimal import Decimal
from django.conf import settings

from shop.models import Product
from coupon.models import Coupon

class Cart(object):
    def __init__(self, request):#초기화 작업
        self.session = request.session
        cart = self.session.get(settings.CART_ID)
        if not cart:
            cart = self.session[settings.CART_ID] = {}
        self.cart = cart # 현재카트는 세션에서불러온 카트 혹은 새로만든카트
        self.coupon_id = self.session.get('coupon_id')

    def __len__(self):# 장바구니에 10개의 상품이 담겨있습니다 메시지출력(len메서드만 호출하면 되도록만듦)
        return sum(item['quantity'] for item in self.cart.values())
        # 카트에 제품들이담겨있으면 그안에는 quantity라는 항목이 있을텐데 그것들을 전부다 더해주겠다.

    def __iter__(self):# for문 같은걸 사용할때 어떤요소들을 어떤식으로 건네줄지
        product_ids = self.cart.keys() # 제품들의 번호목록 불러오기

        products = Product.objects.filter(id__in=product_ids)
        # 장바구니에 들어있었다고한 제품들에 해당하는애들만 주세요라는 메시지
        # product_ids 리스트안에 id가 들어있는 애들만 걸러서 주세요 어디서 제품들중에서
        # 장바구니에 들어있는 제품들만 db에서 빼옴
        for product in products:
            self.cart[str(product.id)]['product'] = product# 세션에 키값으로집어넣을때 글자로만들어서 넣어줌

        for item in self.cart.values(): #장바구니에 들어있는 제품들 하나씩꺼냄
            item['price'] = Decimal(item['price']) #제품가격은
            item['total_price'] = item['price'] * item['quantity']

            yield item #

    def add(self, product, quantity=1, is_update=False):# 제품을 장바구니에 집어넣는 메서드
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity':0, 'price':str(product.price)} # 제품정보가없을떈 담는 if문
        if is_update: #수정(이 quantity로 제품량을 수정)
            self.cart[product_id]['quantity'] = quantity
        else:# 업데이트(수정)이 아닐경우 제품수량을 더해줘라
            self.cart[product_id]['quantity'] += quantity

        self.save() # 업데이트된것을 저장

    def save(self): # settings.CART_ID에 정보업데이트
        self.session[settings.CART_ID] = self.cart
        self.session.modified = True #변경사항있을때 써줌(장고에서 세션에 변경사항있을떄 처리)

    def remove(self,product): #장바구니에서 제품삭제
        product_id = str(product.id)
        if product_id in self.cart: # 제품에카트에들어있는지 찾는다
            del(self.cart[product_id])
            self.save()

    def clear(self): #장바구니 비우기
        self.session[settings.CART_ID] = {}
        self.session['coupon_id'] = None
        self.session.modified = True

    def get_product_total(self): #장바구니에 들어있는 가격의 총합
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())
        # 처음에들어갈때 데시몰타입은 세션에저장할수 없어서 str로 바꿔서 넣음
    #쿠폰
    @property # get방식으로불러와서 .coupon이나 .coupon.amount를 불러와 사용할 수 있다.
    def coupon(self): # 쿠폰내용 전달
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount_total(self):# 쿠폰으로 얼마나할인되는지
        if self.coupon:
            if self.get_product_total() >= self.coupon.amount: # 총금액이 쿠폰(0~10만)보다 크거나 같으면
                return self.coupon.amount # 쿠폰만큼 할인을하게 계산
        return Decimal(0)# 쿠폰없으면 0원할인

    def get_total_price(self): # discount_total 과 product_total 가지고 실제 결제하는금액
        return self.get_product_total() - self.get_discount_total()