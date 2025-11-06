"""
Sabitler ve Konfigürasyonlar
"""

# Segment renkleri (Streamlit ve Plotly için)
SEGMENT_COLORS = {
    'HOT': '#FF4444',
    'RISING_STAR': '#FFD700',
    'STEADY': '#44FF44',
    'SLOW': '#FFA500',
    'DYING': '#666666',
    'UNCLASSIFIED': '#CCCCCC'
}

# Segment emoji'leri
SEGMENT_EMOJI = {
    'HOT': '🔥',
    'RISING_STAR': '⭐',
    'STEADY': '✅',
    'SLOW': '🐢',
    'DYING': '💀',
    'UNCLASSIFIED': '❓'
}

# Alert seviyeleri
ALERT_LEVELS = {
    'CRITICAL': '🔴',
    'WARNING': '🟡',
    'INFO': '🔵'
}

# Segment parametreleri (Default)
DEFAULT_SEGMENT_PARAMS = {
    'HOT': {
        'name': '🔥 HOT (Patlayanlar)',
        'reorder_days': 3,
        'safety_stock_days': 5,
        'depot_priority': ['akyazi', 'oms', 'ana_depo'],
        'auto_transfer': True,
        'transfer_threshold': 0.7,
        'allocation_pct': 0.80,
        'markdown_day': 999,
        'velocity_min': 1.5,
        'trend_min': 1.3,
        'daily_sales_min': 15
    },
    'RISING_STAR': {
        'name': '⭐ RISING STAR (Yükselen)',
        'reorder_days': 4,
        'safety_stock_days': 6,
        'depot_priority': ['akyazi', 'ana_depo', 'oms'],
        'auto_transfer': True,
        'transfer_threshold': 0.6,
        'allocation_pct': 0.70,
        'markdown_day': 999,
        'velocity_min': 1.2,
        'velocity_max': 1.5,
        'trend_min': 1.2,
        'engagement_min': 5
    },
    'STEADY': {
        'name': '✅ STEADY (Düzenli)',
        'reorder_days': 7,
        'safety_stock_days': 10,
        'depot_priority': ['akyazi', 'ana_depo', 'oms'],
        'auto_transfer': False,
        'transfer_threshold': 0.5,
        'allocation_pct': 0.60,
        'markdown_day': 45,
        'velocity_min': 0.8,
        'velocity_max': 1.2,
        'daily_sales_min': 5,
        'stockout_max': 3
    },
    'SLOW': {
        'name': '🐢 SLOW (Yavaş)',
        'reorder_days': 14,
        'safety_stock_days': 20,
        'depot_priority': ['oms', 'ana_depo', 'akyazi'],
        'auto_transfer': False,
        'transfer_threshold': 0.3,
        'allocation_pct': 0.30,
        'markdown_day': 30,
        'daily_sales_max': 5,
        'velocity_min': 0.5
    },
    'DYING': {
        'name': '💀 DYING (Ölen)',
        'reorder_days': 999,
        'safety_stock_days': 0,
        'depot_priority': ['oms', 'akyazi', 'ana_depo'],
        'auto_transfer': False,
        'transfer_threshold': 0,
        'allocation_pct': 0,
        'markdown_day': 7,
        'velocity_max': 0.5,
        'stock_days_min': 60
    }
}

# Zorunlu CSV kolonları
REQUIRED_COLUMNS = [
    'sku',
    'product_name',
    'category',
    'tip',
    'price',
    'stock_akyazi',
    'stock_ana_depo',
    'stock_oms_total',
    'daily_sales_avg_30d',
    'daily_sales_avg_7d',
    'daily_sales_yesterday'
]

# Opsiyonel kolonlar (yoksa default değerler kullanılır)
OPTIONAL_COLUMNS = {
    'margin_pct': 40,
    'view_count_7d': 0,
    'add_to_cart_7d': 0,
    'favorites_7d': 0,
    'review_count': 0,
    'avg_rating': 4.0,
    'stock_out_days_last_30d': 0,
    'campaign_flag': 0
}

# Metrik ağırlıkları
METRIC_WEIGHTS = {
    'velocity_score': 30,
    'trend_score': 25,
    'engagement_score': 15,
    'conversion_rate': 10,
    'quality_score': 10,
    'stockout_penalty': 10
}

# KPI hedefleri
KPI_TARGETS = {
    'growth_target': 30,  # %30 büyüme hedefi
    'service_level_hot': 95,  # HOT ürünlerde %95 servis seviyesi
    'stock_turnover_days': 35,  # İdeal 35 günlük stok
    'markdown_max': 10,  # Maksimum %10 markdown
}

# Transfer bilgileri
TRANSFER_LEAD_TIME_DAYS = 5  # 🚛 Ana Depo → Akyazı transfer süresi (gün)

# Depo bilgileri
DEPOT_INFO = {
    'akyazi': {
        'name': 'Akyazı E-com Deposu',
        'type': 'e-commerce',
        'capacity': 10000,  # placeholder
        'emoji': '🏢',
        'lead_time_days': 0  # Zaten hazır
    },
    'ana_depo': {
        'name': 'Ana Depo',
        'type': 'main',
        'capacity': 50000,
        'emoji': '🏭',
        'lead_time_days': TRANSFER_LEAD_TIME_DAYS  # 5 gün transfer süresi
    },
    'oms': {
        'name': 'OMS Mağazalar',
        'type': 'stores',
        'capacity': 20000,
        'emoji': '🏪',
        'lead_time_days': 0  # Zaten mağazalarda
    }
}
