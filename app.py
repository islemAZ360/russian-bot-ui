import streamlit as st
import telebot
import google.generativeai as genai
import threading

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian AI Master", page_icon="💎", layout="wide")
st.title("💎 المعلم الروسي (واجهة اختيار النماذج)")
st.write("اختر أقوى نموذج متاح حالياً من جوجل لتشغيل البوت.")

# --- القائمة الجانبية للمدخلات ---
with st.sidebar:
    st.header("🔐 مفاتيح التشغيل")
    tg_token = st.text_input("Telegram Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    # زر للكشف عن النماذج
    available_models = []
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            # جلب النماذج التي تدعم إنشاء المحتوى
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            st.success("تم جلب قائمة النماذج بنجاح!")
        except Exception as e:
            st.error(f"المفتاح غير صحيح أو حدث خطأ: {e}")

    # قائمة منسدلة لاختيار النموذج
    if available_models:
        # نحاول تحديد 1.5 pro كخيار افتراضي إذا وجد
        default_ix = 0
        for i, m_name in enumerate(available_models):
            if 'gemini-1.5-pro' in m_name and 'exp' not in m_name:
                default_ix = i
                break
        
        selected_model = st.selectbox("اختر الموديل (الذكاء):", available_models, index=default_ix)
        st.caption("نصيحة: gemini-1.5-pro هو الأذكى والأقوى حالياً.")
    else:
        selected_model = "models/gemini-1.5-pro" # افتراضي
        st.info("أدخل مفتاح Gemini لتر قائمة النماذج المتاحة.")

# --- وظيفة البوت ---
def start_bot_thread(telegram_token, gemini_api_key, model_name):
    print(f">>> Starting Bot with Model: {model_name}")
    
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(model_name)
        bot = telebot.TeleBot(telegram_token)

        @bot.message_handler(commands=['start'])
        def welcome(message):
            bot.reply_to(message, f"أهلاً! أنا أعمل الآن باستخدام النموذج: \n`{model_name}`\nأرسل جملتك للتحليل.")

        @bot.message_handler(func=lambda m: True)
        def analyzer(message):
            text = message.text
            print(f"Msg: {text} | Model: {model_name}")
            
            # برومبت احترافي جداً للنماذج القوية
            prompt = f"""
            Act as a professional Russian language tutor.
            User Input: "{text}"
            
            Task:
            1. If the input is a single word, provide detailed morphology, stress (ударение), and meaning.
            2. If it's a sentence, analyze grammatical structure, verb aspects (СВ/НСВ), and cases.
            3. Translate to Arabic correctly.
            4. Format the output nicely with emojis.
            """
            
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text, parse_mode='Markdown')
            except Exception as e:
                bot.reply_to(message, f"⚠️ Error: {e}")
                print(f"Error: {e}")

        bot.infinity_polling()
        
    except Exception as e:
        print(f"Boot Error: {e}")

# --- منطقة التشغيل ---
st.divider()

if st.button("🔥 تشغيل البوت بالنموذج المختار"):
    if not tg_token or not gemini_key:
        st.error("الرجاء تعبئة المفاتيح في القائمة الجانبية!")
    else:
        st.toast(f"جاري التشغيل باستخدام {selected_model}...", icon="🚀")
        st.write(f"### الحالة: ✅ البوت يعمل الآن بقلب {selected_model}")
        st.write("يمكنك الذهاب لتليجرام للتجربة. (لا تغلق هذه الصفحة)")
        
        t = threading.Thread(target=start_bot_thread, args=(tg_token, gemini_key, selected_model))
        t.start()
