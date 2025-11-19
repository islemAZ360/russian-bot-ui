import streamlit as st
import telebot
import google.generativeai as genai
import threading

# --- إعداد الصفحة ---
st.set_page_config(page_title="Gemini Doctor", page_icon="🩺")
st.title("🩺 كاشف النماذج (الحل النهائي)")
st.write("هذا البرنامج سيجلب قائمة النماذج المتاحة فعلياً لمفتاحك.")

# --- المدخلات ---
tg_token = st.text_input("Telegram Token", type="password")
gemini_key = st.text_input("Gemini API Key", type="password")

# --- جلب القائمة الحقيقية ---
valid_models = []
if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
        # نسأل جوجل: أعطنا القائمة
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                valid_models.append(m.name)
        st.success(f"✅ تم العثور على {len(valid_models)} نموذج متاح لك!")
    except Exception as e:
        st.error(f"خطأ في المفتاح: {e}")

# --- اختيار النموذج ---
if valid_models:
    # دع المستخدم يختار من القائمة الموجودة فعلاً
    selected_model_name = st.selectbox("اختر واحداً من هذه القائمة (لن يعطي 404):", valid_models)
else:
    selected_model_name = None
    st.info("أدخل مفتاح Gemini لتظهر القائمة.")

# --- تشغيل البوت ---
def run_bot(token, api_key, model_name):
    # لا نحذف models/ لأن القائمة تأتي بها جاهزة
    print(f">>> تشغيل: {model_name}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        bot = telebot.TeleBot(token)

        @bot.message_handler(func=lambda m: True)
        def handle(msg):
            try:
                bot.send_chat_action(msg.chat.id, 'typing')
                prompt = f"""
                Analyze Russian text: "{msg.text}"
                1. Verbs (Aspect).
                2. Vocab.
                3. Arabic Translation.
                """
                response = model.generate_content(prompt)
                bot.reply_to(msg, response.text)
            except Exception as e:
                bot.reply_to(msg, f"Error: {e}")

        bot.infinity_polling()
    except Exception as e:
        print(f"Crash: {e}")

# --- زر التنفيذ ---
if st.button("🚀 تشغيل البوت بالنموذج المختار"):
    if not tg_token or not gemini_key or not selected_model_name:
        st.error("البيانات ناقصة!")
    else:
        st.success(f"تم التشغيل بضمان: {selected_model_name}")
        t = threading.Thread(target=run_bot, args=(tg_token, gemini_key, selected_model_name))
        t.start()
