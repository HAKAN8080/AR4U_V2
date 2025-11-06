"""
Ayarlar Sayfası - Sistem Parametrelerini Düzenleme
"""
import streamlit as st
import pandas as pd
import copy
from utils.constants import (
    DEFAULT_SEGMENT_PARAMS, 
    METRIC_WEIGHTS, 
    TRANSFER_LEAD_TIME_DAYS,
    SEGMENT_EMOJI
)
from utils.helpers import show_success, show_warning, show_info

def show_settings_page():
    """Ayarlar sayfası ana fonksiyonu"""
    
    st.markdown("## ⚙️ Sistem Ayarları")
    
    st.info("""
    **💡 Bu sayfada sistem parametrelerini özelleştirebilirsiniz:**
    - Transfer ve lead time ayarları
    - Risk seviye eşikleri
    - Segment parametreleri
    - Metrik ağırlıkları
    - Alert kriterleri
    
    Değişiklikler sadece bu oturum için geçerlidir. Varsayılan ayarlara dönmek için "Reset" butonunu kullanın.
    """)
    
    # Session state'de custom params yoksa oluştur
    if 'custom_segment_params' not in st.session_state:
        st.session_state.custom_segment_params = copy.deepcopy(DEFAULT_SEGMENT_PARAMS)
    
    if 'custom_metric_weights' not in st.session_state:
        st.session_state.custom_metric_weights = copy.deepcopy(METRIC_WEIGHTS)
    
    if 'custom_transfer_lead_time' not in st.session_state:
        st.session_state.custom_transfer_lead_time = TRANSFER_LEAD_TIME_DAYS
    
    if 'custom_risk_levels' not in st.session_state:
        st.session_state.custom_risk_levels = {
            'critical_stock_days': 3,
            'warning_stock_days': 7,
            'ideal_stock_days': 30,
            'overstock_days': 60,
            'urgent_transfer_threshold': 5,
            'auto_transfer_min_qty': 10
        }
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚛 Transfer Ayarları",
        "🎯 Segment Parametreleri",
        "⚖️ Metrik Ağırlıkları",
        "🚨 Risk Seviyeleri",
        "💾 Kaydet & Reset"
    ])
    
    with tab1:
        show_transfer_settings()
    
    with tab2:
        show_segment_settings()
    
    with tab3:
        show_metric_weights_settings()
    
    with tab4:
        show_risk_levels_settings()
    
    with tab5:
        show_save_reset_settings()


