import hmac
import hashlib

def verify_signature(params_dict, secret=None):
    secret = secret or 'settings.RAZORPAY_KEY_SECRET'

    try:
        payload = f"{params_dict['razorpay_order_id']}|{params_dict['razorpay_payment_id']}"
        generated_signature = hmac.new(
            key=bytes(secret, 'utf-8'),
            msg=bytes(payload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return generated_signature == params_dict['razorpay_signature']
    except Exception as e:
        print("Signature Verification Error:", str(e))
        return False
