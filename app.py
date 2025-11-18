import streamlit as st
import telebot
import google.generativeai as genai
import threading
import time

# --- واجهة المستخدم (UI Design) ---
st.set_page_config(page_title="Russian Bot Host", page_icon="🇷🇺", layout="centered")

st.title("🇷🇺 المعلم الروسي الذكي")
st.write("لوحة تحكم لربط تليجرام مع الذكاء الاصطناعي لتعلم الروسية")

st.divider()

# --- المدخلات ---
col1, col2 = st.columns(2)
with col1:
    tg_token = st.text_input("Telegram Bot Token", type="password", placeholder="أدخل توكن تليجرام")
with col2:
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="أدخل مفتاح Gemini")

# --- متغيرات الحالة ---
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- دالة عرض السجلات ---
def log_message(msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

# --- منطق البوت ---
def run_bot(telegram_token, gemini_api_key):
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        bot = telebot.TeleBot(telegram_token)
        
        # الذاكرة المؤقتة
        user_memory = {}

        system_prompt = """
        أنت خبير لغة روسية. حلل الجملة، استخرج الأفعال وصيغتها (СВ/НСВ)، والكلمات الصعبة.
        تذكر دائماً ما يرسله المستخدم لتبني عليه لاحقاً.
        """

        @bot.message_handler(commands=['start'])
        def start(message):
            bot.reply_to(message, "أهلاً! أنا جاهز لتحليل الروسية.")
            log_message(f"New user started: {message.chat.id}")

        @bot.message_handler(func=lambda m: True)
        def handle_all(message):
            user_id = message.chat.id
            text = message.text
            log_message(f"Received: {text} from {user_id}")
            
            # السياق من الذاكرة
            history = user_memory.get(user_id, [])
            context = f"سياق سابق: {history[-3:]}" if history else ""
            
            full_prompt = f"{system_prompt}\n{context}\nUser said: {text}\nAnalyze in Arabic:"
            
            try:
                response = model.generate_content(full_prompt).text
                bot.reply_to(message, response)
                
                if user_id not in user_memory: user_memory[user_id] = []
                user_memory[user_id].append(text)
                
                log_message(f"Replied to {user_id}")
            except Exception as e:
                log_message(f"Error: {e}")

        log_message("Bot started polling...")
        bot.infinity_polling()
        
    except Exception as e:
        log_message(f"Critical Error: {e}")

# --- أزرار التحكم ---
st.subheader("حالة التشغيل")

if st.button("🚀 تشغيل البوت"):
    if not tg_token or not gemini_key:
        st.error("الرجاء إدخال المفاتيح أولاً!")
    else:
        if not st.session_state.bot_running:
            st.session_state.bot_running = True
            st.success("تم بدء تشغيل البوت في الخلفية!")
            # تشغيل البوت في Thread منفصل لكي لا يجمد الموقع
            t = threading.Thread(target=run_bot, args=(tg_token, gemini_key))
            t.start()
        else:
            st.warning("البوت يعمل بالفعل!")

# --- عرض السجلات ---
st.divider()
st.subheader("📝 سجل العمليات (Logs)")
log_container = st.container()
with log_container:
    for log in reversed(st.session_state.logs[-10:]): # عرض آخر 10 عمليات
        st.code(log, language="text")
