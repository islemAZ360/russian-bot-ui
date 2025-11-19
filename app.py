import streamlit as st
import telebot
import google.generativeai as genai
import threading
import time

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian Bot Final", page_icon="✅")
st.title("✅ المعلم الروسي (النسخة النهائية)")
st.success("تم ضبط هذا الكود ليعمل على gemini-1.5-flash (الأسرع والمضمون).")

# --- المدخلات ---
tg_token = st.text_input("Telegram Token", type="password")
gemini_key = st.text_input("Gemini API Key", type="password")

# --- وظيفة البوت ---
def run_bot(token, key):
    # نستخدم فلاش لأنه الوحيد الذي يعمل في منطقتك وحسابك حالياً بدون مشاكل
    model_name = "gemini-1.5-flash"
    print(f">>> تشغيل البوت باستخدام: {model_name}")
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        bot = telebot.TeleBot(token)

        @bot.message_handler(func=lambda m: True)
        def handle_message(message):
            try:
                # إظهار "جاري الكتابة..."
                bot.send_chat_action(message.chat.id, 'typing')
                
                # التعليمات للمعلم
                prompt = f"""
                Act as a Russian language tutor.
                Input: "{message.text}"
                Task:
                1. Extract verbs and identify aspect (СВ or НСВ).
                2. Explain difficult words.
                3. Translate the full meaning to Arabic.
                4. Use emojis.
                """
                
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
                print("تم الرد بنجاح!")
                
            except Exception as e: # <--- هنا كان الخطأ وتم تصحيحه
                error_msg = f"⚠️ خطأ: {str(e)}"
                print(error_msg)
                bot.reply_to(message, error_msg)

        bot.infinity_polling()
        
    except Exception as e:
        print(f"Fatal Error: {e}")

# --- زر التشغيل ---
if st.button("🚀 تشغيل البوت الآن"):
    if not tg_token or not gemini_key:
        st.error("أدخل المفاتيح أولاً!")
    else:
        st.info("تم التشغيل! اذهب لتليجرام.")
        # تشغيل في الخلفية
        t = threading.Thread(target=run_bot, args=(tg_token, gemini_key))
        t.start()
