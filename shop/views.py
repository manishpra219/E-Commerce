from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Product, Contact, Orders, OrderUpdate
from .utils import verify_signature  # your Razorpay signature verification logic
from math import ceil
import json
import razorpay
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt

# mac/shop/views.py


def terms(request):
    return render(request, 'policies/terms.html')

def refund(request):
    return render(request, 'policies/refund.html')

def shipping(request):
    return render(request, 'policies/shipping.html')

def privacy(request):
    return render(request, 'policies/privacy.html')

def contact_policy(request):
    return render(request, 'policies/contact_policy.html')



def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(nSlides), nSlides])

        # allProds.append([prod, range(1, nSlides), nSlides])
    return render(request, 'shop/index.html', {'allProds': allProds})

def searchMatch(query, item):
    query = query.lower()
    return query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower()

def search(request):
    query = request.GET.get('search', '')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if prod:
            allProds.append([prod, range(nSlides), nSlides])

            # allProds.append([prod, range(1, nSlides), nSlides])
    if not allProds or len(query) < 4:
        return render(request, 'shop/search.html', {'msg': "Please enter a relevant search query"})
    return render(request, 'shop/search.html', {'allProds': allProds, "msg": ""})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})

def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if order.exists():
                updates = OrderUpdate.objects.filter(order_id=orderId)
                updates_list = [{'text': item.update_desc, 'time': item.timestamp} for item in updates]
                response = json.dumps({"status": "success", "updates": updates_list, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except:
            return HttpResponse('{"status":"error"}')
    return render(request, 'shop/tracker.html')

def productView(request, myid):
    product = Product.objects.filter(id=myid).first()
    return render(request, 'shop/prodView.html', {'product': product})
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        amount = int(float(request.POST.get('amount', '')) * 100)
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # 1. Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})

        # 2. Save Django Order with Razorpay order ID
        order = Orders(
            items_json=items_json, name=name, email=email,
            address=address, city=city, state=state,
            zip_code=zip_code, phone=phone, amount=amount / 100,
            razorpay_order_id=payment['id']
            
           
           

        )
        order.save()

        return render(request, 'shop/razorpay_checkout.html', {
            'payment': payment,
            'order': order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        })

    return render(request, 'shop/checkout.html')


def verify_signature(params_dict):
    try:
        key = bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8')
        msg = f"{params_dict['razorpay_order_id']}|{params_dict['razorpay_payment_id']}"
        generated_signature = hmac.new(key, msg.encode(), hashlib.sha256).hexdigest()
        return generated_signature == params_dict['razorpay_signature']
    except Exception as e:
  
        return False
    



@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            if verify_signature(params_dict):
                try: 
                   

                    order = Orders.objects.get(razorpay_order_id=razorpay_order_id)
                    order.razorpay_payment_id = razorpay_payment_id
                    
                    order.paid = True
                    order.save()

                    return render(request, 'shop/paymentstatus.html', {
                        'status': 'success',
                        'razorpay_payment_id': razorpay_payment_id,
                        'razorpay_order_id': razorpay_order_id,
                        'order_id': order.order_id,  # ✅ Safely using 'order'
                    })

                except Orders.DoesNotExist:
                    return render(request, 'shop/paymentstatus.html', {
                        'status': 'error',
                        'message': 'Order does not exist'
                    })

            else:
                return render(request, 'shop/paymentstatus.html', {
                    'status': 'failure'
                })

        except Exception as e:
            # ⚠️ Don't use `order` here because it might not be defined
            return render(request, 'shop/paymentstatus.html', {
                'status': 'error',
                'message': str(e)
            })
