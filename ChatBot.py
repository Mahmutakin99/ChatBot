import random
import speech_recognition as sr
import pyttsx3
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import datetime
import wikipedia

# API anahtarlarını gir
GEMINI_API_KEY = "GEMINI_API_KEY"
WEATHER_API_KEY = "WEATHER_API_KEY"
CITY = "Afyonkarahisar"  # Şehir adını istediğiniz gibi değiştirebilirsiniz

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-002')

def hava_durumu_mgm(il_ismi):
    url = f"https://www.mgm.gov.tr/tahmin/il-ve-ilceler.aspx?il={il_ismi}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            derece = soup.find("div", class_="havaAnlikDegerKapsul").find("span", class_="havaAnlikSicaklikDeger").text.strip()
            durum = soup.find("div", class_="havaAnlikDegerKapsul").find("span", class_="havaAnlikDurum").text.strip()
            return f"{il_ismi} için MGM hava durumu: {durum}, sıcaklık: {derece}°C"
        except Exception:
            return "Veri çekilemedi (MGM sayfa yapısı değişmiş olabilir)."
    else:
        return "MGM'den hava durumu alınamadı."

def hava_durumu(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&lang=tr&units=metric"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{city} için hava: {desc}, sıcaklık: {temp}°C"
    else:
        return "Hava durumu bilgisi alınamadı."

def hava_durumu_gemini(city):
    prompt = f"{city} ilinin güncel hava durumu nedir? Sadece kısa ve güncel bir özet ver."
    try:
        yanit = model.generate_content(prompt)
        return yanit.text
    except Exception as e:
        return f"Gemini API hatası: {e}"

def gemini_cevap(soru):
    try:
        yanit = model.generate_content(soru)
        return yanit.text
    except Exception as e:
        return f"Gemini API hatası: {e}"

def sesli_cevap(metin):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)# konuşma hızı
    engine.say(metin)
    engine.runAndWait()

def sesli_komut_al():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dinleniyor...")
        audio = r.listen(source)
    try:
        komut = r.recognize_google(audio, language="tr-TR")
        print("Sen:", komut)
        return komut
    except sr.UnknownValueError:
        print("Seni anlayamadım.")
        return ""
    except sr.RequestError:
        print("Google API hatası.")
        return ""

def cevap_ver(mesaj):
    mesaj = mesaj.lower()
    if "merhaba" in mesaj:
        return random.choice(["Merhaba!", "Selam!", "Hoş geldin!"])
    elif "nasılsın" in mesaj:
        return random.choice(["İyiyim, sen nasılsın?", "Harikayım! Sen?", "Gayet iyiyim!"])
    elif "adın ne" in mesaj:
        return "Ben ChatBot, kişisel asistanın!"
    elif "görüşürüz" in mesaj or "çık" in mesaj:
        return "Görüşmek üzere!"
    else:
        return "Bunu anlayamadım."

sohbet_gecmisi = []

# Şaka fonksiyonu
def saka_yap():
    sakalar = [
        "Neden bilgisayarlar asla acıkmaz? Çünkü onların çipi var!",
        "Bir yazılımcı neden güneşe bakamaz? Çünkü çok fazla bug var!",
        "Python neden yılan gibi sürünür? Çünkü kodu indentation ile akar!"
    ]
    return random.choice(sakalar)

# Wikipedia özet fonksiyonu
def wikipedia_ozet(sorgu):
    try:
        wikipedia.set_lang("tr")
        ozet = wikipedia.summary(sorgu, sentences=2)
        return ozet
    except Exception:
        return "Wikipedia'da bu konuda özet bulunamadı."

# Sohbet geçmişini kaydetme fonksiyonu
def sohbeti_kaydet(dosya_adi, sohbet):
    try:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            for satir in sohbet:
                f.write(satir + "\n")
        return "Sohbet geçmişi kaydedildi."
    except Exception as e:
        return f"Kayıt hatası: {e}"

print("Sesli ChatBot başlatıldı. Çıkmak için 'çık' de.")
while True:
    komut = sesli_komut_al()
    if not komut:
        continue
    sohbet_gecmisi.append(f"Kullanıcı: {komut}")
    if "çık" in komut.lower():
        sesli_cevap("Görüşmek üzere!")
        sohbet_gecmisi.append("ChatBot: Görüşmek üzere!")
        break
    elif "hava" in komut.lower():
        cevap = hava_durumu_mgm(CITY)
    elif "saat" in komut.lower() or "zaman" in komut.lower():
        cevap = f"Şu an saat: {datetime.datetime.now().strftime('%H:%M')}"
    elif "tarih" in komut.lower():
        cevap = f"Bugünün tarihi: {datetime.datetime.now().strftime('%d.%m.%Y')}"
    elif "şaka" in komut.lower():
        cevap = saka_yap()
    elif "wikipedia" in komut.lower():
        konu = komut.lower().replace("wikipedia", "").strip()
        if not konu:
            cevap = "Hangi konuda özet istediğini belirtmelisin."
        else:
            cevap = wikipedia_ozet(konu)
    elif "sohbeti kaydet" in komut.lower():
        cevap = sohbeti_kaydet("sohbet_gecmisi.txt", sohbet_gecmisi)
    else:
        cevap = gemini_cevap(komut)
    sohbet_gecmisi.append(f"ChatBot: {cevap}")
    print("ChatBot:", cevap)
    sesli_cevap(cevap)
