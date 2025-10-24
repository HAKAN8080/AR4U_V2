# 📦 Sevkiyat Optimizasyon Sistemi - Proje Özeti

## 🎯 Proje Hedefi

E-commerce operasyonlarında ürün sevkiyatını optimize etmek ve %30 büyüme hedefine ulaşmak için velocity-based segmentation ve smart allocation kullanan bir Streamlit uygulaması.

## 📊 Temel Sorunlar ve Çözümler

### Sorunlar:
1. ❌ Büyüme hedefini yakalayamıyoruz (%20 yerine %30 olmalı)
2. ❌ Büyük satış dönemleri sonrası elde mal kalıyor
3. ❌ Kasım'da stok kırılması yaşanıyor
4. ❌ Markdown politikası yok, para donuyor
5. ❌ Excel bazlı yavaş karar mekanizması

### Çözümler:
1. ✅ **Velocity-based Segmentation**: Ürünleri hız/trend bazlı 5 segmente ayır
2. ✅ **Smart Allocation**: Segment bazlı optimal depo dağılımı
3. ✅ **Real-time Alerts**: Kritik stok durumlarını anında tespit et
4. ✅ **Markdown Engine**: Otomatik indirim önerileri
5. ✅ **Interactive Dashboard**: Hızlı karar destek sistemi

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI LAYER                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │Dashboard│  │ Product │  │Shipment │  │ Alerts  │       │
│  │  Page   │  │ Analysis│  │Strategy │  │  Page   │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
└───────┼───────────┼────────────┼─────────────┼─────────────┘
        │           │            │             │
        └───────────┴────────────┴─────────────┘
                        │
        ┌───────────────▼────────────────┐
        │    BUSINESS LOGIC LAYER        │
        │  ┌─────────────────────────┐   │
        │  │  Analytics Engine       │   │
        │  │  - Metrics calculation  │   │
        │  │  - Segmentation         │   │
        │  └──────────┬──────────────┘   │
        │             │                  │
        │  ┌──────────▼──────────────┐   │
        │  │  Allocation Optimizer   │   │
        │  │  - Strategy generation  │   │
        │  │  - Transfer planning    │   │
        │  └──────────┬──────────────┘   │
        │             │                  │
        │  ┌──────────▼──────────────┐   │
        │  │    Alert Manager        │   │
        │  │  - Alert generation     │   │
        │  │  - Prioritization       │   │
        │  └─────────────────────────┘   │
        └────────────────────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │       DATA LAYER               │
        │  ┌─────────────────────────┐   │
        │  │    Data Loader          │   │
        │  │  - CSV parsing          │   │
        │  │  - Validation           │   │
        │  │  - Preprocessing        │   │
        │  └─────────────────────────┘   │
        └────────────────────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │    VISUALIZATION LAYER         │
        │  ┌─────────────────────────┐   │
        │  │   Plotly Charts         │   │
        │  │  - Interactive plots    │   │
        │  │  - Real-time updates    │   │
        │  └─────────────────────────┘   │
        └────────────────────────────────┘
