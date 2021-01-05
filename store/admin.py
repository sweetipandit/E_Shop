from django.contrib import admin

# Register your models here.
from store.models import Tshirt ,Payment,Order,OrderItem ,Cart, Brand , Color , IdealFor , NeckType , Occasion , Sleeve, SizeVariant



class SizeVariantConfigration(admin.TabularInline):
    model = SizeVariant

class TshirtConfigration(admin.ModelAdmin):
    inlines = [ SizeVariantConfigration ]
    list_display = ['name','slug','description','descount','image']


admin.site.register(Tshirt, TshirtConfigration)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(IdealFor)
admin.site.register(NeckType)
admin.site.register(Occasion)
admin.site.register(Sleeve)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
