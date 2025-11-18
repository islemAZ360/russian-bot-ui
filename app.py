# --- وظيفة البوت (نسخة محسنة لمعالجة الأسماء) ---
def start_bot_thread(telegram_token, gemini_api_key, model_name):
    # تنظيف اسم الموديل (حذف كلمة models/ إذا وجدت)
    clean_model_name = model_name.replace("models/", "")
    print(f">>> Starting Bot with Model: {clean_model_name}")
    
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(clean_model_name)
        bot = telebot.TeleBot(telegram_token)

        @bot.message_handler(commands=['start'])
        def welcome(message):
            bot.reply_to(message, f"أهلاً! أنا أعمل الآن باستخدام النموذج: \n`{clean_model_name}`\nأرسل جملتك للتحليل.")

        @bot.message_handler(func=lambda m: True)
        def analyzer(message):
            text = message.text
            
            prompt = f"""
            Act as a professional Russian language tutor.
            User Input: "{text}"
            
            Task:
            1. If the input is a single word, provide detailed morphology, stress (ударение), and meaning.
            2. If it's a sentence, analyze grammatical structure, verb aspects (СВ/НСВ), and cases.
            3. Translate to Arabic correctly.
            """
            
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text, parse_mode='Markdown')
            except Exception as e:
                # رسالة خطأ أوضح
                bot.reply_to(message, f"⚠️ هذا النموذج ({clean_model_name}) لا يستجيب حالياً.\nالخطأ: {e}")
                print(f"Error: {e}")

        bot.infinity_polling()
        
    except Exception as e:
        print(f"Boot Error: {e}")
