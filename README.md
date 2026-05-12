Márhamat, bul botqa tiyisli qollanba (README) faylınıń tolıq qaraqalpaqsha awdarması:Markdown# Nokis Bot 

Telegram bot — Nókis qalasındaǵı imaratlar hám jaylar haqqında maǵlıwmat beredi.

## Ornatıw

```bash
pip install -r requirements.txt
Sazlaw.env faylın ashıń hám tómendegilerdi toltırıń:Фрагмент кодаBOT_TOKEN=7xxxxxxxxxx:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_ID=123456789
BOT_TOKEN — @BotFather botınan alıńADMIN_ID — Ózińizdiń Telegram ID'ińiz (@userinfobot botınan bilip alsalız boladı)Iske túsiriwBashpython main.py
Fayllar dúzilisiPlaintextnokis_bot/
├── main.py           # Iske túsiriw noqatı (Entry point)
├── db.py             # JSON saqlaw (data/places.json)
├── keyboards.py      # Barlıq inline tuymeler
├── handlers/
│   ├── admin.py      # Admin: jay qosıw/ózgertiw/óshiriw (FSM)
│   └── user.py       # Paydalanıwshı: jaylardı kóriw
├── data/
│   └── places.json   # Avtomat túrde jaratıladı
├── .env
└── requirements.txt
Admin imkaniyatlarıTuymeFunkciyası➕ Jay qosıwFSM arqalı súwretler + atı + telefon + maǵlıwmat qosıw📋 Jaylardı kóriwBarlıq jaylar dizimi + óshiriw / ózgertiw🔙 ArqaǵaHárbir basqıshta biykar etiw yamasa arqaǵa qaytıwPaydalanıwshı imkaniyatları/start → Barlıq jaylar inline menyu retinde shıǵadıJay tuymesin basıw → Súwretler + atı (úlken hárip penen) + túsindirme + telefon nomeri🔙 Arqaǵa → Tiykarǵı menyuǵa qaytıw