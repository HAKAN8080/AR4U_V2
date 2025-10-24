"""
🚀 E-Commerce Sevkiyat Optimizasyon Sistemi
Ana Streamlit Uygulaması - ÜST MENÜ VERSİYONU
"""
import streamlit as st
import pandas as pd
from modules.data_loader import DataLoader
from modules.analytics_engine import AnalyticsEngine
from modules.allocation_optimizer import AllocationOptimizer
from modules.alert_manager import AlertManager
from modules.visualizations import Visualizations
from utils.helpers import (
    format_number, format_currency, format_percentage,
    show_success, show_error, show_info
)
from utils.constants import KPI_TARGETS, SEGMENT_COLORS, SEGMENT_EMOJI

# Sayfa konfigürasyonu - YAN MENÜYÜ KAPATIYORUZ
st.set_page_config(
    page_title="Sevkiyat Optimizasyonu",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"  # Yan menüyü kapattık
)

# Custom CSS - ÜST MENÜ STİLLERİ
st.markdown("""
    <style>
    /* Yan menüyü tamamen gizle */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Header'ı gizle */
    header {
        visibility: hidden;
    }
    
    /* Üst menü konteyneri */
    .top-menu {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        margin: -50px 0 20px 0;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Menü items */
    .menu-items {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 0;
        margin: 0;
    }
    
    /* Menü butonları */
    .menu-btn {
        background: none;
        border: none;
        color: white;
        padding: 15px 25px;
        margin: 0 5px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        border-radius: 0;
        transition: all 0.3s ease;
        text-decoration: none;
        flex: 1;
        text-align: center;
    }
    
    .menu-btn:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-2px);
    }
    
    .menu-btn.active {
        background: rgba(255,255,255,0.3);
        border-bottom: 3px solid white;
    }
    
    /* Logo ve başlık */
    .header-title {
        text-align: center;
        padding: 15px;
        background: rgba(255,255,255,0.1);
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 0;
    }
    
    /* Ana başlık */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stAlert {
        padding: 1rem;
        border-radius: 5px;
    }
    
    /* Sayfa içeriği */
    .page-content {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Veri yükleme butonu */
    .data-load-btn {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .data-load-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(255,107,107,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

def load_and_analyze_data():
    """Veri yükle ve analiz et"""
    
    with st.spinner('🔄 Veri yükleniyor ve analiz ediliyor...'):
        # Data loader
        loader = DataLoader()
        df = loader.load_sample_data()
        
        if df is not None:
            # Analytics engine
            analytics = AnalyticsEngine(df)
            df = analytics.calculate_all_metrics()
            df = analytics.segment_products()
            
            # Allocation optimizer
            optimizer = AllocationOptimizer(df)
            allocation_df = optimizer.generate_allocation_strategy()
            
            # Alert manager
            alert_mgr = AlertManager(df, allocation_df)
            alerts_df = alert_mgr.generate_all_alerts()
            
            # Session state'e kaydet
            st.session_state.df = df
            st.session_state.allocation_df = allocation_df
            st.session_state.alerts_df = alerts_df
            st.session_state.analytics = analytics
            st.session_state.optimizer = optimizer
            st.session_state.alert_mgr = alert_mgr
            st.session_state.data_loaded = True
            st.session_state.analyzed = True
            
            show_success("Analiz tamamlandı!")
            return True
        else:
            show_error("Veri yüklenemedi!")
            return False

def create_top_menu():
    """Üst menüyü oluştur"""
    
    # JavaScript için
    st.markdown("""
    <script>
    function setPage(page) {
        // Streamlit ile iletişim
        const data = {page: page};
        window.parent.postMessage(data, '*');
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Üst menü
    st.markdown("""
    <div class="top-menu">
        <div class="header-title">
            📦 E-Commerce Sevkiyat Optimizasyonu
        </div>
        <div class="menu-items">
            <button class="menu-btn %s" onclick="setPage('home')">🏠 Ana Sayfa</button>
            <button class="menu-btn %s" onclick="setPage('dashboard')">📊 Dashboard</button>
            <button class="menu-btn %s" onclick="setPage('analysis')">🔍 Ürün Analizi</button>
            <button class="menu-btn %s" onclick="setPage('shipment')">📦 Sevkiyat Stratejisi</button>
            <button class="menu-btn %s" onclick="setPage('alerts')">🚨 Kritik Uyarılar</button>
            <button class="menu-btn %s" onclick="setPage('settings')">⚙️ Ayarlar</button>
        </div>
    </div>
    """ % (
        'active' if st.session_state.current_page == 'home' else '',
        'active' if st.session_state.current_page == 'dashboard' else '',
        'active' if st.session_state.current_page == 'analysis' else '',
        'active' if st.session_state.current_page == 'shipment' else '',
        'active' if st.session_state.current_page == 'alerts' else '',
        'active' if st.session_state.current_page == 'settings' else ''
    ), unsafe_allow_html=True)

def main():
    """Ana uygulama"""
    
    # Üst menüyü oluştur
    create_top_menu()
    
    # Veri yükleme butonu - üstte
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 VERİYİ YÜKLE VE ANALİZ ET", 
                    use_container_width=True, 
                    type="primary" if not st.session_state.data_loaded else "secondary"):
            if load_and_analyze_data():
                st.rerun()
    
    # Veri durumu göstergesi
    if st.session_state.data_loaded:
        st.success(f"✅ Veri yüklü - {len(st.session_state.df)} ürün analiz edildi")
    else:
        st.warning("⚠️ Lütfen veriyi yükleyin")
    
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    # Sayfa içerikleri
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "dashboard":
        if st.session_state.data_loaded:
            show_dashboard_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif st.session_state.current_page == "analysis":
        if st.session_state.data_loaded:
            show_product_analysis_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif st.session_state.current_page == "shipment":
        if st.session_state.data_loaded:
            show_shipment_strategy_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif st.session_state.current_page == "alerts":
        if st.session_state.data_loaded:
            show_alerts_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif st.session_state.current_page == "settings":
        show_settings_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

# JavaScript event listener için
components.html("""
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.page) {
        // Streamlit'e mesaj gönder
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: event.data.page
        }, '*');
    }
});
</script>
""", height=0)

def show_home_page():
    """Ana sayfa"""
    
    st.markdown('<div class="main-header">👋 Hoşgeldiniz!</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Bu sistem, e-ticaret operasyonlarınızda ürün sevkiyatını optimize etmek için geliştirilmiştir.
    
    ### 🎯 Özellikler:
    
    - **📊 Dashboard**: Genel görünüm ve KPI'lar
    - **🔍 Ürün Analizi**: Detaylı ürün bazlı analiz
    - **📦 Sevkiyat Stratejisi**: Optimal sevkiyat planları
    - **🚨 Kritik Uyarılar**: Acil aksiyon gerektiren durumlar
    - **⚙️ Ayarlar**: Segment parametrelerini özelleştir
    
    ### 🚀 Başlamak için:
    
    1. Yukarıdaki **"VERİYİ YÜKLE VE ANALİZ ET"** butonuna tıklayın
    2. Sistem otomatik olarak analizleri çalıştıracak
    3. Üst menüden istediğiniz sayfaya gidin
    """)
    
    # Quick stats (eğer veri yüklüyse)
    if st.session_state.data_loaded:
        st.divider()
        st.markdown("### 📈 Hızlı Özet")
        
        df = st.session_state.df
        allocation_df = st.session_state.allocation_df
        alerts_df = st.session_state.alerts_df
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Toplam Ürün",
                format_number(len(df)),
                help="Sistemdeki toplam ürün sayısı"
            )
        
        with col2:
            hot_count = len(df[df['segment'] == 'HOT'])
            st.metric(
                "🔥 HOT Ürünler",
                hot_count,
                help="Hızlı satan ürünler"
            )
        
        with col3:
            critical_count = len(alerts_df[alerts_df['level'] == 'CRITICAL'])
            st.metric(
                "🔴 Kritik Uyarı",
                critical_count,
                delta=None if critical_count == 0 else f"-{critical_count}",
                delta_color="inverse",
                help="Acil aksiyon gerektiren uyarılar"
            )
        
        with col4:
            avg_stock_days = df['days_of_stock'].mean()
            st.metric(
                "Ortalama Stok Günü",
                f"{avg_stock_days:.0f}",
                delta=f"{avg_stock_days - 30:.0f} gün (hedef 30)",
                delta_color="inverse" if avg_stock_days > 30 else "normal",
                help="Mevcut stok kaç güne yeter"
            )
    
    # Info boxes
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **💡 İpucu:**  
        Sistem ürünleri satış hızına göre 5 segmente ayırır:
        - 🔥 HOT (Patlayanlar)
        - ⭐ RISING STAR (Yükselenler)
        - ✅ STEADY (Düzenli)
        - 🐢 SLOW (Yavaş)
        - 💀 DYING (Ölenler)
        """)
    
    with col2:
        st.success("""
        **🎯 Hedefler:**  
        - %30 e-com büyüme
        - HOT ürünlerde %95 servis seviyesi
        - 35 günlük ideal stok devri
        - Kontrollü %10 maksimum markdown
        """)

def show_dashboard_page():
    """Dashboard sayfası"""
    
    st.markdown("## 📊 Executive Dashboard")
    
    df = st.session_state.df
    allocation_df = st.session_state.allocation_df
    analytics = st.session_state.analytics
    viz = Visualizations()
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Toplam Ürün",
            format_number(len(df))
        )
    
    with col2:
        total_value = (df['total_stock'] * df['price']).sum()
        st.metric(
            "Stok Değeri",
            format_currency(total_value)
        )
    
    with col3:
        daily_forecast = allocation_df['forecasted_daily_sales'].sum()
        st.metric(
            "Günlük Satış Tahmini",
            format_number(daily_forecast, 0)
        )
    
    with col4:
        hot_count = len(df[df['segment'] == 'HOT'])
        st.metric(
            "🔥 HOT Ürünler",
            hot_count
        )
    
    with col5:
        dying_count = len(df[df['segment'] == 'DYING'])
        st.metric(
            "💀 DYING Ürünler",
            dying_count,
            delta=f"-{dying_count}" if dying_count > 0 else None,
            delta_color="inverse"
        )
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Genel Görünüm", "📊 Segment Analizi", "🏪 Depo Durumu"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                viz.segment_pie_chart(df),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                viz.velocity_histogram(df),
                use_container_width=True
            )
        
        st.plotly_chart(
            viz.stock_health_scatter(df),
            use_container_width=True
        )
        
        st.plotly_chart(
            viz.category_performance_bar(df),
            use_container_width=True
        )
    
    with tab2:
        segment_summary = analytics.get_segment_summary()
        
        st.markdown("### Segment Performansı")
        st.dataframe(
            segment_summary.style.format({
                'total_stock': '{:,.0f}',
                'stock_value': '₺{:,.2f}',
                'avg_velocity': '{:.2f}',
                'avg_trend': '{:.2f}',
                'total_daily_sales': '{:.1f}',
                'avg_days_of_stock': '{:.1f}',
                'avg_final_score': '{:.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔥 Top 10 Performans")
            top_df = analytics.get_top_performers(10)
            st.dataframe(top_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📉 Bottom 10 Performans")
            bottom_df = analytics.get_bottom_performers(10)
            st.dataframe(bottom_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.plotly_chart(
            viz.depot_stacked_bar(df),
            use_container_width=True
        )
        
        st.plotly_chart(
            viz.transfer_needs_bar(allocation_df),
            use_container_width=True
        )
        
        # Depo özeti
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🏢 Akyazı Stok",
                format_number(df['stock_akyazi'].sum())
            )
        
        with col2:
            st.metric(
                "🏭 Ana Depo Stok",
                format_number(df['stock_ana_depo'].sum())
            )
        
        with col3:
            st.metric(
                "🏪 OMS Stok",
                format_number(df['stock_oms_total'].sum())
            )

def show_product_analysis_page():
    """Ürün analizi sayfası"""
    st.markdown("## 🔍 Ürün Analizi")
    st.info("Bu sayfa yakında eklenecek...")

def show_shipment_strategy_page():
    """Sevkiyat stratejisi sayfası"""
    st.markdown("## 📦 Sevkiyat Stratejisi")
    st.info("Bu sayfa yakında eklenecek...")

def show_alerts_page():
    """Kritik uyarılar sayfası"""
    st.markdown("## 🚨 Kritik Uyarılar")
    
    alerts_df = st.session_state.alerts_df
    
    if len(alerts_df) == 0:
        st.success("✅ Kritik durum yok! Her şey güzel.")
        return
    
    # Alert özeti
    alert_summary = st.session_state.alert_mgr.get_alert_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Uyarı", alert_summary['total'])
    with col2:
        st.metric("🔴 CRITICAL", alert_summary['critical'])
    with col3:
        st.metric("🟡 WARNING", alert_summary['warning'])
    with col4:
        st.metric("🔵 INFO", alert_summary['info'])
    
    st.divider()
    
    # Alert listesi
    for idx, alert in alerts_df.head(20).iterrows():
        level_emoji = {'CRITICAL': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}.get(alert['level'], '⚪')
        
        with st.expander(f"{level_emoji} {alert['product_name']} - {alert['message']}", expanded=(idx < 3)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Ürün:** {alert['product_name']}")
                st.markdown(f"**SKU:** {alert['sku']}")
                st.markdown(f"**Segment:** {SEGMENT_EMOJI.get(alert['segment'], '❓')} {alert['segment']}")
                st.markdown(f"**Mesaj:** {alert['message']}")
                st.markdown(f"**👉 Aksiyon:** {alert['action']}")
            
            with col2:
                st.metric("Stok Günü", f"{alert['days_of_stock']:.1f}")
                st.metric("Günlük Satış", f"{alert['forecasted_sales']:.1f}")

def show_settings_page():
    """Ayarlar sayfası"""
    st.markdown("## ⚙️ Ayarlar")
    st.info("Bu sayfa yakında eklenecek...")

if __name__ == "__main__":
    main()
