"""
Configuration for Donation Site Scraper Bot.
All settings, API keys, gateway/platform signatures, and search dorks.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API Keys
# ============================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
VALUESERP_API_KEY = os.getenv("VALUESERP_API_KEY", "AB09C976EF514B8396DF6009FAAAD9F4")
BING_API_KEY = os.getenv("BING_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8523232096:AAGh8LA6Wmp2jmIoONuFwt9JgwkOazDDbd0")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7566000469")

# ============================================================
# Timing & Limits
# ============================================================
CYCLE_SLEEP_SECONDS = int(os.getenv("CYCLE_SLEEP_SECONDS", "3600"))      # 1 hour between cycles
FETCH_TIMEOUT = int(os.getenv("FETCH_TIMEOUT", "60"))                     # seconds per page
FETCH_CONCURRENCY = int(os.getenv("FETCH_CONCURRENCY", "100"))             # max concurrent fetches
MAX_RESPONSE_SIZE = 512 * 1024                                             # 500KB body cap
CRAWLER_MAX_DEPTH = 2                                                      # max hops for link crawling
CRTSH_INTERVAL_HOURS = 6                                                   # crt.sh runs every 6h
COMMONCRAWL_INTERVAL_HOURS = 24                                            # Common Crawl daily

# Daily query limits per provider
DAILY_LIMITS = {
    "google": int(os.getenv("GOOGLE_DAILY_LIMIT", "95")),
    "serper": int(os.getenv("SERPER_DAILY_LIMIT", "1600")),      # 50K/mo ≈ 1600/day
    "serpapi": int(os.getenv("SERPAPI_DAILY_LIMIT", "3")),        # 100/mo ≈ 3/day
    "valueserp": int(os.getenv("VALUESERP_DAILY_LIMIT", "16000")),  # 500K/mo
    "bing": int(os.getenv("BING_DAILY_LIMIT", "30")),
}

# SQLite
DB_PATH = os.getenv("DB_PATH", "found_sites.db")

# ============================================================
# Payment Gateway Signatures
# ============================================================
GATEWAY_SIGNATURES = {
    "Braintree": [
        "braintree", "braintree-web", "client.create", "data-braintree",
        "braintree-hosted-fields", "braintree.setup", "bt-hosted-field",
        "braintree.dropin.create", "braintree-dropin", "js.braintreegateway.com",
        "api.braintreegateway.com", "braintree_client_token", "braintreegateway",
        "braintree.client", "bt-dropin",
    ],
    "Cybersource": [
        "cybersource", "flex-microform", "cybs", "cybersource.flex",
        "secureacceptance", "cybersource.com", "flex.cybersource.com",
        "testflex.cybersource.com", "microform.cybersource",
    ],
    "Payflow": [
        "payflow", "payflowlink", "payflow_color", "payflowpro",
        "paypal.com/cgi-bin/webscr", "manager.paypal.com",
        "payflowpro.paypal.com", "pilot-payflowpro.paypal.com",
    ],
    "Spreedly": [
        "spreedly", "spreedly.com", "core.spreedly.com",
        "spreedlyjs", "Spreedly.init", "spreedly.tokenize",
        "spreedly-number", "spreedly-cvv",
    ],
    "Chase": [
        "chase paymentech", "orbital", "safetech",
        "chase.com/payment", "chasepaymentech", "orbital.paymentech.com",
        "orbitalvault", "paymentech",
    ],
    "Adyen": [
        "adyen", "adyen-checkout", "checkoutshopper",
        "adyen.encrypt", "adyen-cse", "checkoutshopper-live.adyen.com",
        "checkoutshopper-test.adyen.com", "adyen-checkout__",
        "adyen.createFromAction", "adyen-payment",
    ],
    "Convergepay": [
        "convergepay", "elavon", "converge.myvirtualmerchant",
        "api.convergepay.com", "myvirtualmerchant", "elavon.com",
        "converge.elavon.com",
    ],
    "AuthorizeNet": [
        "authorize.net", "Accept.js", "acceptjs", "authorizenet",
        "js.authorize.net", "AcceptUI", "Accept.dispatchData",
        "secure.authorize.net", "anet-sdk", "authnet", "acceptHosted",
        "Accept.HostedForm",
    ],
    "Worldpay": [
        "worldpay", "access.worldpay.com", "payments.worldpay.com",
        "secure.worldpay.com", "worldpay-cse", "Worldpay.useTemplateForm",
        "worldpay.com/select", "wpwlOptions",
    ],
    "Moneris": [
        "moneris", "esqa.moneris.com", "www3.moneris.com", "moneris-checkout",
        "monerisjsv2", "moneris.com/HPPtoken", "monerisCheckout",
    ],
    "Bambora": [
        "bambora", "web.na.bambora.com", "api.na.bambora.com", "bamboracheckout",
        "customcheckout.bambora.com", "na.bambora.com",
    ],
    "BlueSnap": [
        "bluesnap", "sandpay.bluesnap.com", "pay.bluesnap.com", "bluesnap-hosted",
        "BluesnapEncryptedPaymentField", "bluesnap.com/services",
        "hostedpaymentfields.bluesnap.com",
    ],
    "Nuvei": [
        "nuvei", "nuvei.com", "ppp.nuvei.com", "secure.safecharge.com",
        "safecharge", "safecharge.com", "nuvei-checkout", "nuveiSDK",
    ],
    "Checkout.com": [
        "checkout.com", "frames.checkout.com", "cdn.checkout.com",
        "Frames.init", "checkout-frames", "cko-card-number",
        "cko-expiry-date", "cko-cvv",
    ],
    "PayU": [
        "payu", "payulatam", "payubiz", "payumoney", "payu.in",
        "secure.payu.com", "payuCheckoutPro", "bolt.js",
        "payuWidgets", "payu.pl",
    ],
    "Razorpay": [
        "razorpay", "checkout.razorpay.com", "Razorpay.open",
        "razorpay-payment", "razorpay.js", "rzp_live_", "rzp_test_",
        "api.razorpay.com",
    ],
    "Payeezy": [
        "payeezy", "api.payeezy.com", "first-data", "firstdata",
        "payeezy.js", "Payeezy.createToken", "fts.firstdata.com",
    ],
    "NMI": [
        "nmi", "secure.networkmerchants.com", "CollectJS", "collectjs",
        "gateway.merchantservicesltd", "secure.nmi.com",
        "collect.js", "nmi-payment",
    ],
    "USAePay": [
        "usaepay", "sandbox.usaepay.com", "secure.usaepay.com",
        "usaepay-form", "PaymentForm.usaepay", "usaepay.com",
    ],
    "CardConnect": [
        "cardconnect", "cardpointe", "api.cardconnect.com",
        "fts-uat.cardconnect.com", "bolt-api.cardconnect.com",
        "cardconnect.com", "cardsecure",
    ],
    "Paysafe": [
        "paysafe", "paysafe.js", "hosted.paysafe.com", "api.paysafe.com",
        "paysafecard", "netbanx", "paysafe.fields",
    ],
    "Clover": [
        "clover", "clover.com", "api.clover.com", "clover-sdk",
        "checkout.clover.com", "clover-payment", "cloverconnector",
    ],
    "Heartland": [
        "heartland", "api.heartlandportico.com", "SecureSubmit",
        "securesubmit", "globalpayments", "hps.js",
        "heartlandpaymentsystems", "heartland-payment",
    ],
    "iATS": [
        "iatspayments", "iats", "www.iatspayments.com",
        "aura.iatspayments.com", "iats-payment",
    ],
    "Blackbaud": [
        "blackbaud", "bbpayments", "blackbaud.com", "sky-api",
        "checkout.blackbaud.com", "bbox.blackbaudhosting.com",
        "bbrequest", "bbcheckout",
    ],
    "Windcave": [
        "windcave", "paymentexpress", "sec.windcave.com", "pxpay",
        "sec.paymentexpress.com", "windcave.com",
    ],
    "Flywire": [
        "flywire", "flywire.com", "payment.flywire.com", "flywire-payment",
    ],
    "TouchNet": [
        "touchnet", "commerce.touchnet.com", "uPay", "touchnet.net",
        "marketplace.touchnet.com", "touchnet-payment",
    ],
    "CashNet": [
        "cashnet", "commerce.cashnet.com", "cashnet.com", "cashnet-payment",
    ],
    "Nelnet": [
        "nelnet", "quikpayasp.com", "myquikpay", "nelnet.com",
    ],
    "PayTrace": [
        "paytrace", "paytrace.com", "api.paytrace.com",
        "paytrace.js", "paytrace-payment",
    ],
    "Vanco": [
        "vancopayments", "vanco", "vancopayment.com", "epaymentamerica",
        "vanco-payment", "givingflow",
    ],
    "Helcim": [
        "helcim", "helcim.com", "api.helcim.com", "helcim-pay",
        "helcimpayjs", "helcimPay",
    ],
    "Shift4": [
        "shift4", "shift4.com", "i4go", "i4go.js", "lighthouse",
        "secure.shift4.com", "shift4sdk", "shift4payment",
    ],
    "OpenEdge": [
        "openedge", "openedgepay.com", "openedge.js",
        "transfirst", "openedge-payment",
    ],
    "PayArc": [
        "payarc", "payarc.net", "payarc.js", "payarc-payment",
    ],
    "Stax": [
        "staxpayments", "stax", "fattmerchant", "stax.js",
        "fattjs", "omni.fattmerchant.com",
    ],
    "ProPay": [
        "propay", "propay.com", "iframes.propay.com",
        "propay-payment", "protectpay",
    ],
    "Payrix": [
        "payrix", "payrix.com", "payrix.js",
        "payrix-payment", "webpay.payrix",
    ],
}

GATEWAY_SHORT = {
    "Braintree": "B3",
    "Cybersource": "CS",
    "Payflow": "PF",
    "Spreedly": "SP",
    "Chase": "CH",
    "Adyen": "AD",
    "Convergepay": "CV",
    "AuthorizeNet": "ANET",
    "Worldpay": "WP",
    "Moneris": "MNR",
    "Bambora": "BMB",
    "BlueSnap": "BSNP",
    "Nuvei": "NUV",
    "Checkout.com": "CKOUT",
    "PayU": "PAYU",
    "Razorpay": "RZP",
    "Payeezy": "PYZ",
    "NMI": "NMI",
    "USAePay": "USAE",
    "CardConnect": "CCNT",
    "Paysafe": "PSFE",
    "Clover": "CLVR",
    "Heartland": "HTLD",
    "iATS": "IATS",
    "Blackbaud": "BBAUD",
    "Windcave": "WNDCV",
    "Flywire": "FLYW",
    "TouchNet": "TCHN",
    "CashNet": "CSHN",
    "Nelnet": "NLNT",
    "PayTrace": "PTRC",
    "Vanco": "VNCO",
    "Helcim": "HLCM",
    "Shift4": "SH4",
    "OpenEdge": "OE",
    "PayArc": "PARC",
    "Stax": "STAX",
    "ProPay": "PPAY",
    "Payrix": "PRIX",
}

# ============================================================
# Platform / CMS Signatures (order matters: specific before generic)
# ============================================================
PLATFORM_SIGNATURES = {
    "WooCommerce": [
        "woocommerce", "wc-ajax", "/wp-content/plugins/woocommerce",
        "wc_add_to_cart", "woocommerce-checkout",
    ],
    "Magento": [
        "mage.", "magento", "/static/frontend/", "varien/js",
        "mage/cookies", "Magento_",
    ],
    "Shopify": [
        "shopify", "cdn.shopify", "myshopify.com",
        "Shopify.theme", "shopify-section",
    ],
    "BigCommerce": [
        "bigcommerce", "cdn11.bigcommerce.com", "stencil-utils",
    ],
    "Squarespace": [
        "squarespace", "static.squarespace.com", "sqs-block",
    ],
    "Wix": [
        "wix.com", "parastorage.com", "wixstatic.com",
    ],
    "WordPress": [
        "wp-content", "wordpress", "wp-includes", "wp-json",
    ],
    "Drupal": [
        "drupal", "sites/default/files", "drupal.js",
    ],
    "Joomla": [
        "joomla", "/media/system/js", "com_content",
    ],
    "Django": [
        "csrfmiddlewaretoken", "django",
    ],
}

PLATFORM_SHORT = {
    "WooCommerce": "WOO",
    "Magento": "MAG",
    "Shopify": "SHOP",
    "BigCommerce": "BC",
    "Squarespace": "SQS",
    "Wix": "WIX",
    "WordPress": "WP",
    "Drupal": "DRP",
    "Joomla": "JML",
    "Django": "DJG",
    "Custom": "CUST",
}

# ============================================================
# Captcha Signatures
# ============================================================
CAPTCHA_SIGNATURES = {
    "reCAPTCHA v2": [
        "g-recaptcha", "www.google.com/recaptcha/api.js",
        "recaptcha/api.js", "g-recaptcha-response",
    ],
    "reCAPTCHA v3": [
        "recaptcha/api.js?render=", "grecaptcha.execute",
        "recaptcha-v3", "recaptcha_v3",
    ],
    "hCaptcha": [
        "hcaptcha", "h-captcha", "js.hcaptcha.com",
        "h-captcha-response",
    ],
    "Cloudflare Turnstile": [
        "challenges.cloudflare.com/turnstile", "cf-turnstile",
        "turnstile-callback",
    ],
    "FunCaptcha": [
        "funcaptcha", "arkoselabs", "arkose",
    ],
    "GeeTest": [
        "geetest", "gt_lib", "initGeetest",
    ],
}

# ============================================================
# 3D Secure Signatures
# ============================================================
THREE_DS_SIGNATURES = {
    "3DS2": [
        "threeDSecure", "three-d-secure", "3dsecure",
        "cardinal", "cardinalcommerce", "songbird",
        "Cardinal.setup", "Cardinal.trigger",
        "threeDS2", "3ds2",
    ],
    "3DS1": [
        "3dsecure", "ThreeDSecure", "visa secure",
        "mastercard identity check", "securecode",
    ],
}

# ============================================================
# AVS Detection Signatures
# ============================================================
AVS_SIGNATURES = {
    "street": [
        "billing_address", "billTo_street", "street_address",
        "address_line_1", "address1", "billing-address",
        "streetAddressVerification", 'name="street"',
        'name="address"', "billing_street",
        'data-braintree-name="streetAddress"',
    ],
    "zip": [
        "billing_zip", "billTo_postalCode", "postal_code",
        "postalCode", "zip_code", "billing-zip",
        "postalCodeVerification", 'name="zip"',
        'data-braintree-name="postalCode"',
    ],
    "city": [
        "billing_city", "billTo_city", 'name="city"',
        "billing-city",
    ],
    "state": [
        "billing_state", "billTo_state", 'name="state"',
        "billing-state", "billing_region",
    ],
}

# ============================================================
# Integration Type Detection
# ============================================================
INTEGRATION_SIGNATURES = {
    "Hosted Fields": [
        "braintree-hosted-fields", "hosted-field-",
        "hostedFields.create", "flex-microform",
        "hosted-session", "adyen-checkout__input",
    ],
    "Drop-in UI": [
        "braintree.dropin.create", "dropin-container",
        "braintree-dropin", "adyen-checkout__dropin",
    ],
    "iFrame": [
        "payment-iframe", "payflow-iframe",
        "secure-payment-frame",
    ],
    "Redirect": [
        "payflowlink", "redirect-to-payment",
        "myvirtualmerchant.com", "securepayments",
    ],
}

# ============================================================
# Server / CDN Detection (from HTTP headers)
# ============================================================
SERVER_HEADERS = {
    "cf-ray": "Cloudflare",
    "cf-cache-status": "Cloudflare",
    "x-sucuri-id": "Sucuri WAF",
    "x-sucuri-cache": "Sucuri WAF",
    "x-amz-cf-id": "AWS CloudFront",
    "x-vercel-id": "Vercel",
    "x-netlify-request-id": "Netlify",
    "fly-request-id": "Fly.io",
}

SERVER_NAMES = {
    "nginx": "Nginx",
    "apache": "Apache",
    "litespeed": "LiteSpeed",
    "microsoft-iis": "IIS",
    "cloudflare": "Cloudflare",
    "openresty": "OpenResty",
    "caddy": "Caddy",
}

# ============================================================
# User Agents for rotation
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
]

# ============================================================
# Crawler link keywords
# ============================================================
DONATE_LINK_KEYWORDS = [
    # Donation
    "donate", "giving", "gift", "contribute", "contribution",
    "support", "pledge", "ways-to-give", "make-a-gift",
    "get-involved", "help-us", "fundrais",
    # Invoice / bill pay
    "pay-invoice", "invoice", "bill-pay", "make-payment", "pay-bill",
    # Store / checkout
    "checkout", "cart", "shop", "store", "buy", "order",
    "product", "purchase",
    # Subscription / membership
    "subscribe", "membership", "subscription", "plans", "pricing",
    # Event / ticket
    "tickets", "register", "event", "rsvp",
]

# ============================================================
# Invoice / Bill Pay Signatures
# ============================================================
INVOICE_SIGNATURES = {
    "invoice_keywords": [
        "pay invoice", "invoice number", "invoice id", "invoice payment",
        "pay your bill", "pay bill online", "bill pay", "payment portal",
        "enter invoice", "invoice lookup", "account number", "pay now",
        "outstanding balance", "make a payment", "pay your invoice",
        "billing statement", "statement number", "balance due",
        "amount due", "pay online", "quick pay", "express pay",
    ],
    "invoice_form_fields": [
        "invoice_number", "invoice_id", "invoiceNumber", "invoiceId",
        "account_number", "accountNumber", "bill_number", "reference_number",
        "customer_id", "payment_reference", "invoice-number", "invoice-id",
        "account-number", "bill-number", "reference-number", "customer-id",
    ],
    "invoice_url_patterns": [
        "pay-invoice", "invoice-payment", "bill-pay", "payment-portal",
        "pay-bill", "make-payment", "pay-online", "billing/pay",
        "quickpay", "expresspay", "epay", "billpay", "paybill",
    ],
}

# ============================================================
# Site Type Signatures
# ============================================================
STORE_SIGNATURES = {
    "keywords": [
        "add to cart", "add to bag", "buy now", "shop now", "checkout",
        "shopping cart", "product", "price", "qty", "quantity",
        "in stock", "out of stock", "add_to_cart", "woocommerce",
        "view cart", "proceed to checkout", "continue shopping",
        "order summary", "your cart", "cart total",
    ],
    "url_patterns": [
        "/shop", "/store", "/product", "/cart", "/checkout",
        "/buy", "/order", "/products",
    ],
}

SUBSCRIPTION_SIGNATURES = {
    "keywords": [
        "subscribe", "subscription", "membership", "monthly plan",
        "annual plan", "per month", "per year", "billing cycle",
        "auto-renew", "cancel anytime", "free trial", "upgrade plan",
        "current plan", "plan details", "recurring billing",
    ],
    "url_patterns": [
        "/subscribe", "/membership", "/plans", "/pricing",
        "/upgrade", "/billing",
    ],
}

EVENT_SIGNATURES = {
    "keywords": [
        "buy tickets", "ticket", "register now", "event registration",
        "reserve your seat", "rsvp", "attend", "admission",
        "event", "conference", "seminar", "workshop", "webinar",
    ],
    "url_patterns": [
        "/tickets", "/register", "/event", "/events",
        "/registration", "/rsvp",
    ],
}

# ============================================================
# Static Search Dorks
# ============================================================
STATIC_DORKS = [
    # ── Cat 1: NMI (Network Merchants) ─────────────────────
    '"CollectJS" "checkout" -github -npm -docs',
    '"collectjs.com" inurl:checkout -github',
    '"secure.networkmerchants.com" "payment" site:.com',
    '"collect.js" "card-number" "cvv" -github',
    'inurl:checkout "secure.nmi.com" -github -stackoverflow',

    # ── Cat 2: Authorize.Net ────────────────────────────────
    '"Accept.js" "checkout" -github -developer -docs',
    '"acceptjs" "card" "payment" inurl:checkout -github',
    '"AcceptUI" "payment" site:.com -github',
    '"secure.authorize.net" inurl:pay -github -developer',
    '"Accept.dispatchData" "checkout" -npm -github',

    # ── Cat 3: Braintree ────────────────────────────────────
    '"braintree-hosted-fields" "checkout" -github -npm',
    '"braintree_client_token" "payment" site:.com -github',
    '"js.braintreegateway.com" inurl:checkout -github',
    '"braintree.dropin" "checkout" site:.com -github -npm',
    '"bt-hosted-field" "card" "amount" -github -docs',

    # ── Cat 4: Cybersource ──────────────────────────────────
    '"flex.cybersource.com" inurl:checkout -github',
    '"cybersource.flex" "payment" site:.com -github',
    '"flex-microform" "checkout" -github -developer',
    '"secureacceptance.cybersource.com" -github',
    '"testflex.cybersource.com" "checkout" site:.com',

    # ── Cat 5: Adyen ────────────────────────────────────────
    '"adyen-checkout" "payment" site:.com -github -npm',
    '"checkoutshopper-live.adyen.com" inurl:checkout',
    '"adyen.createFromAction" "payment" -github -docs',
    '"adyen-checkout__" "card" site:.com -github',
    '"adyen.encrypt" "checkout" site:.com -github',

    # ── Cat 6: Heartland / Global Payments ─────────────────
    '"SecureSubmit" "checkout" site:.com -github -npm',
    '"api.heartlandportico.com" "payment" -github',
    '"heartland-payment" "card" inurl:checkout',
    '"globalpayments" "checkout" site:.com -github',
    '"hps.js" "payment" site:.com -github',

    # ── Cat 7: CardConnect / CardPointe ─────────────────────
    '"cardpointe" inurl:checkout "payment" -github',
    '"cardconnect" "tokenize" "payment" site:.com -github',
    '"bolt-api.cardconnect.com" -github -developer',
    '"cardsecure" "checkout" site:.com -github',

    # ── Cat 8: Spreedly ─────────────────────────────────────
    '"spreedly-number" "checkout" -github -npm',
    '"Spreedly.init" "payment" site:.com -github',
    '"core.spreedly.com" inurl:checkout -github',
    '"spreedly.tokenize" "card" site:.com -github',

    # ── Cat 9: Checkout.com ──────────────────────────────────
    '"frames.checkout.com" "checkout" -github',
    '"Frames.init" "payment" site:.com -github',
    '"cko-card-number" "checkout" site:.com',
    '"cdn.checkout.com/sdk" "payment" -github',

    # ── Cat 10: Nuvei / SafeCharge ──────────────────────────
    '"safecharge.com" inurl:checkout "payment" -github',
    '"ppp.nuvei.com" "payment" site:.com -github',
    '"nuveiSDK" "checkout" -github',

    # ── Cat 11: PayTrace ─────────────────────────────────────
    '"paytrace.js" "checkout" site:.com -github',
    '"api.paytrace.com" "payment" -github',
    '"paytrace" inurl:checkout "card" -github',

    # ── Cat 12: Helcim ──────────────────────────────────────
    '"helcimPay" "checkout" -github',
    '"api.helcim.com" "payment" site:.com',
    '"helcim-pay" inurl:checkout -github',

    # ── Cat 13: Shift4 / i4Go ────────────────────────────────
    '"i4go.js" "payment" site:.com -github',
    '"secure.shift4.com" inurl:checkout -github',
    '"shift4sdk" "payment" site:.com',

    # ── Cat 14: Vanco ────────────────────────────────────────
    '"vancopayments" "payment" site:.com -github',
    '"givingflow" "payment" -github -docs',
    '"epaymentamerica" "online" "payment" -github',

    # ── Cat 15: Stax / Fattmerchant ──────────────────────────
    '"omni.fattmerchant.com" "payment" -github',
    '"fattjs" "checkout" site:.com -github',
    '"staxpayments" inurl:checkout -github',

    # ── Cat 16: USAePay ─────────────────────────────────────
    '"usaepay" "checkout" "payment" site:.com -github',
    '"secure.usaepay.com" inurl:pay -github',
    '"PaymentForm.usaepay" -github -npm',

    # ── Cat 17: Paysafe ─────────────────────────────────────
    '"hosted.paysafe.com" inurl:checkout -github',
    '"paysafe.fields" "payment" site:.com -github',
    '"netbanx" "checkout" site:.com -github',

    # ── Cat 18: BlueSnap ─────────────────────────────────────
    '"hostedpaymentfields.bluesnap.com" -github',
    '"BluesnapEncryptedPaymentField" "checkout" -github',
    '"pay.bluesnap.com" inurl:checkout site:.com',

    # ── Cat 19: Worldpay ─────────────────────────────────────
    '"wpwlOptions" "checkout" site:.com -github',
    '"access.worldpay.com" inurl:pay -github',
    '"Worldpay.useTemplateForm" site:.com -github',

    # ── Cat 20: Store / Ecommerce checkout ──────────────────
    '"add to cart" "checkout" "billing address" "braintree" site:.com',
    '"add to cart" inurl:checkout "CollectJS" -github',
    '"shopping cart" "secure checkout" "acceptjs" site:.com',
    '"order total" "checkout" "cybersource" site:.com -github',
    '"proceed to checkout" "heartland" "payment" site:.com',
    '"buy now" "checkout" "adyen" site:.com -github -docs',
    '"product" "add to cart" "nmi" "payment" site:.com',
    '"order summary" "checkout" "authorize.net" site:.com',

    # ── Cat 21: Subscription / Membership ───────────────────
    '"subscribe" "billing" "braintree" inurl:membership -github',
    '"monthly" "billing" "adyen" inurl:subscribe site:.com',
    '"recurring" "billing" "CollectJS" site:.com -github',
    '"subscription" "payment" "authorize.net" inurl:plans',
    '"membership" "billing" "heartland" site:.com -github',
    '"plan" "subscribe" "spreedly" site:.com -github',

    # ── Cat 22: Event / Ticket pages ────────────────────────
    '"buy tickets" "checkout" "braintree" -github',
    '"event registration" "payment" "authorize.net" site:.com',
    '"register now" "billing" "adyen" inurl:event -github',
    '"ticket" "purchase" "NMI" site:.com -github',
    '"conference" "registration" "cybersource" -github -docs',

    # ── Cat 23: Invoice / Bill Pay ────────────────────────────
    '"pay invoice" "enter invoice number" -github -stackoverflow',
    'inurl:pay-invoice "credit card" -github -template',
    '"invoice payment" "billing" "authorize.net" site:.com',
    '"bill pay" "account number" "amount due" -github',
    'inurl:quickpay "invoice" "payment" -docs -github',
    '"online bill pay" "card number" "account" site:.com',
    '"payment portal" "invoice number" -github -template',
    'inurl:billpay "card" "payment" site:.com -github',

    # ── Cat 24: Donation (focused, high signal) ──────────────
    '"civicrm" "contribute" "amount" -github -developer',
    '"donorbox" "braintree" inurl:embed -github',
    '"give-form" "payment" "braintree" -wordpress.org',
    '"charitable" "payment" "heartland" site:.org',
    '"online giving" "CollectJS" site:.org -github',
    '"donate" "authorize.net" "billing address" site:.org -github',
    '"fundrais" "checkout" "adyen" site:.org -github',
]

# ============================================================
# Dork Generator Components
# ============================================================
DORK_ACTIONS = [
    # Store / checkout
    'inurl:checkout "payment"',
    '"add to cart" "payment"',
    '"buy now" "checkout"',
    '"order" "billing" "payment"',
    '"shopping cart" "checkout"',
    'inurl:shop "checkout" "payment"',
    # Subscription / membership
    '"subscribe" "billing"',
    '"membership" "payment"',
    '"recurring" "billing"',
    'inurl:subscribe "payment"',
    # Events / tickets
    '"buy tickets" "payment"',
    '"register" "billing" "payment"',
    # Invoice / bill pay
    '"pay invoice"',
    '"invoice payment"',
    '"pay your bill"',
    'inurl:billpay "payment"',
    # Donation (kept but reduced)
    '"make a donation"',
    '"donate" "payment"',
    '"give now" "billing"',
    '"contribute" "amount"',
]

DORK_SECTORS = [
    # TLD / country
    'site:.com', 'site:.com -site:.edu -site:.gov',
    'site:.org', 'site:.ca', 'site:.co.uk',
    'site:.net', 'site:.us',
    # Store types
    '"online store"', '"shop"', '"ecommerce"', '"boutique"',
    '"clothing" "checkout"', '"electronics" "checkout"',
    '"furniture" "checkout"', '"food" "checkout"',
    '"jewelry" "shop"', '"accessories" "checkout"',
    # Service / membership
    '"gym" "membership"', '"club" "membership"', '"association" "payment"',
    '"subscription" "billing"', '"service" "billing"',
    # Event
    '"event" "ticket"', '"conference" "registration"',
    '"workshop" "register"',
    # Nonprofit (reduced weight)
    '"foundation"', '"nonprofit" "payment"',
    '"church" "giving"', '"hospital" "payment"',
    '"university" "payment"',
    # Invoice / billing
    '"billing portal"', '"payment portal"', '"invoice"',
]

DORK_EXCLUSIONS = "-github -stackoverflow -wordpress.org -npm -template -theme -demo -docs -api -developer -sandbox"

# ============================================================
# Quality Scoring Weights
# ============================================================
SCORE_WEIGHTS = {
    "gateway_confidence": 20,     # 0-20 based on signature match count
    "avs_present": 10,
    "no_captcha": 10,
    "has_captcha": -5,
    "platform_identified": 5,
    "has_recurring": 5,
    "domain_age_2yr": 10,
    "https": 5,
    "has_3ds": -5,
    "high_traffic": 10,
    "multi_currency": 5,
    "recently_indexed": 15,
}