def show_transfer_settings():
    """Transfer ve lead time ayarları"""
    
    st.markdown("### 🚛 Transfer ve Lead Time Ayarları")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Ana Depo → Akyazı Transfer Süresi")
        
        lead_time = st.number_input(
            "Transfer Lead Time (gün)",
            min_value=1,
            max_value=30,
            value=st.session_state.custom_transfer_lead_time,
            help="Ürünün ana depodan Akyazı'ya ulaşma süresi",
            key='lead_time_input'
        )
        
        st.caption(f"**Mevcut:** {lead_time} gün")
        st.caption("Transfer başlatıldıktan sonra ürün bu kadar gün sonra satışa hazır olur.")
        
        if lead_time != st.session_state.custom_transfer_lead_time:
            if st.button("Lead Time'ı Güncelle", key='update_lead_time'):
                st.session_state.custom_transfer_lead_time = lead_time
                st.session_state.custom_risk_levels['urgent_transfer_threshold'] = lead_time
                show_success(f"Lead time {lead_time} gün olarak güncellendi!")
                st.rerun()
    
    with col2:
        st.markdown("#### Transfer Kriterleri")
        
        urgent_threshold = st.number_input(
            "Urgent Transfer Eşiği (gün)",
            min_value=1,
            max_value=15,
            value=st.session_state.custom_risk_levels['urgent_transfer_threshold'],
            help="Akyazı stoğu bu günden az ise transfer acil sayılır",
            key='urgent_threshold_input'
        )
        
        auto_min_qty = st.number_input(
            "Auto Transfer Min Miktar (adet)",
            min_value=1,
            max_value=100,
            value=st.session_state.custom_risk_levels['auto_transfer_min_qty'],
            help="Bu adetten az transferler otomatik önerilmez",
            key='auto_min_qty_input'
        )
        
        if st.button("Transfer Kriterlerini Güncelle", key='update_transfer_criteria'):
            st.session_state.custom_risk_levels['urgent_transfer_threshold'] = urgent_threshold
            st.session_state.custom_risk_levels['auto_transfer_min_qty'] = auto_min_qty
            show_success("Transfer kriterleri güncellendi!")
            st.rerun()
    
    st.divider()
    
    # Açıklamalar
    st.markdown("### 📋 Transfer Mantığı")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Lead Time Etkisi:**
        
        Transfer süresi: {st.session_state.custom_transfer_lead_time} gün
        
        Bu süre boyunca satışlar devam eder ve stok tüketilir.
        
        Transfer ihtiyacı hesaplanırken lead time dahil edilir.
        """)
    
    with col2:
        st.warning(f"""
        **Urgent Transfer:**
        
        Eşik: {st.session_state.custom_risk_levels['urgent_transfer_threshold']} gün
        
        Akyazı stoğu bu günden az ise transfer ACİL sayılır.
        
        Transfer yolda iken stok bitme riski var.
        """)
    
    with col3:
        st.success(f"""
        **Auto Transfer:**
        
        Min miktar: {st.session_state.custom_risk_levels['auto_transfer_min_qty']} adet
        
        Bu adetten az transferler otomatik önerilmez.
        
        HOT ve RISING_STAR için aktif.
        """)


def show_segment_settings():
    """Segment parametreleri düzenleme"""
    
    st.markdown("### 🎯 Segment Parametreleri")
    
    st.info("""
    **Her segment için aşağıdaki parametreleri düzenleyebilirsiniz:**
    - Reorder Days: Sipariş verme eşiği (gün)
    - Safety Stock Days: Güvenlik stoğu (gün)
    - Allocation %: Akyazı'da olması gereken oran
    - Markdown Day: Markdown başlatma günü
    """)
    
    # Segment seçimi
    segments = ['HOT', 'RISING_STAR', 'STEADY', 'SLOW', 'DYING']
    selected_segment = st.selectbox(
        "Segment Seçin:",
        segments,
        format_func=lambda x: f"{SEGMENT_EMOJI.get(x, '❓')} {x}",
        key='segment_select'
    )
    
    params = st.session_state.custom_segment_params[selected_segment]
    
    st.markdown(f"### {SEGMENT_EMOJI.get(selected_segment, '❓')} {selected_segment} Parametreleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Stok Yönetimi")
        
        reorder_days = st.number_input(
            "Reorder Days (gün)",
            min_value=1,
            max_value=60,
            value=params['reorder_days'],
            help="Stok bu günden az olduğunda sipariş ver",
            key=f'reorder_{selected_segment}'
        )
        
        safety_stock_days = st.number_input(
            "Safety Stock Days (gün)",
            min_value=0,
            max_value=90,
            value=params['safety_stock_days'],
            help="Güvenlik stoğu süresi",
            key=f'safety_{selected_segment}'
        )
        
        allocation_pct = st.slider(
            "Akyazı Allocation %",
            min_value=0.0,
            max_value=1.0,
            value=params['allocation_pct'],
            step=0.05,
            format="%.0f%%",
            help="Toplam stokun bu oranı Akyazı'da olmalı",
            key=f'allocation_{selected_segment}'
        )
        
        markdown_day = st.number_input(
            "Markdown Day (gün)",
            min_value=0,
            max_value=999,
            value=params['markdown_day'],
            help="Stok bu günden fazla ise markdown öner (999 = asla)",
            key=f'markdown_{selected_segment}'
        )
    
    with col2:
        st.markdown("#### ⚙️ Diğer Ayarlar")
        
        auto_transfer = st.checkbox(
            "Auto Transfer Aktif",
            value=params['auto_transfer'],
            help="Bu segment için otomatik transfer önerisi yapılsın mı?",
            key=f'auto_{selected_segment}'
        )
        
        depot_priority = st.multiselect(
            "Depo Önceliği",
            ['akyazi', 'ana_depo', 'oms'],
            default=params['depot_priority'],
            help="Sevkiyat sırasında depo kullanım önceliği",
            key=f'depot_{selected_segment}'
        )
        
        st.markdown("**Segmentasyon Eşikleri:**")
        
        if 'velocity_min' in params:
            velocity_min = st.number_input(
                "Velocity Min",
                min_value=0.0,
                max_value=5.0,
                value=params.get('velocity_min', 1.0),
                step=0.1,
                key=f'vel_min_{selected_segment}'
            )
        
        if 'velocity_max' in params:
            velocity_max = st.number_input(
                "Velocity Max",
                min_value=0.0,
                max_value=5.0,
                value=params.get('velocity_max', 2.0),
                step=0.1,
                key=f'vel_max_{selected_segment}'
            )
    
    st.divider()
    
    # Kaydet butonu
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button(f"💾 {selected_segment} Parametrelerini Kaydet", key=f'save_{selected_segment}'):
            # Parametreleri güncelle
            st.session_state.custom_segment_params[selected_segment]['reorder_days'] = reorder_days
            st.session_state.custom_segment_params[selected_segment]['safety_stock_days'] = safety_stock_days
            st.session_state.custom_segment_params[selected_segment]['allocation_pct'] = allocation_pct
            st.session_state.custom_segment_params[selected_segment]['markdown_day'] = markdown_day
            st.session_state.custom_segment_params[selected_segment]['auto_transfer'] = auto_transfer
            st.session_state.custom_segment_params[selected_segment]['depot_priority'] = depot_priority
            
            if 'velocity_min' in params:
                st.session_state.custom_segment_params[selected_segment]['velocity_min'] = velocity_min
            if 'velocity_max' in params:
                st.session_state.custom_segment_params[selected_segment]['velocity_max'] = velocity_max
            
            show_success(f"{selected_segment} parametreleri kaydedildi!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Bu Segmenti Varsayılana Dön", key=f'reset_{selected_segment}'):
            st.session_state.custom_segment_params[selected_segment] = copy.deepcopy(
                DEFAULT_SEGMENT_PARAMS[selected_segment]
            )
            show_success(f"{selected_segment} varsayılan değerlere döndürüldü!")
            st.rerun()
    
    # Mevcut parametreleri göster
    with st.expander("📊 Mevcut Parametreleri Görüntüle"):
        st.json(st.session_state.custom_segment_params[selected_segment])


def show_metric_weights_settings():
    """Metrik ağırlıkları ayarlama"""
    
    st.markdown("### ⚖️ Metrik Ağırlıkları")
    
    st.info("""
    **Final Score Hesaplama:**
    
    Ürünlerin final score'u bu metriklerin ağırlıklı toplamıdır.
    Ağırlıkları değiştirerek hangi metriklerin daha önemli olduğunu belirleyebilirsiniz.
    
    **Not:** Toplam %100 olmalıdır.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        velocity_weight = st.slider(
            "🚀 Velocity Score",
            min_value=0,
            max_value=100,
            value=st.session_state.custom_metric_weights['velocity_score'],
            help="Satış hızı değişimi ağırlığı",
            key='velocity_weight'
        )
        
        trend_weight = st.slider(
            "📈 Trend Score",
            min_value=0,
            max_value=100,
            value=st.session_state.custom_metric_weights['trend_score'],
            help="Momentum ağırlığı",
            key='trend_weight'
        )
        
        engagement_weight = st.slider(
            "👁️ Engagement Score",
            min_value=0,
            max_value=100,
            value=st.session_state.custom_metric_weights['engagement_score'],
            help="İlgi oranı ağırlığı",
            key='engagement_weight'
        )
    
    with col2:
        conversion_weight = st.slider(
            "🎯 Conversion Rate",
            min_value=0,
            max_value=100,
            value=st.session_state.custom_metric_weights['conversion_rate'],
            help="Dönüşüm oranı ağırlığı",
            key='conversion_weight'
        )
        
        quality_weight = st.slider(
            "⭐ Quality Score",
            min_value=0,
            max_value=100,
            value=st.session_state.custom_metric_weights['quality_score'],
            help="Ürün kalitesi ağırlığı",
            key='quality_weight'
        )
        
        stockout_weight = st.slider(
            "📦 Stockout Penalty",
            min_value=0,
            max_value=100,
            value=st.session_state.custom_metric_weights['stockout_penalty'],
            help="Stoksuzluk cezası ağırlığı",
            key='stockout_weight'
        )
    
    # Toplam kontrol
    total_weight = (
        velocity_weight + trend_weight + engagement_weight +
        conversion_weight + quality_weight + stockout_weight
    )
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if total_weight == 100:
            st.success(f"✅ Toplam: {total_weight}%")
        else:
            st.error(f"❌ Toplam: {total_weight}% (100% olmalı!)")
    
    with col2:
        if total_weight == 100:
            if st.button("💾 Ağırlıkları Kaydet", key='save_weights'):
                st.session_state.custom_metric_weights = {
                    'velocity_score': velocity_weight,
                    'trend_score': trend_weight,
                    'engagement_score': engagement_weight,
                    'conversion_rate': conversion_weight,
                    'quality_score': quality_weight,
                    'stockout_penalty': stockout_weight
                }
                show_success("Metrik ağırlıkları kaydedildi!")
                st.rerun()
        else:
            st.button("💾 Ağırlıkları Kaydet", disabled=True, key='save_weights_disabled')
    
    # Varsayılana dön
    if st.button("🔄 Varsayılan Ağırlıklara Dön", key='reset_weights'):
        st.session_state.custom_metric_weights = copy.deepcopy(METRIC_WEIGHTS)
        show_success("Ağırlıklar varsayılan değerlere döndürüldü!")
        st.rerun()
    
    # Grafik gösterimi
    st.divider()
    
    st.markdown("### 📊 Mevcut Ağırlık Dağılımı")
    
    weights_df = pd.DataFrame({
        'Metrik': ['Velocity', 'Trend', 'Engagement', 'Conversion', 'Quality', 'Stockout'],
        'Ağırlık': [
            velocity_weight, trend_weight, engagement_weight,
            conversion_weight, quality_weight, stockout_weight
        ]
    })
    
    st.bar_chart(weights_df.set_index('Metrik'))


