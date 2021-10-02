import csv
import datetime

from django.contrib import admin
from .models import Order,OrderItem
from django.http import HttpResponse

# 이액션은 csv파일로 다운받는 액션
# modeladmin, request, queryset(어떤애들이 선택되서 오느냐) 정해져있음
def export_to_csv(modeladmin, request, queryset):#액션은 함수로만들어 등록
    opts = modeladmin.model._meta #필드정보를 얻어올수있음(.meta)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.' \
                                      'csv'.format(opts.verbose_name)

    writer = csv.writer(response)
    # 일반정보(textField,CharField 등(숫자나 글자만들어있는애들만) 뽑아서 field에넣어주겟다)
    fields = [field for field in opts.get_fields() if not field
              .many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            # isinstance 는 어떤객체가 어떤오브젝트에 실제 어떤클래스에 자식이맞느냐 구분
            if isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d")
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV' #이 액션의 이름


# forienKey로 연결된 다른 model을 같이 수중하기위해 inlines 사용
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] #


from django.urls import reverse
from django.utils.safestring import mark_safe
# reverse= 주소를생성해줌,
# mark_safe= 관리자페이지목록에 원래는 html노출이 안되게 돼있는데 이걸쓰면 html을 보여줌(안전하게)
def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    html = mark_safe(f"<a href='{url}'>Detail</a>")
    return html
# 항목의 헤더가바뀜(short_description)
order_detail.short_description = 'Detail'

def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    html = mark_safe(f"<a href='{url}'>PDF</a>")
    return html
order_pdf.short_description = 'PDF'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id','first_name','last_name','email','address'
        ,'postal_code','city','paid',order_detail
        ,order_pdf,'created','updated'
    ]
    list_filter = ['paid','created','updated']
    inlines = [OrderItemInline] #
    actions = [export_to_csv] # 관리자페이지에서 (Action:) 목록추가

admin.site.register(Order, OrderAdmin)

