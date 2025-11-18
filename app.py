import streamlit as st
import telebot
import google.generativeai as genai
import threading

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian AI Master", page_icon="🎓", layout="wide")
st.title("🎓 المعلم الروسي (قائمة النماذج الكاملة)")

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    tg_token = st.text_input("Telegram Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    # --- قائمة النماذج (إجبارية + تلقائية) ---
    # نبدأ بالنماذج المضمونة يدوياً
    model_list = [
        "models/gemini-1.5-pro",       # الأقوى والأذكى (ينصح به)
        "models/gemini-1.5-flash",     # الأسرع
        "models/gemini-1.5-pro-latest", # نسخة أخرى
    ]
    
    # نحاول جلب المزيد من القائمة
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if m.name not in model_list:
                        model_list.append(m.name)
        except:
            pass # لا يهم إذا فشل الجلب، لدينا القائمة اليدوية

    # القائمة المنسدلة
    selected_model = st.selectbox("اختر النموذج (ينصح بـ 1.5-pro):", model_list)

# --- وظيفة البوت ---
def run_bot(token, key, model_name):
    # تنظيف الاسم
    clean_name = model_name.replace("models/", "")
    print(f">>> تشغيل: {clean_name}")
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(clean_name)
        bot = telebot.TeleBot(token)

        @bot.message_handler(func=lambda m: True)
        def handle(msg):
            try:
                bot.send_chat_action(msg.chat.id, 'typing')
                
                prompt = f"""
                Role: Russian Language Tutor.
                Input: "{msg.text}"
                Task:
                1. Analyze verbs (Aspect: СВ/НСВ).
                2. Explain complex vocabulary.
                3. Translate to Arabic.
                """
                
                response = model.generate_content(prompt)
                bot.reply_to(msg, response.text)
                print("تم الرد بنجاح.")
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    bot.reply_to(msg, "⚠️ النموذج مشغول أو الحد المجاني ممتلئ. جرب 1.5-flash.")
                else:
                    bot.reply_to(msg, f"⚠️ خطأ: {err_msg}")

        bot.infinity_polling()
    except Exception as e:
        print(f"خطأ التشغيل: {e}")

# --- زر التشغيل ---
if st.button("🚀 تشغيل البوت (Force Run)"):
    if not tg_token or not gemini_key:
        st.error("أدخل المفاتيح!")
    else:
        st.success(f"تم الإرسال للنموذج: {selected_model}")
        st.info("اذهب لتليجرام وجرب الآن.")
        t = threading.Thread(target=run_bot, args=(tg_token, gemini_key, selected_model))
        t.start()