def show_risk_levels_settings():
    """Risk seviyesi ayarları"""
    
    st.markdown("### 🚨 Risk Seviye Eşikleri")
    
    st.info("""
    **Risk seviyeleri uyarı ve alert sisteminde kullanılır.**
    
    Bu eşiklere göre ürünler kategorize edilir ve aksiyonlar önerilir.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Stok Günü Eşikleri")
        
        critical_days = st.number_input(
            "🔴 Kritik Seviye (gün)",
            min_value=1,
            max_value=10,
            value=st.session_state.custom_risk_levels['critical_stock_days'],
            help="Bu günden az stok CRITICAL alert",
            key='critical_days'
        )
        
        warning_days = st.number_input(
            "🟡 Uyarı Seviyesi (gün)",
            min_value=1,
            max_value=20,
            value=st.session_state.custom_risk_levels['warning_stock_days'],
            help="Bu günden az stok WARNING alert",
            key='warning_days'
        )
        
        ideal_days = st.number_input(
            "🟢 İdeal Stok Günü",
            min_value=10,
            max_value=60,
            value=st.session_state.custom_risk_levels['ideal_stock_days'],
            help="Hedeflenen ideal stok süresi",
            key='ideal_days'
        )
        
        overstock_days = st.number_input(
            "⚠️ Fazla Stok Eşiği (gün)",
            min_value=30,
            max_value=180,
            value=st.session_state.custom_risk_levels['overstock_days'],
            help="Bu günden fazla stok markdown adayı",
            key='overstock_days'
        )
    
    with col2:
        st.markdown("#### 📊 Risk Görselleştirme")
        
        # Risk aralıklarını göster
        st.markdown(f"""
        **Mevcut Eşikler:**
        
        - 🔴 **Kritik:** 0 - {critical_days} gün
        - 🟡 **Uyarı:** {critical_days} - {warning_days} gün
        - 🟢 **İdeal:** {ideal_days} ± 10 gün
        - ⚪ **Normal:** {warning_days} - {overstock_days} gün
        - ⚠️ **Fazla:** > {overstock_days} gün
        """)
        
        # Özet tablo
        risk_summary = pd.DataFrame({
            'Seviye': ['Kritik', 'Uyarı', 'İdeal', 'Fazla'],
            'Gün': [f'< {critical_days}', f'< {warning_days}', f'~{ideal_days}', f'> {overstock_days}'],
            'Aksiyon': ['ACİL transfer/sipariş', 'Transfer hazırla', 'İzle', 'Markdown başlat']
        })
        
        st.dataframe(risk_summary, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Kaydet
    if st.button("💾 Risk Seviyelerini Kaydet", key='save_risk_levels'):
        st.session_state.custom_risk_levels['critical_stock_days'] = critical_days
        st.session_state.custom_risk_levels['warning_stock_days'] = warning_days
        st.session_state.custom_risk_levels['ideal_stock_days'] = ideal_days
        st.session_state.custom_risk_levels['overstock_days'] = overstock_days
        show_success("Risk seviyeleri kaydedildi!")
        st.rerun()


def show_save_reset_settings():
    """Kaydetme ve reset işlemleri"""
    
    st.markdown("### 💾 Ayarları Kaydet & Reset")
    
    st.warning("""
    **⚠️ ÖNEMLİ:**
    
    - Yaptığınız değişiklikler sadece bu oturum için geçerlidir
    - Sayfayı yenilediğinizde veya uygulamayı kapattığınızda ayarlar kaybolur
    - Kalıcı değişiklik için `constants.py` dosyasını düzenleyin
    - Değişiklikler analizleri yeniden çalıştırmayı gerektirir
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 Analizi Yenile")
        
        st.info("""
        Parametreleri değiştirdikten sonra analizi yeniden çalıştırın.
        
        Bu işlem:
        - Metrikleri yeniden hesaplar
        - Segmentleri günceller
        - Allocation stratejisini yeniler
        - Alert'leri günceller
        """)
        
        if st.button("🔄 Analizi Yeniden Çalıştır", use_container_width=True, type="primary"):
            if st.session_state.data_loaded:
                with st.spinner("Analiz yeniden çalıştırılıyor..."):
                    from modules.analytics_engine import AnalyticsEngine
                    from modules.allocation_optimizer import AllocationOptimizer
                    from modules.alert_manager import AlertManager
                    
                    df = st.session_state.df
                    
                    # Yeni parametrelerle analiz
                    analytics = AnalyticsEngine(
                        df,
                        segment_params=st.session_state.custom_segment_params
                    )
                    df = analytics.calculate_all_metrics()
                    df = analytics.segment_products()
                    
                    # Allocation optimizer
                    optimizer = AllocationOptimizer(
                        df,
                        segment_params=st.session_state.custom_segment_params,
                        transfer_lead_time=st.session_state.custom_transfer_lead_time
                    )
                    allocation_df = optimizer.generate_allocation_strategy()
                    
                    # Alerts
                    alert_mgr = AlertManager(df, allocation_df)
                    alerts_df = alert_mgr.generate_all_alerts()
                    
                    # Session state'i güncelle
                    st.session_state.df = df
                    st.session_state.allocation_df = allocation_df
                    st.session_state.alerts_df = alerts_df
                    st.session_state.analytics = analytics
                    st.session_state.optimizer = optimizer
                    st.session_state.alert_mgr = alert_mgr
                    
                    show_success("✅ Analiz yeni parametrelerle tamamlandı!")
                    st.balloons()
            else:
                show_warning("⚠️ Önce veri yükleyin!")
    
    with col2:
        st.markdown("### 🔄 Varsayılan Ayarlara Dön")
        
        st.error("""
        **DİKKAT:**
        
        Bu işlem TÜM özel ayarlarınızı siler ve varsayılan değerlere döner.
        
        - Transfer ayarları
        - Segment parametreleri
        - Metrik ağırlıkları
        - Risk seviyeleri
        """)
        
        if st.button("⚠️ TÜM AYARLARI SIFIRLA", use_container_width=True, type="secondary"):
            # Onay dialogu
            st.session_state.custom_segment_params = copy.deepcopy(DEFAULT_SEGMENT_PARAMS)
            st.session_state.custom_metric_weights = copy.deepcopy(METRIC_WEIGHTS)
            st.session_state.custom_transfer_lead_time = TRANSFER_LEAD_TIME_DAYS
            st.session_state.custom_risk_levels = {
                'critical_stock_days': 3,
                'warning_stock_days': 7,
                'ideal_stock_days': 30,
                'overstock_days': 60,
                'urgent_transfer_threshold': 5,
                'auto_transfer_min_qty': 10
            }
            show_success("✅ Tüm ayarlar varsayılana döndürüldü!")
            st.rerun()
    
    st.divider()
    
    # Mevcut ayarları göster
    st.markdown("### 📊 Mevcut Özel Ayarlar")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Transfer Ayarları",
        "Segment Parametreleri",
        "Metrik Ağırlıkları",
        "Risk Seviyeleri"
    ])
    
    with tab1:
        st.json({
            'transfer_lead_time': st.session_state.custom_transfer_lead_time,
            'risk_levels': st.session_state.custom_risk_levels
        })
    
    with tab2:
        # Sadece değişen segmentleri göster
        changed_segments = {}
        for segment in st.session_state.custom_segment_params:
            if st.session_state.custom_segment_params[segment] != DEFAULT_SEGMENT_PARAMS[segment]:
                changed_segments[segment] = st.session_state.custom_segment_params[segment]
        
        if changed_segments:
            st.json(changed_segments)
        else:
            st.info("Hiçbir segment parametresi değiştirilmedi.")
    
    with tab3:
        st.json(st.session_state.custom_metric_weights)
    
    with tab4:
        st.json(st.session_state.custom_risk_levels)
