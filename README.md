# Kommunal hisoblagich

Oylik ko'rsatkich, hisoblagich surati va tarif bo'yicha hisob-kitob tizimi.

## Loyihaning maqsadi

Uy-joy boshqarmasi abonentlardan har oy hisoblagich ko'rsatkichini yig'adi. Abonent bot orqali raqamni va hisoblagich suratini yuboradi, tizim oldingi oy bilan farqini hisoblab tarifga ko'paytiradi va hisob chiqaradi. Nazoratchi shubhali ko'rsatkichlarni surat bo'yicha tekshiradi.

## Texnologiyalar

- Python, Django, Django REST Framework
- PostgreSQL
- aiogram 3 (Telegram bot)
- JWT autentifikatsiya (djangorestframework-simplejwt)
- django-filter (filtrlash)
- Pillow (rasm bilan ishlash)

## Loyiha strukturasi

```
kommunal_hisoblagich/
    config/          - loyiha sozlamalari (settings, urls)
    users/           - foydalanuvchi modeli va rollar
    subscribers/     - abonent, xizmat turi, hisoblagich
    billing/         - tarif, ko'rsatkich, hisob
    bot/             - Telegram bot (aiogram)
    media/           - yuklangan suratlar
    manage.py
    requirements.txt
    .env.example
```

## O'rnatish

### 1. Repositoryni klonlash

```
git clone <repo-url>
cd kommunal_hisoblagich
```

### 2. Virtual muhit yaratish

Windows:
```
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```
python -m venv venv
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish

```
pip install -r requirements.txt
```

### 4. PostgreSQL'da baza yaratish

`psql` yoki pgAdmin orqali:

```sql
CREATE DATABASE kommunal_db;
```

### 5. `.env` faylini sozlash

`.env.example` faylidan nusxa olib `.env` nomi bilan saqlang, so'ng qiymatlarni to'ldiring:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=kommunal_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
BOT_TOKEN=your-bot-token-here
API_BASE_URL=http://127.0.0.1:8000/api
BOT_API_USERNAME=your-username
BOT_API_PASSWORD=your-password
```

### 6. Migratsiya

```
python manage.py makemigrations
python manage.py migrate
```

### 7. Superuser yaratish

```
python manage.py createsuperuser
```

(Username, Phone va Password so'raladi)

### 8. Django serverni ishga tushirish

```
python manage.py runserver
```

Server: `http://127.0.0.1:8000/`
Admin panel: `http://127.0.0.1:8000/admin/`

### 9. Telegram botni ishga tushirish (alohida terminalda)

```
venv\Scripts\activate
python -m bot.main
```

**Eslatma:** Django server va bot bir vaqtda, ikkita alohida terminalda ishlashi kerak.

## Boshlang'ich ma'lumotlarni kiritish

Admin panel orqali quyidagilarni kiriting:

