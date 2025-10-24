# 🚀 E-Commerce Sevkiyat Optimizasyon Sistemi

## 📋 Genel Bakış

Bu sistem, e-ticaret operasyonlarında ürün sevkiyatını optimize etmek için geliştirilmiş akıllı bir modüldür. Ürünleri satış hızına göre segmentlere ayırır ve her segment için özel stratejiler uygular.

## 🎯 Özellikler

### 1. **Velocity-Based Segmentation**
Ürünler 5 ana segmente ayrılır:

- **🔥 HOT (Patlayanlar)**
  - Hızlı satan, yüksek trend
  - %80 Akyazı depo önceliği
  - 3 günlük reorder point
  - Otomatik transfer aktif

- **⭐ RISING STAR (Yükselen)**
  - Momentum yakalayan ürünler
  - %70 Akyazı önceliği
  - 4 günlük reorder point
  - Otomatik transfer aktif

- **✅ STEADY (Düzenli)**
  - Stabil satışlar
  - %60 Akyazı önceliği
  - 7 günlük reorder point
  - Manuel transfer

- **🐢 SLOW (Yavaş)**
  - Düşük satış hızı
  - OMS mağazalar öncelikli
  - 14 günlük reorder point
  - 30 gün sonra markdown değerlendirmesi

- **💀 DYING (Ölen)**
  - Satışı düşen/duran ürünler
  - Yeni stok alınmaz
  - ACIL markdown önerisi (7 gün)
  - Mevcut stoğu tüket stratejisi

### 2. **Akıllı Metrikler**

Sistem şu metrikleri hesaplar:

- **Velocity Score**: Son 7 gün / Son 30 gün satış hızı
- **Trend Score**: Dün / Son 7 gün momentum
- **Engagement Score**: Sepete ekleme / Görüntülenme oranı
- **Conversion Rate**: Satış / Sepete ekleme oranı
- **Days of Stock**: Mevcut stok kaç güne yeter
- **Final Score**: Tüm metriklerin ağırlıklı toplamı

### 3. **Otomatik Uyarı Sistemi**

- 🔴 **CRITICAL**: Stok 3 günden az (HOT/RISING_STAR ürünlerde)
- 🟡 **WARNING**: Trend yüksek ama stok orta
- 🔵 **INFO**: Markdown önerileri

### 4. **Depo Optimizasyonu**

- Akyazı (E-com deposu) - Tip 2 ürünler
- Ana Depo - Tip 1 ürünler
- OMS Mağazalar - Buffer/yedek stok

## 📊 Veri Yapısı

CSV dosyanız şu kolonları içermeli:

```
sku                     : Ürün kodu
product_name            : Ürün adı
category                : Kategori (Tekstil, Mutfak, vs)
tip                     : 1 (Ana depo) veya 2 (Akyazı)
price                   : Fiyat
margin_pct              : Kar marjı %
stock_akyazi            : Akyazı stok
stock_ana_depo          : Ana depo stok
stock_oms_total         : Toplam OMS stok
daily_sales_avg_30d     : Son 30 gün günlük ortalama satış
daily_sales_avg_7d      : Son 7 gün günlük ortalama satış
daily_sales_yesterday   : Dün satış
view_count_7d           : Son 7 gün görüntülenme
add_to_cart_7d          : Son 7 gün sepete ekleme
favorites_7d            : Son 7 gün favorilere ekleme
review_count            : Toplam yorum sayısı
avg_rating              : Ortalama puan
stock_out_days_last_30d : Son 30 günde kaç gün stoksuz kaldı
last_restock_date       : Son stok giriş tarihi
campaign_flag           : Kampanyada mı? (1/0)
```

## 🚀 Kullanım

### Adım 1: Veri Hazırlama
```bash
# CSV dosyanızı sample_data.csv formatında hazırlayın
```

### Adım 2: Analiz Çalıştırma
```bash
python shipment_optimizer.py
```

### Adım 3: Dashboard Oluşturma
```bash
python create_dashboard.py
```

## 📈 Çıktılar

Sistem 4 ana çıktı üretir:

1. **allocation_strategy.csv**
   - Her ürün için sevkiyat stratejisi
   - Hangi depodan gönderilecek
   - Transfer ihtiyaçları
   - Reorder point'ler

2. **critical_alerts.csv**
   - Kritik durum uyarıları
   - Aksiyon önerileri
   - Öncelik seviyeleri

