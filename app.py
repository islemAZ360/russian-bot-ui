import streamlit as st
import telebot
import google.generativeai as genai
import threading

# --- إعداد الصفحة ---
st.set_page_config(page_title="Russian Bot Stable", page_icon="🛡️")
st.title("🛡️ المعلم الروسي (النسخة المستقرة)")
st.write("يعمل هذا البوت بمحرك **Gemini 1.5 Flash** لتجنب أخطاء 404 و Quota.")

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("🔑 المفاتيح")
    tg_token = st.text_input("Telegram Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    st.header("🧠 اختيار الدماغ")
    # هنا نضع الفلاش كخيار افتراضي لأنه الأضمن
    model_choice = st.selectbox(
        "اختر النموذج:", 
        ["gemini-1.5-flash", "gemini-1.5-pro-latest", "gemini-pro"],
        index=0 # الفلاش هو الافتراضي
    )
    st.caption("نصيحة: gemini-1.5-flash هو الأسرع والأكثر استقراراً حالياً.")

# --- وظيفة البوت ---
def run_bot(token, api_key, model_name):
    # تنظيف الاسم من أي زيادات قد تسبب خطأ 404
    clean_model = model_name.replace("models/", "").strip()
    print(f">>> Starting with: {clean_model}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(clean_model)
        bot = telebot.TeleBot(token)

        @bot.message_handler(func=lambda m: True)
        def handle_message(message):
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                
                # البرومبت
                prompt = f"""
                Act as a Russian language expert.
                Input: "{message.text}"
                Task:
                1. Analyze verbs (Aspect: СВ/НСВ).
                2. Explain difficult vocabulary.
                3. Translate to Arabic.
                """
                
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
                print("Success!")
                
            except Exception as
