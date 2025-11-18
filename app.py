import streamlit as st
import telebot
import google.generativeai as genai
import time

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian Bot Debugger", page_icon="🛠️")

st.title("🛠️ وضع إصلاح البوت")
st.warning("⚠️ ملاحظة: عند تشغيل البوت، ستظهر دائرة التحميل في الأعلى باستمرار. هذا طبيعي! لا تغلق الصفحة.")

# --- المدخلات ---
tg_token = st.text_input("Telegram Token", type="password")
gemini_key = st.text_input("Gemini API Key", type="password")

# --- دالة لاختبار مفتاح Gemini ---
def test_gemini(key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Test connection")
        return True, "✅ اتصال Gemini سليم!"
    except Exception as e:
        return False, f"❌ خطأ في Gemini: {e}"

# --- التشغيل ---
if st.button("تشغيل البوت (Start)"):
    if not tg_token or not gemini_key:
        st.error("أدخل المفاتيح أولاً!")
    else:
        # 1. اختبار Gemini أولاً
        status, msg = test_gemini(gemini_key)
        if not status:
            st.error(msg)
        else:
            st.success(msg)
            st.info("جاري الاتصال بتليجرام... ابق في هذه الصفحة.")
            
            # إعداد البوت
            try:
                bot = telebot.TeleBot(tg_token)
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-pro')

                # رسالة ترحيب
                @bot.message_handler(commands=['start'])
                def send_welcome(message):
                    bot.reply_to(message, "أهلاً! أنا أعمل الآن. أرسل لي جملة.")

                # معالجة الرسائل
                @bot.message_handler(func=lambda m: True)
                def handle_message(message):
                    user_text = message.text
                    # طباعة في الشاشة السوداء للتأكد
                    print(f"New Message: {user_text}") 
                    
                    prompt = f"""
                    حلل الجملة الروسية التالية، استخرج الأفعال (СВ/НСВ) والكلمات الصعبة ومعانيها بالعربية:
                    "{user_text}"
                    """
                    
                    try:
                        # محاولة التحليل
                        bot.send_chat_action(message.chat.id, 'typing') # يظهر "جاري الكتابة"
                        response = model.generate_content(prompt)
                        bot.reply_to(message, response.text)
                    except Exception as e:
                        # إذا فشل الذكاء الاصطناعي، أرسل الخطأ للمستخدم
                        error_msg = f"⚠️ حدث خطأ تقني:\n{str(e)}"
                        bot.reply_to(message, error_msg)
                        print(f"Error: {e}")

                # تشغيل البوت (هذا سيجعل الصفحة في حالة تحميل دائم)
                bot.infinity_polling(timeout=10, long_polling_timeout=5)
                
            except Exception as e:
                st.error(f"فشل تشغيل البوت: {e}")
