import streamlit as st
import telebot
import google.generativeai as genai
import threading
import time

# 1. إعداد الصفحة (يجب أن يكون أول أمر في الملف)
st.set_page_config(page_title="AI Russian Tutor", page_icon="🤖", layout="wide")

# عنوان التطبيق
st.title("🤖 المعلم الروسي الذكي (Gemini Advanced)")
st.markdown("---")

# 2. القائمة الجانبية (الإعدادات)
with st.sidebar:
    st.header("⚙️ إعدادات التشغيل")
    tg_token = st.text_input("Telegram Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    # كاشف النماذج الذكي
    available_models = []
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            st.success("المفتاح سليم! جاري جلب النماذج...")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except Exception as e:
            st.error(f"خطأ في المفتاح: {e}")

    # قائمة اختيار النموذج
    selected_model = "gemini-1.5-pro" # افتراضي
    if available_models:
        # محاولة تحديد 1.5 pro كخيار مفضل
        default_index = 0
        for i, name in enumerate(available_models):
            if "1.5-pro" in name and "exp" not in name:
                default_index = i
                break
        selected_model = st.selectbox("اختر مستوى الذكاء:", available_models, index=default_index)
    else:
        st.warning("أدخل مفتاح Gemini لظهور القائمة.")

# 3. وظيفة البوت (تعمل في الخلفية)
def run_bot_process(token, api_key, raw_model_name):
    # تنظيف اسم النموذج (إزالة models/ إذا وجدت لتجنب الأخطاء)
    clean_model = raw_model_name.replace("models/", "")
    print(f">>> Starting bot with model: {clean_model}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(clean_model)
        bot = telebot.TeleBot(token)

        @bot.message_handler(commands=['start'])
        def start_msg(message):
            bot.reply_to(message, f"أهلاً! أنا أعمل الآن باستخدام الدماغ:\n`{clean_model}`\nأرسل جملتك الروسية.")

        @bot.message_handler(func=lambda m: True)
        def process_message(message):
            user_text = message.text
            print(f"Processing: {user_text} | Model: {clean_model}")
            
            prompt = f"""
            Act as an expert Russian tutor.
            Input: "{user_text}"
            Task:
            1. Identify verbs and their aspect (СВ/НСВ).
            2. Explain difficult words.
            3. Translate to Arabic.
            4. Use emojis and clear formatting.
            """
            
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
            except Exception as e:
                err = f"⚠️ حدث خطأ مع النموذج {clean_model}:\n{e}"
                print(err)
                bot.reply_to(message, err)

        bot.infinity_polling()
        
    except Exception as e:
        print(f"Bot Crash detected: {e}")

# 4. زر التشغيل الرئيسي
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🚀 تشغيل البوت الآن", use_container_width=True):
        if not tg_token or not gemini_key:
            st.error("الرجاء إدخال المفاتيح أولاً!")
        else:
            st.toast(f"جاري الاتصال بـ {selected_model}...", icon="🔌")
            st.success(f"✅ تم بدء التشغيل باستخدام: {selected_model}")
            st.info("يمكنك الآن استخدام البوت في تليجرام. لا تغلق هذه الصفحة.")
            
            # تشغيل في مسار منفصل
            t = threading.Thread(target=run_bot_process, args=(tg_token, gemini_key, selected_model))
            t.start()

with col2:
    st.info("💡 نصيحة: إذا ظهرت لك موديلات مثل gemini-2.5 وجربتها ولم تعمل، عد واستخدم gemini-1.5-pro فهو الأضمن.")
