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
        "api.braintreegateway.com", "braintree_client_token",
    ],
    "Cybersource": [
        "cybersource", "flex-microform", "cybs", "cybersource.flex",
        "secureacceptance", "cybersource.com", "sonsofsecurity",
    ],
    "Payflow": [
        "payflow", "payflowlink", "payflow_color", "payflowpro",
        "paypal.com/cgi-bin/webscr", "manager.paypal.com",
    ],
    "Spreedly": [
        "spreedly", "spreedly.com", "core.spreedly.com",
        "spreedlyjs", "Spreedly.init",
    ],
    "Chase": [
        "chase paymentech", "orbital", "safetech",
        "chase.com/payment", "chasepaymentech",
    ],
    "Adyen": [
        "adyen", "adyen-checkout", "checkoutshopper",
        "adyen.encrypt", "adyen-cse", "checkoutshopper-live.adyen.com",
        "checkoutshopper-test.adyen.com", "adyen-checkout__",
    ],
    "Convergepay": [
        "convergepay", "elavon", "converge.myvirtualmerchant",
        "api.convergepay.com", "myvirtualmerchant",
    ],
    "Stripe": [
        "stripe", "stripe.js", "js.stripe.com", "stripe-elements",
        "stripe.createToken", "stripe.confirmCardPayment", "pk_live_",
        "pk_test_", "stripe-card-element", "StripeElement",
        "stripe.createPaymentMethod", "api.stripe.com",
    ],
    "Square": [
        "square", "squareup.com", "js.squareup.com", "square-payment-form",
        "SqPaymentForm", "web.squarecdn.com", "squareupsandbox.com",
    ],
    "AuthorizeNet": [
        "authorize.net", "Accept.js", "acceptjs", "authorizenet",
        "js.authorize.net", "AcceptUI", "Accept.dispatchData",
        "secure.authorize.net", "anet-sdk",
    ],
    "Worldpay": [
        "worldpay", "access.worldpay.com", "payments.worldpay.com",
        "secure.worldpay.com", "worldpay-cse", "Worldpay.useTemplateForm",
    ],
    "Moneris": [
        "moneris", "esqa.moneris.com", "www3.moneris.com", "moneris-checkout",
        "monerisjsv2", "moneris.com/HPPtoken",
    ],
    "Bambora": [
        "bambora", "web.na.bambora.com", "api.na.bambora.com", "bamboracheckout",
        "customcheckout.bambora.com",
    ],
    "BlueSnap": [
        "bluesnap", "sandpay.bluesnap.com", "pay.bluesnap.com", "bluesnap-hosted",
        "BluesnapEncryptedPaymentField", "bluesnap.com/services",
    ],
    "2Checkout": [
        "2checkout", "2co.com", "2checkout.com", "TwoCoInlineCart",
        "avng8.net", "2checkout-inline",
    ],
    "PayU": [
        "payu", "payulatam", "payubiz", "payumoney", "payu.in",
        "secure.payu.com", "payuCheckoutPro", "bolt.js",
    ],
    "Razorpay": [
        "razorpay", "checkout.razorpay.com", "Razorpay.open",
        "razorpay-payment", "razorpay.js", "rzp_live_", "rzp_test_",
    ],
    "Payeezy": [
        "payeezy", "api.payeezy.com", "first-data", "firstdata",
        "payeezy.js", "Payeezy.createToken",
    ],
    "NMI": [
        "nmi", "secure.networkmerchants.com", "CollectJS", "collectjs",
        "gateway.merchantservicesltd", "secure.nmi.com",
    ],
    "USAePay": [
        "usaepay", "sandbox.usaepay.com", "secure.usaepay.com",
        "usaepay-form", "PaymentForm.usaepay",
    ],
    "CardConnect": [
        "cardconnect", "cardpointe", "api.cardconnect.com",
        "fts-uat.cardconnect.com", "bolt-api.cardconnect.com",
    ],
    "Paysafe": [
        "paysafe", "paysafe.js", "hosted.paysafe.com", "api.paysafe.com",
        "paysafecard", "netbanx",
    ],
    "Clover": [
        "clover", "clover.com", "api.clover.com", "clover-sdk",
        "checkout.clover.com", "clover-payment",
    ],
    "Heartland": [
        "heartland", "api.heartlandportico.com", "SecureSubmit",
        "securesubmit", "globalpayments", "hps.js",
    ],
    "iATS": [
        "iatspayments", "iats", "www.iatspayments.com",
        "aura.iatspayments.com",
    ],
    "Blackbaud": [
        "blackbaud", "bbpayments", "blackbaud.com", "sky-api",
        "checkout.blackbaud.com", "bbox.blackbaudhosting.com",
    ],
    "Windcave": [
        "windcave", "paymentexpress", "sec.windcave.com", "pxpay",
        "sec.paymentexpress.com",
    ],
    "Flywire": [
        "flywire", "flywire.com", "payment.flywire.com", "flywire-payment",
    ],
    "TouchNet": [
        "touchnet", "commerce.touchnet.com", "uPay", "touchnet.net",
        "marketplace.touchnet.com",
    ],
    "CashNet": [
        "cashnet", "commerce.cashnet.com", "cashnet.com",
    ],
    "Nelnet": [
        "nelnet", "quikpayasp.com", "myquikpay", "nelnet.com",
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
    "Stripe": "STRP",
    "Square": "SQR",
    "AuthorizeNet": "ANET",
    "Worldpay": "WP",
    "Moneris": "MNR",
    "Bambora": "BMB",
    "BlueSnap": "BSNP",
    "2Checkout": "2CO",
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
    "donate", "giving", "gift", "contribute", "contribution",
    "support", "pledge", "ways-to-give", "make-a-gift",
    "get-involved", "help-us", "fundrais",
    "pay-invoice", "invoice", "bill-pay", "make-payment", "pay-bill",
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
# Static Search Dorks (60+)
# ============================================================
STATIC_DORKS = [
    # Cat 1: Gateway-specific plugin signatures
    '"wp-content/plugins/woo-braintree" inurl:donate',
    '"braintree-hosted-fields" "donation" site:.org',
    '"cybersource.environment" "donate" -github',
    '"adyen-checkout" "give" OR "donate" -stackoverflow',
    '"spreedly-iframe" "donation" site:.org',
    '"payflow" "donate" "secure" site:.org',
    '"converge" "ssl_merchant_id" "donate"',
    '"braintree.dropin" "donate" -npm -github',
    '"adyen.encrypt" "donation" -docs',
    '"cybersource" "flex" "donate" site:.org',

    # Cat 2: CMS donation plugin pages
    '"give-form" "make a donation" -wordpress.org -developer',
    '"charitable-donation" site:.org',
    '"wp-content/plugins/give" "support" OR "gift" -developer',
    '"civicrm" "contribute" "amount" site:.org',
    '"donorbox" braintree site:.org',
    '"formidable" "payment" "donate" site:.org',
    '"gravity forms" "donate" "payment" site:.org',

    # Cat 3: Niche nonprofit sectors
    '"tithe" OR "offering" "donate online" "secure" site:.org',
    '"alumni" "make a gift" site:.edu',
    '"annual fund" "give now" site:.edu',
    '"parish" OR "church" "online giving" "donate"',
    '"animal rescue" "donate" "payment" site:.org',
    '"food bank" "donate" "contribution" site:.org',
    '"humane society" "donate" site:.org',
    '"habitat for humanity" "donate" site:.org',
    '"veterans" "donate" "support" site:.org',
    '"arts council" "donate" site:.org',
    '"community foundation" "give" "donate" site:.org',
    '"hospice" "donate" "memorial" site:.org',
    '"museum" "donate" "support" site:.org',
    '"public radio" OR "public television" "donate"',
    '"boys and girls club" "donate" site:.org',
    '"literacy" "donate" "education" site:.org',
    '"women\'s shelter" "donate" site:.org',

    # Cat 4: URL pattern hunting
    'inurl:"/give/donate" -github -npm -packagist',
    'inurl:"/ways-to-give" "online"',
    'inurl:"/support-us/donate" "payment"',
    'inurl:"/get-involved/donate" site:.org',
    'inurl:"donorshops.com"',
    'inurl:"/cart" "donate" site:.org',
    'inurl:"/giving" "make a gift" site:.edu',
    'inurl:"/contribute" "amount" "donate" site:.org',
    'inurl:"/pledge" "donate" site:.org',

    # Cat 5: Form/checkout element hunting
    '"hosted-field-braintree" "amount"',
    '"data-cse" "adyen" "donate"',
    '"Accept.js" "chase" "donation" site:.org',
    '"tokenize" "payment" "donate" -stackoverflow -github',
    '"payment-form" "donate" "billing" site:.org',
    '"cc-number" "donate" "amount" site:.org',

    # Cat 6: Regional markets
    '"donate" "canadian charity" "receipt" site:.ca',
    '"donate" "charity" "ABN" site:.org.au',
    '"donate" "registered charity" site:.org.uk',
    '"fondation" "don" "paiement" site:.ca',
    '"donate" "charity number" site:.ie',
    '"donate" "DGR" site:.org.au',

    # Cat 7: AVS-focused
    '"billing address" "donate" "braintree" site:.org',
    '"street address" "zip" "donate" site:.org',
    '"billing_address" "postalCode" "donate"',
    '"address verification" "donation" -github',

    # Cat 8: Generic high-quality
    '"tax deductible" "donate online" "secure" -template -theme',
    '"501c3" "make a donation" "amount" -irs.gov',
    '"charitable organization" "donate now" "payment" -wikipedia',
    '"nonprofit" "support our mission" "give" -indeed -linkedin',
    '"make a gift" "secure" "online" site:.org -wordpress.org',
    '"donate" "amount" "recurring" site:.org -github',

    # Cat 9: Invoice / Bill Pay pages
    '"pay invoice" "enter invoice number" site:.com -github',
    'inurl:pay-invoice "payment" -github -stackoverflow',
    '"invoice payment portal" "billing" -template -demo',
    '"pay your bill online" "account number" -github',
    'inurl:billing/pay "invoice" -stackoverflow',
    '"payment portal" "invoice number" "amount" site:.com',
    'inurl:make-payment "invoice" "billing" -github',
    '"pay invoice online" "credit card" -template',
    '"bill pay" "account number" "amount due" -github',
    'inurl:quickpay "invoice" "payment" -docs',
    '"online bill pay" "enter your" "account" site:.com',
    'inurl:epay "invoice" OR "billing" -github -npm',
]

# ============================================================
# Dork Generator Components
# ============================================================
DORK_ACTIONS = [
    'inurl:donate', '"make a donation"', '"give now"', '"support us"',
    '"ways to give"', '"make a gift"', '"donate online"', '"contribute"',
    '"donate now"', '"online donation"', '"donate today"', '"giving"',
    '"support our mission"', '"help us"', '"your gift"', '"your donation"',
    '"pay invoice"', '"invoice payment"', '"pay your bill"', '"bill pay online"',
]

DORK_SECTORS = [
    'site:.org', 'site:.edu', 'site:.ca', 'site:.org.uk', 'site:.org.au',
    '"church"', '"foundation"', '"rescue"', '"food bank"', '"museum"',
    '"hospital"', '"university"', '"wildlife"', '"homeless"', '"veterans"',
    '"arts"', '"library"', '"ymca"', '"habitat"', '"shelter"',
    '"community"', '"children"', '"cancer"', '"heart"', '"medical"',
    '"environmental"', '"conservation"', '"youth"', '"senior"', '"animal"',
    '"education"', '"scholarship"', '"relief"', '"mission"', '"ministry"',
    '"billing portal"', '"payment portal"', '"invoice"', '"customer payment"',
]

DORK_EXCLUSIONS = "-github -stackoverflow -wordpress.org -npm -template -theme -demo -docs -api -developer"

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
