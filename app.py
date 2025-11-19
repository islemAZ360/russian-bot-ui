import streamlit as st
import telebot
import google.generativeai as genai
import threading
import json
import pandas as pd
import os
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Russian Bot Local DB", page_icon="📂", layout="wide")
st.title("📂 المعلم الروسي (نظام الملفات الشخصي)")
st.markdown("""
**كيف يعمل هذا النظام؟**
1. أدخل المفاتيح واضغط تشغيل.
2. تواصل مع البوت في تليجرام.
3. البيانات ستظهر هنا في الجدول.
4. **مهم:** قبل إغلاق الموقع، اضغط زر **تحميل البيانات** لتحفظها في جهازك.
5. في المرة القادمة، اضغط **رفع ملف** لاستعادة بياناتك القديمة.
""")

# --- ملف البيانات المؤقت ---
DATA_FILE = "russian_data.json"

# --- دوال التعامل مع الملفات ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_entry(entry):
    data = load_data()
    data.append(entry)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("🔑 الإعدادات")
    tg_token = st.text_input("Telegram Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    st.header("📤 استعادة نسخة سابقة")
    uploaded_file = st.file_uploader("ارفع ملف JSON القديم هنا", type=["json"])
    if uploaded_file is not None:
        try:
            old_data = json.load(uploaded_file)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(old_data, f, ensure_ascii=False, indent=4)
            st.success(f"تم استعادة {len(old_data)} عنصر بنجاح!")
        except Exception as e:
            st.error(f"الملف فاسد: {e}")

# --- وظيفة البوت (الخلفية) ---
def run_bot(token, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # نستخدم الفلاش للسرعة
        bot = telebot.TeleBot(token)

        @bot.message_handler(func=lambda m: True)
        def handle_message(message):
            user_text = message.text
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                
                # نطلب من جيميناي الرد بصيغة JSON لسهولة التخزين
                prompt = f"""
                Analyze this Russian text: "{user_text}"
                
                Task:
                1. Extract verbs (Infinitive + Aspect pair).
                2. Extract difficult vocabulary.
                3. Translate sentence to Arabic.
                
                OUTPUT FORMAT (Strict JSON):
                [
                  {{"type": "Verb", "russian": "word", "pair": "pair", "meaning": "arabic"}},
                  {{"type": "Word", "russian": "word", "pair": "None", "meaning": "arabic"}},
                  {{"type": "Translation", "russian": "Full Sentence", "pair": "-", "meaning": "Arabic Translation"}}
                ]
                Do not use Markdown code blocks. Just raw JSON string.
                """
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                
                # محاولة قراءة الرد وتحليله
                items = json.loads(clean_json)
                
                # حفظ العناصر في الملف المحلي
                saved_count = 0
                reply_msg = "🏁 **التحليل:**\n\n"
                
                for item in items:
                    # حفظ في الملف
                    save_entry(item)
                    saved_count += 1
                    
                    # تجهيز الرد للتليجرام
                    if item['type'] == 'Verb':
                        reply_msg += f"🔴 {item['russian']} ({item['pair']}) -> {item['meaning']}\n"
                    elif item['type'] == 'Word':
                        reply_msg += f"🟡 {item['russian']} -> {item['meaning']}\n"
                    elif item['type'] == 'Translation':
                        reply_msg += f"\n🇸🇦 **الترجمة:** {item['meaning']}\n"

                reply_msg += "\n✅ (تم الحفظ في ملف الموقع)"
                bot.reply_to(message, reply_msg)
                
            except Exception as e:
                bot.reply_to(message, f"⚠️ حدث خطأ في التحليل: {e}")
                print(f"Error: {e}")

        bot.infinity_polling()
        
    except Exception as e:
        print(f"Bot Crash: {e}")

# --- واجهة العرض والتحكم ---
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("🚀 تشغيل البوت"):
        if tg_token and gemini_key:
            st.toast("جاري تشغيل البوت...", icon="🤖")
            t = threading.Thread(target=run_bot, args=(tg_token, gemini_key))
            t.start()
        else:
            st.error("المفاتيح ناقصة!")

with col2:
    # زر تحديث الجدول يدوي
    if st.button("🔄 تحديث الجدول"):
        st.rerun()

# --- عرض البيانات ---
st.subheader("📊 البيانات المحفوظة حالياً")
current_data = load_data()

if current_data:
    df = pd.DataFrame(current_data)
    st.dataframe(df, use_container_width=True)
    
    # زر التنزيل (أهم ميزة)
    json_string = json.dumps(current_data, ensure_ascii=False, indent=4)
    st.download_button(
        label="📥 تحميل البيانات (JSON)",
        data=json_string,
        file_name="my_russian_progress.json",
        mime="application/json"
    )
else:
    st.info("الجدول فارغ. أرسل رسالة للبوت لتظهر هنا.")
