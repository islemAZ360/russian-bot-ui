import streamlit as st
import telebot
import google.generativeai as genai
import threading

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian Bot V2", page_icon="🚀")
st.title("🚀 مشغل البوت (النسخة المستقرة)")
st.write("هذه النسخة تستخدم Gemini 1.5 Flash وتعمل في الخلفية بثبات.")

# --- المدخلات ---
tg_token = st.text_input("Telegram Token", type="password")
gemini_key = st.text_input("Gemini API Key", type="password")

# --- وظيفة البوت (تعمل في الخلفية) ---
def start_background_bot(telegram_token, gemini_api_key):
    print(">>> جاري بدء تشغيل البوت في الخلفية...")
    
    try:
        # 1. إعداد Gemini (بالاسم الجديد)
        genai.configure(api_key=gemini_api_key)
        # تم تغيير الاسم هنا لحل مشكلة 404
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        # 2. إعداد تليجرام
        bot = telebot.TeleBot(telegram_token)

        # رسالة الترحيب
        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            print(f"User started: {message.chat.id}")
            bot.reply_to(message, "أهلاً! أنا أعمل الآن بنسخة Gemini 1.5 Flash. أرسل جملتك.")

        # معالجة الرسائل
        @bot.message_handler(func=lambda m: True)
        def handle_message(message):
            text = message.text
            print(f"Received: {text}") # يطبع في الشاشة السوداء فقط
            
            prompt = f"""
            أنت معلم للغة الروسية. 
            المستخدم أرسل: "{text}"
            المطلوب:
            1. استخرج الأفعال وحدد (СВ/НСВ).
            2. استخرج الكلمات الصعبة.
            3. ترجم للعربية.
            """
            
            try:
                # إرسال "جاري الكتابة..." في تليجرام
                bot.send_chat_action(message.chat.id, 'typing')
                
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
                print("Replied successfully.")
            except Exception as e:
                error_msg = f"حدث خطأ في المعالجة: {e}"
                print(error_msg)
                bot.reply_to(message, error_msg)

        # تشغيل البوت
        print(">>> البوت جاهز ويستقبل الرسائل الآن!")
        bot.infinity_polling()
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

# --- زر التشغيل ---
if st.button("تشغيل البوت الآن"):
    if not tg_token or not gemini_key:
        st.error("الرجاء إدخال المفاتيح أولاً.")
    else:
        st.success("تم إرسال أمر التشغيل! راقب 'Manage App' (الشاشة السوداء) للتأكد.")
        st.warning("⚠️ لا تغلق هذه الصفحة، يمكنك تركها مفتوحة في الخلفية.")
        
        # تشغيل البوت في مسار منفصل بدون تعارض مع الواجهة
        t = threading.Thread(target=start_background_bot, args=(tg_token, gemini_key))
        t.start()
