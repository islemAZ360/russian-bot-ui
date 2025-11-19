import streamlit as st
import telebot
import google.generativeai as genai
import threading

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian Tutor Pro", page_icon="🇷🇺", layout="centered")
st.title("🇷🇺 المعلم الروسي (النسخة المستقرة)")
st.success("يتم العمل الآن بمحرك: gemini-1.5-pro (الأقوى والمجاني)")

# --- المدخلات ---
tg_token = st.text_input("Telegram Token", type="password")
gemini_key = st.text_input("Gemini API Key", type="password")

# --- وظيفة البوت (Hardcoded 1.5 Pro) ---
def run_bot(token, key):
    # هنا نختار الموديل يدوياً لنضمن عدم الخطأ
    model_name = "gemini-1.5-pro"
    print(f">>> Starting Bot with: {model_name}")
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        bot = telebot.TeleBot(token)

        @bot.message_handler(func=lambda m: True)
        def handle_all(message):
            try:
                # إشعار "جاري الكتابة"
                bot.send_chat_action(message.chat.id, 'typing')
                
                # البرومبت الذكي
                prompt = f"""
                Act as a professional Russian linguist.
                Input: "{message.text}"
                
                Tasks:
                1. Analyze verbs: provide Aspect (СВ/НСВ) and Infinitive.
                2. Identify complex nouns/adjectives.
                3. Translate the meaning to Arabic clearly.
                4. Format the response with emojis (🔍, 📖, 🇸🇦).
                """
                
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
                print("Response sent!")
                
            except Exception as e:
                error_msg = str(e)
                # تحسين رسالة الخطأ
                if "429" in error_msg:
                    bot.reply_to(message, "⏳ الضغط عالٍ، يرجى الانتظار 10 ثوانٍ.")
                else:
                    bot.reply_to(message, f"⚠️ خطأ تقني: {error_msg}")

        bot.infinity_polling()
        
    except Exception as e:
        print(f"Bot Error: {e}")

# --- زر التشغيل ---
if st.button("🔥 تشغيل البوت فوراً"):
    if not tg_token or not gemini_key:
        st.error("أدخل المفاتيح أولاً")
    else:
        st.info("تم التشغيل! اذهب لتليجرام.")
        # إطلاق البوت
        t = threading.Thread(target=run_bot, args=(tg_token, gemini_key))
        t.start()