3. **detailed_analysis.csv**
   - Tüm metriklerin detaylı analizi
   - Segment atamaları
   - Score'lar

4. **shipment_dashboard.png**
   - 9 panelli görsel dashboard
   - Segment dağılımı
   - Stok sağlığı analizi
   - Kategori performansı
   - Transfer ihtiyaçları

## 🎨 Dashboard Bileşenleri

Dashboard 9 ana görselleştirme içerir:

1. **Segment Dağılımı** (Pasta Grafik)
2. **Top 8 Satış Hızı** (Bar Chart)
3. **Stok vs Satış Hızı** (Scatter Plot)
4. **Velocity Score Dağılımı** (Histogram)
5. **Kategori Performansı** (Grouped Bar)
6. **Engagement vs Conversion** (Scatter)
7. **Depo Bazlı Stok Dağılımı** (Stacked Bar)
8. **Transfer İhtiyacı** (Bar Chart)
9. **Alert Summary** (Metin Özet)

## 💡 Stratejik Öneriler

### Kasım Sezon Hazırlığı İçin:

1. **Eylül-Ekim**: 
   - HOT/RISING_STAR ürünleri belirle
   - Agresif stok planı yap (%40-50 fazla)
   - Akyazı'ya önceden transfer et

2. **Kasım İlk Hafta**:
   - Günlük trend takibi yap
   - İlk 3 gün satışa göre reaksiyon ver
   - Otomatik transfer'i aktif et

3. **Kasım Ortası**:
   - Hızlı tükenen ürünlerde OMS'den çek
   - Ana depodan express transfer
   - Yavaşlayanları markdown'a hazırla

4. **Aralık-Ocak**:
   - DYING segment'i agresif markdown
   - Stok fazlasını temizle
   - Yeni sezona hafif gir

## 🔧 Parametre Optimizasyonu

Kendi ihtiyaçlarınıza göre `segment_params` içindeki değerleri ayarlayabilirsiniz:

```python
'HOT': {
    'reorder_days': 3,          # Daha erken sipariş için düşür
    'safety_stock_days': 5,     # Daha fazla buffer için arttır
    'allocation_pct': 0.80,     # Akyazı oranını ayarla
    'transfer_threshold': 0.7,  # Transfer tetikleyici
}
```

## 📞 Öneriler

### İyileştirmeler:
1. ✅ Gerçek zamanlı API entegrasyonu
2. ✅ Otomatik email/Slack uyarıları
3. ✅ ML-based demand forecasting
4. ✅ Dinamik fiyatlandırma önerisi
5. ✅ Tedarikçi lead time optimizasyonu

### Markdown Politikası Ekleyin:
- Sistem markdown önerileri veriyor
- Ancak uygulama için süreç/yetki gerekli
- %15 → %25 → %40 → %50 kademeli indirim

## 🎯 Hedef Metrikler

Bu sistem ile şunları hedefleyin:

- **Büyüme**: %20 → %30+ e-com growth
- **Stok Devir**: 60+ gün → 30-45 güne indir
- **Lost Sales**: %15 → %5 azalt
- **Markdown Loss**: %0 → kontrollü %10 kabul et
- **Servis Level**: HOT ürünlerde %95+ tutma

## 🚨 Dikkat Edilecekler

1. **Veri Kalitesi**: Güncel ve doğru veri kritik
2. **Kampanya Etkisi**: Campaign_flag'i doğru set edin
3. **Lead Time**: Transfer sürelerini gerçekçi tutun
4. **Kapasite**: Depo kapasitelerini göz önünde bulundurun
5. **Organizasyon**: Kararları kim verecek netleştirin

## 📝 Versiyon Geçmişi

- **v1.0** (Ekim 2024)
  - İlk versiyon
  - Velocity-based segmentation
  - Otomatik alert sistemi
  - Visual dashboard

---

**Geliştirici Notları:**
- Sistem Python 3.8+ gerektirir
- pandas, numpy, matplotlib, seaborn kütüphaneleri gerekli
- Gerçek zamanlı kullanım için API/database entegrasyonu eklenebilir

**Sorular/Öneriler:**
Bu bir MVP (Minimum Viable Product) versiyonudur. Gerçek implementasyon için:
- ERP entegrasyonu
- Gerçek zamanlı veri akışı
- User authentication
- Role-based access control
eklenmelidir.