1. **Service types** — Suv, Elektr, Gaz (nomi va o'lchov birligi bilan)
2. **Subscribers** — abonentlar (hisob raqami, F.I.SH, manzil)
3. **Meters** — abonentlarga hisoblagich biriktirish
4. **Tariffs** — har bir xizmat turi uchun narx (`valid_from` sanasi bilan)

## API endpointlar

| Metod | Yo'l | Kim uchun | Nima qiladi |
|-------|------|-----------|-------------|
| POST | `/api/auth/login/` | Hammasi | JWT token olish |
| POST | `/api/auth/login/refresh/` | Hammasi | Tokenni yangilash |
| GET | `/api/services/` | Hammasi | Xizmat turlari ro'yxati |
| GET | `/api/tariffs/` | Admin | Tariflar tarixi (filter: service) |
| POST | `/api/tariffs/` | Admin | Yangi tarif kiritish |
| GET | `/api/subscribers/` | Admin, Nazoratchi | Abonentlar (qidiruv: hisob raqami, F.I.SH, manzil) |
| POST | `/api/subscribers/` | Admin | Yangi abonent qo'shish |
| GET | `/api/meters/` | Admin | Hisoblagichlar (filter: subscriber, service) |
| POST | `/api/meters/` | Admin | Hisoblagich qo'shish |
| POST | `/api/readings/` | Abonent | Ko'rsatkich yuborish (multipart: value + photo) |
| GET | `/api/readings/` | Nazoratchi, Admin | Ko'rsatkichlar (filter: period, status, service) |
| GET | `/api/readings/my/` | Abonent | O'z ko'rsatkichlari tarixi |
| POST | `/api/readings/{id}/approve/` | Nazoratchi | Tasdiqlash — hisob avtomatik chiqadi |
| POST | `/api/readings/{id}/reject/` | Nazoratchi | Rad etish (sababi bilan) |
| GET | `/api/invoices/` | Admin | Hisoblar (filter: period, is_paid, subscriber) |
| GET | `/api/invoices/my/` | Abonent | O'z hisoblari va umumiy qarzi |
| POST | `/api/invoices/{id}/pay/` | Admin | To'landi deb belgilash |
| GET | `/api/reports/debtors/` | Admin | Qarzdorlar ro'yxati |
| GET | `/api/reports/monthly/?period=2026-08` | Admin | Oylik yig'im hisoboti |

## Telegram bot buyruqlari

- `/start` — ro'yxatdan o'tish, hisob raqami orqali akkauntni bog'lash
- `/nazoratchi` — nazoratchi panelini ochish

### Abonent tugmalari
- **Ko'rsatkich yuborish** — hisoblagich tanlash, qiymat va surat yuborish
- **Mening hisoblarim** — oxirgi 6 oylik hisoblar
- **Qarzim** — umumiy to'lanmagan summa

### Nazoratchi tugmalari
- **Tekshirilmagan ko'rsatkichlar** — tasdiqlash yoki rad etish

## Rollar va huquqlar

| Rol | Huquqlari |
|-----|-----------|
| **Administrator** | Abonent, hisoblagich, tarif kiritadi; hisoblarni to'landi deb belgilaydi; hisobotlarni ko'radi |
| **Nazoratchi** | Yuborilgan ko'rsatkichlarni suratiga qarab tasdiqlaydi yoki rad etadi |
| **Abonent** | Bot orqali ko'rsatkich va surat yuboradi; o'z hisobini va qarzini ko'radi |

## Biznes qoidalar

- Sarf = joriy ko'rsatkich − oldingi tasdiqlangan ko'rsatkich (birinchi oyda `Meter.initial_value`dan hisoblanadi)
- Summa = sarf × ko'rsatkich davriga mos keladigan tarif narxi
- Hisob faqat tasdiqlangan ko'rsatkich uchun chiqadi
- Bir davrga bitta hisob (`Reading` bilan `OneToOne`)
- Tarif o'zgarsa eski hisoblar qayta hisoblanmaydi — narx nusxasi saqlanadi
- Ko'rsatkich yuborilgandan keyin abonent uni o'zgartira olmaydi, faqat nazoratchi rad etsa qayta yuborishi mumkin

## Ma'lumotlar bazasi tuzilishi

- **User** — AbstractUser'dan meros, `role`, `phone`, `telegram_id`
- **Subscriber** — abonent, `user`ga OneToOne (bo'lishi shart emas)
- **ServiceType** — Suv / Elektr / Gaz
- **Meter** — hisoblagich, `subscriber` va `service`ga bog'langan, `unique_together`
- **Tariff** — xizmat narxi tarixi, `valid_from` / `valid_to`
- **Reading** — oylik ko'rsatkich va surat, `unique_together (meter, period)`
- **Invoice** — hisob, `reading`ga OneToOne, narx nusxasi bilan

## Muallif

IT Shaharcha o'quv markazi — Mustaqil loyiha № 8