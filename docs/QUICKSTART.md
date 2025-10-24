# 🚀 STREAMLIT UYGULAMASI - HIZLI BAŞLANGIÇ

## ✅ Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlat
```bash
cd shipment_optimization
streamlit run app.py
```

Uygulama otomatik olarak tarayıcınızda açılacak: `http://localhost:8501`

## 📁 Klasör Yapısı

```
shipment_optimization/
│
├── app.py                      # 🏠 Ana Streamlit uygulaması
│
├── modules/                    # 🧩 Core modüller
│   ├── data_loader.py         # CSV yükleme
│   ├── analytics_engine.py    # Analiz ve segmentasyon
│   ├── allocation_optimizer.py # Sevkiyat stratejisi
│   ├── alert_manager.py       # Uyarı sistemi
│   └── visualizations.py      # Plotly charts
│
├── utils/                      # 🛠️ Yardımcı fonksiyonlar
│   ├── constants.py           # Sabitler, renkler
│   └── helpers.py             # Utility fonksiyonlar
│
├── data/                       # 📊 Veri dosyaları
│   └── sample_data.csv        # Örnek veri
│
├── config/                     # ⚙️ Konfigürasyon
│
└── pages/                      # 📄 Ekstra sayfalar (gelecek)
```

## 🎯 Kullanım

### İlk Adımlar:

1. **Uygulamayı Başlat**
   ```bash
   streamlit run app.py
   ```

2. **Sol Menüden "Veriyi Yükle ve Analiz Et" Butonuna Tıkla**
   - Sistem örnek veriyi yükleyecek
   - Otomatik analiz başlayacak
   - ~2-3 saniye sürer

3. **Menüden İstediğin Sayfaya Git**
   - 📊 Dashboard: Genel görünüm
   - 🔍 Ürün Analizi: Detaylı ürün incelemesi
   - 📦 Sevkiyat Stratejisi: Allocation planları
   - 🚨 Kritik Uyarılar: Acil aksiyonlar

## 📊 Kendi Verinizi Yüklemek

### CSV Format:

Dosyanız şu kolonları içermeli:

**Zorunlu Kolonlar:**
- `sku`: Ürün kodu
- `product_name`: Ürün adı
- `category`: Kategori
- `tip`: 1 (Ana depo) veya 2 (Akyazı)
- `price`: Fiyat
- `stock_akyazi`: Akyazı stok
- `stock_ana_depo`: Ana depo stok
- `stock_oms_total`: OMS toplam stok
- `daily_sales_avg_30d`: 30 günlük ortalama
- `daily_sales_avg_7d`: 7 günlük ortalama
- `daily_sales_yesterday`: Dün satış

**Opsiyonel Kolonlar:**
- `margin_pct`: Kar marjı %
- `view_count_7d`: Görüntülenme
- `add_to_cart_7d`: Sepete ekleme
- `favorites_7d`: Favorilere ekleme
- `review_count`: Yorum sayısı
- `avg_rating`: Ortalama puan
- `stock_out_days_last_30d`: Stoksuzluk günleri
- `campaign_flag`: Kampanyada mı (1/0)

### Veri Yükleme:

**Yöntem 1: Dosya Değiştir**
```bash
# Kendi CSV'nizi data/ klasörüne kopyalayın
cp your_data.csv shipment_optimization/data/sample_data.csv
```

**Yöntem 2: Kod İçinde** (gelecek özellik)
- "📥 Veri Yükleme" sayfasından drag & drop ile yükleyeceksiniz

## 🎨 Mevcut Özellikler

### ✅ Tamamlanmış:
- [x] Ana sayfa ve navigasyon
- [x] Veri yükleme ve validasyon
- [x] Otomatik segmentasyon (5 segment)
- [x] Metrik hesaplamaları (9 farklı metrik)
- [x] Dashboard sayfası
- [x] Interactive Plotly charts
- [x] Kritik uyarı sistemi
- [x] Sevkiyat stratejisi hesaplama

### 🔄 Geliştirme Aşamasında:
- [ ] Ürün Analizi sayfası (detaylı)
- [ ] Sevkiyat Stratejisi sayfası (detaylı)
- [ ] Ayarlar sayfası (parametre düzenleme)
- [ ] Veri yükleme sayfası (drag & drop)
- [ ] Excel export özelliği
- [ ] Tarihsel trend analizi

## 🔧 Özelleştirme

### Segment Parametrelerini Değiştir:

`utils/constants.py` dosyasındaki `DEFAULT_SEGMENT_PARAMS` içindeki değerleri düzenleyin:

```python
'HOT': {
    'reorder_days': 3,          # Yenileme günü
    'safety_stock_days': 5,     # Güvenlik stoğu
    'allocation_pct': 0.80,     # Akyazı oranı
    # ... diğer parametreler
}
```

### Renkleri Değiştir:

`utils/constants.py` içindeki `SEGMENT_COLORS` sözlüğünü düzenleyin.

## 🐛 Sorun Giderme

### Uygulama Başlamıyor:
```bash
# Streamlit'i yeniden yükle
pip install streamlit --upgrade --break-system-packages

# Port değiştir
streamlit run app.py --server.port 8502
```

### Veri Yüklenmiyor:
- CSV dosyasının `data/sample_data.csv` yolunda olduğundan emin olun
- Zorunlu kolonların eksik olmadığını kontrol edin
- Encoding UTF-8 olmalı

### Grafik Görünmüyor:
```bash
# Plotly'i yeniden yükle
pip install plotly --upgrade --break-system-packages
```

## 📱 Production Deployment

### Streamlit Cloud'a Deploy:

1. GitHub'a push edin
2. [share.streamlit.io](https://share.streamlit.io) adresine gidin
3. Repository'nizi seçin
4. `app.py` dosyasını belirtin
5. Deploy!

### Docker ile:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

## 💡 İpuçları

1. **Performans**: Büyük veri setleri için `@st.cache_data` decorator kullanın
2. **Güvenlik**: Production'da environment variables kullanın
3. **UI/UX**: Plotly grafiklerini interactive bırakın
4. **Testing**: Her modül için unit testler ekleyin

## 📞 Destek

Sorunlar için:
1. Console log'larını kontrol edin
2. `modules/` içindeki fonksiyonları debug edin
3. Streamlit documentation: https://docs.streamlit.io

## 🎉 Başarılar!

Artık profesyonel bir Streamlit uygulamanız var! 

Geliştirmeye devam etmek için:
- Yeni sayfalar ekleyin (pages/ klasörüne)
- Yeni modüller yazın (modules/ klasörüne)
- Custom componentler oluşturun

---
**Version:** 1.0.0  
**Created:** Ekim 2024  
**Last Updated:** Ekim 2024