```

## 🔢 Algoritmalar ve Metrikler

### 1. Velocity Score
```python
velocity_score = daily_sales_7d / daily_sales_30d
```
- > 1.5: Hız artıyor (HOT potansiyeli)
- 0.8-1.2: Stabil (STEADY)
- < 0.5: Düşüyor (DYING)

### 2. Trend Score
```python
trend_score = daily_sales_yesterday / daily_sales_7d
```
- > 1.3: Güçlü momentum (HOT)
- > 1.2: Pozitif trend (RISING_STAR)
- < 1.0: Negatif trend

### 3. Days of Stock
```python
days_of_stock = total_stock / daily_sales_7d
```
- < 7 gün: Kritik (transfer gerekli)
- 30-45 gün: İdeal
- > 60 gün: Fazla (markdown düşün)

### 4. Final Score (Weighted)
```python
final_score = (
    velocity * 30 +
    trend * 25 +
    engagement * 15 +
    conversion * 10 +
    quality * 10 +
    stockout_penalty * 10
) * campaign_boost
```

## 🎨 Segmentation Logic

### HOT 🔥
**Kriterler:**
- velocity_score > 1.5
- trend_score > 1.3
- daily_sales > 15

**Strateji:**
- %80 Akyazı'da
- 3 günlük reorder point
- Otomatik transfer aktif
- Safety stock: 5 gün

### RISING_STAR ⭐
**Kriterler:**
- velocity_score: 1.2-1.5
- trend_score > 1.2
- engagement > 5%

**Strateji:**
- %70 Akyazı'da
- 4 günlük reorder point
- Otomatik transfer aktif
- Safety stock: 6 gün

### STEADY ✅
**Kriterler:**
- velocity_score: 0.8-1.2
- daily_sales > 5
- stockout < 3 gün

**Strateji:**
- %60 Akyazı'da
- 7 günlük reorder point
- Manuel transfer
- Safety stock: 10 gün

### SLOW 🐢
**Kriterler:**
- daily_sales < 5
- velocity > 0.5

**Strateji:**
- %30 Akyazı'da
- OMS öncelikli
- 14 günlük reorder
- Markdown: 30 gün sonra

### DYING 💀
**Kriterler:**
- velocity < 0.5
- VEYA days_of_stock > 60

**Strateji:**
- Yeni stok alma
- Mevcut stoğu tüket
- ACİL markdown (7 gün)

## 📈 Beklenen Impact

### Operasyonel:
- ✅ Stok kırılması: %15 → %5
- ✅ Stok devir hızı: 64 gün → 35 gün
- ✅ Servis seviyesi (HOT): %85 → %95
- ✅ Karar süresi: 2-3 saat → 5 dakika

### Finansal:
- ✅ E-com büyüme: %20 → %30+
- ✅ Stokta para donması: ↓ %40
- ✅ Lost sales: ↓ %60
- ✅ Markdown loss: Kontrollü %10

## 🛠️ Teknoloji Stack

### Frontend:
- **Streamlit**: Interactive UI framework
- **Plotly**: Interactive charts
- **HTML/CSS**: Custom styling

### Backend:
- **Python 3.9+**: Core language
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations

### Data:
- **CSV**: Data source (gelecekte DB)
- **Session State**: In-memory cache

## 📁 Dosya Yapısı Detayı

### Core Modules:

**data_loader.py** (235 satır)
- CSV loading & validation
- Data preprocessing
- Missing value handling
- Type conversion

**analytics_engine.py** (280 satır)
- 9 farklı metrik hesaplama
- Segmentasyon algoritması
- Segment özet istatistikleri
- Top/bottom performers

**allocation_optimizer.py** (245 satır)
- Sevkiyat stratejisi
- Transfer hesaplamaları
- Reorder önerileri
- Markdown adayları

**alert_manager.py** (260 satır)
- 5 tip alert: CRITICAL, WARNING, INFO
- Önceliklendirme algoritması
- Filtreleme ve raporlama

**visualizations.py** (220 satır)
- 10+ interactive chart tipi
- Plotly-based
- Custom color schemes
- Responsive design

### Utility Files:

**constants.py** (120 satır)
- Segment parametreleri
- Renk paleti
- KPI hedefleri
- Metrik ağırlıkları

**helpers.py** (85 satır)
- Number formatting
- Date utilities
- Export functions
- UI helpers

### Main App:

**app.py** (400+ satır)
- Navigation system
- Page routing
- Session state management
- 5 sayfa: Home, Dashboard, Product, Shipment, Alerts

## 🔮 Gelecek Özellikler (Roadmap)

### Sprint 1 (Tamamlandı):
- [x] Core modules
- [x] Dashboard
- [x] Basic visualizations
- [x] Alert system

### Sprint 2 (Sonraki):
- [ ] Ürün Analizi sayfası (detaylı)
- [ ] Sevkiyat Stratejisi sayfası (detaylı)
- [ ] Drag & drop veri yükleme
- [ ] Excel export

### Sprint 3 (İleri):
- [ ] Ayarlar sayfası (parametre düzenleme)
- [ ] Tarihsel trend analizi
- [ ] What-if simulasyonları
- [ ] Email/Slack alerts

### Sprint 4 (Production):
- [ ] Database integration (PostgreSQL)
- [ ] API endpoints (FastAPI)
- [ ] User authentication
- [ ] Role-based access control
- [ ] Automated reporting

## 🎓 Öğrenme Noktaları

### Bu Proje Size Şunları Öğretir:

1. **Streamlit Mastery**
   - Multi-page apps
   - Session state management
   - Custom components
   - Interactive widgets

2. **Data Analytics**
   - Segmentation algorithms
   - Metric design
   - Statistical analysis
   - Business intelligence

3. **Modular Architecture**
   - Clean code principles
   - Separation of concerns
   - Reusable components
   - Documentation

4. **Data Visualization**
   - Plotly charts
   - Interactive dashboards
   - Color theory
   - UX design

5. **Business Logic**
   - E-commerce operations
   - Supply chain optimization
   - Inventory management
   - Decision support systems

## 🏆 Best Practices

### Code Quality:
- ✅ Docstrings for all functions
- ✅ Type hints where applicable
- ✅ Error handling with try-catch
- ✅ Modular, testable code

### Performance:
- ✅ @st.cache_data for expensive ops
- ✅ Vectorized pandas operations
- ✅ Minimal dataframe copies
- ✅ Efficient filtering

### UX/UI:
- ✅ Consistent color scheme
- ✅ Clear navigation
- ✅ Helpful tooltips
- ✅ Responsive layout

### Documentation:
- ✅ README for setup
- ✅ QUICKSTART for usage
- ✅ Inline comments
- ✅ Architecture diagrams

## 🎯 Başarı Kriterleri

### Teknik:
- [x] Tüm modüller çalışıyor
- [x] UI responsive
- [x] Hata yönetimi var
- [x] Performans optimize

### İş:
- [ ] Karar süresi < 5 dakika
- [ ] Kullanıcı adoption > %80
- [ ] Doğruluk > %90
- [ ] Büyüme hedefe ulaşıyor

## 📞 İletişim ve Destek

- **GitHub**: (Proje linkini ekleyin)
- **Documentation**: [Streamlit Docs](https://docs.streamlit.io)
- **Plotly**: [Plotly Python](https://plotly.com/python/)

---

**🚀 Sonuç:**  
Bu sistem, e-commerce operasyonlarınızı next-level'a taşıyacak. Velocity-based segmentation ile doğru ürünleri, doğru zamanda, doğru yerde bulundurarak hem büyümeyi hem karlılığı artırıyoruz!

**İyi çalışmalar!** 🎉

