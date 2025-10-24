"""
Yardımcı Fonksiyonlar
"""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from utils.constants import SEGMENT_COLORS, SEGMENT_EMOJI, ALERT_LEVELS

def format_number(num, decimal=0):
    """Sayıyı formatla"""
    if pd.isna(num):
        return "N/A"
    if decimal == 0:
        return f"{int(num):,}".replace(',', '.')
    return f"{num:,.{decimal}f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_currency(amount):
    """Para birimi formatla"""
    return f"₺{format_number(amount, 2)}"

def format_percentage(value, decimal=1):
    """Yüzde formatla"""
    return f"%{format_number(value, decimal)}"

def get_segment_color(segment):
    """Segment rengini getir"""
    return SEGMENT_COLORS.get(segment, '#CCCCCC')

def get_segment_emoji(segment):
    """Segment emoji'sini getir"""
    return SEGMENT_EMOJI.get(segment, '❓')

def get_alert_emoji(level):
    """Alert emoji'sini getir"""
    return ALERT_LEVELS.get(level, '🔵')

def create_metric_card(title, value, delta=None, help_text=None):
    """Streamlit metric kartı oluştur"""
    col1, col2 = st.columns([3, 1])
    with col1:
        if delta:
            st.metric(label=title, value=value, delta=delta, help=help_text)
        else:
            st.metric(label=title, value=value, help=help_text)

def safe_divide(numerator, denominator, default=0):
    """Güvenli bölme işlemi"""
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return default
    return numerator / denominator

def calculate_days_between(date_str, reference_date=None):
    """İki tarih arasındaki gün farkını hesapla"""
    if reference_date is None:
        reference_date = datetime.now()
    
    try:
        date = pd.to_datetime(date_str)
        return (reference_date - date).days
    except:
        return None

def export_to_csv(df, filename):
    """DataFrame'i CSV olarak indir"""
    csv = df.to_csv(index=False).encode('utf-8-sig')
    return csv

def create_download_button(data, filename, label="📥 İndir"):
    """Download butonu oluştur"""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime='text/csv'
    )

def show_success(message):
    """Başarı mesajı göster"""
    st.success(f"✅ {message}")

def show_error(message):
    """Hata mesajı göster"""
    st.error(f"❌ {message}")

def show_warning(message):
    """Uyarı mesajı göster"""
    st.warning(f"⚠️ {message}")

def show_info(message):
    """Bilgi mesajı göster"""
    st.info(f"ℹ️ {message}")

def get_color_gradient(value, min_val, max_val, reverse=False):
    """Değere göre renk gradient'i döndür"""
    # Normalize değer (0-1 arası)
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)
    
    if reverse:
        normalized = 1 - normalized
    
    # Kırmızıdan yeşile gradient
    if normalized < 0.5:
        # Kırmızı -> Sarı
        r = 255
        g = int(255 * (normalized * 2))
        b = 0
    else:
        # Sarı -> Yeşil
        r = int(255 * (2 - normalized * 2))
        g = 255
        b = 0
    
    return f'rgb({r}, {g}, {b})'

def styled_dataframe(df, height=400):
    """Styled dataframe göster"""
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )

def create_expander_section(title, expanded=False):
    """Genişletilebilir section oluştur"""
    return st.expander(title, expanded=expanded)
