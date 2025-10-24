"""
Analytics Engine - Segmentasyon ve Metrik Hesaplama
"""
import pandas as pd
import numpy as np
from utils.constants import DEFAULT_SEGMENT_PARAMS, METRIC_WEIGHTS
from utils.helpers import safe_divide

class AnalyticsEngine:
    """Ürün analizi ve segmentasyon motoru"""
    
    def __init__(self, df, segment_params=None):
        """
        Args:
            df: Ürün dataframe
            segment_params: Özel segment parametreleri (opsiyonel)
        """
        self.df = df.copy()
        self.segment_params = segment_params or DEFAULT_SEGMENT_PARAMS
        self.segments = {}
    
    def calculate_all_metrics(self):
        """Tüm metrikleri hesapla"""
        
        # 1. Velocity Score (Satış hız değişimi)
        self.df['velocity_score'] = safe_divide(
            self.df['daily_sales_avg_7d'],
            self.df['daily_sales_avg_30d'],
            default=1.0
        )
        
        # 2. Trend Score (Günlük momentum)
        self.df['trend_score'] = safe_divide(
            self.df['daily_sales_yesterday'],
            self.df['daily_sales_avg_7d'],
            default=1.0
        )
        
        # 3. Engagement Score (İlgi/Görüntülenme oranı)
        self.df['engagement_score'] = safe_divide(
            self.df['add_to_cart_7d'],
            self.df['view_count_7d'],
            default=0
        ) * 100
        
        # 4. Conversion Rate (Satış/Sepet oranı)
        self.df['conversion_rate'] = safe_divide(
            self.df['daily_sales_avg_7d'] * 7,
            self.df['add_to_cart_7d'],
            default=0
        ) * 100
        
        # 5. Stock Health (Stok kaç güne yeter?)
        self.df['days_of_stock'] = safe_divide(
            self.df['total_stock'],
            self.df['daily_sales_avg_7d'],
            default=999
        )
        
        # 6. Quality Score (Ürün kalitesi - rating + review count)
        self.df['quality_score'] = (
            self.df['avg_rating'] * 20 +  # 0-100 skala
            np.minimum(self.df['review_count'] / 10, 10)  # Max 10 puan
        ) / 2
        
        # 7. Stockout Penalty (Stoksuzluk cezası)
        self.df['stockout_penalty'] = 100 - (self.df['stock_out_days_last_30d'] * 3)
        self.df['stockout_penalty'] = self.df['stockout_penalty'].clip(lower=0)
        
        # 8. Campaign Boost
        self.df['campaign_boost'] = self.df['campaign_flag'] * 1.3 + (1 - self.df['campaign_flag']) * 1.0
        
        # 9. Final Score (Ağırlıklı toplam)
        self.df['final_score'] = (
            self.df['velocity_score'] * METRIC_WEIGHTS['velocity_score'] +
            self.df['trend_score'] * METRIC_WEIGHTS['trend_score'] +
            self.df['engagement_score'] * METRIC_WEIGHTS['engagement_score'] +
            self.df['conversion_rate'] * METRIC_WEIGHTS['conversion_rate'] +
            self.df['quality_score'] * METRIC_WEIGHTS['quality_score'] +
            self.df['stockout_penalty'] * METRIC_WEIGHTS['stockout_penalty']
        ) * self.df['campaign_boost']
        
        return self.df
    
    def segment_products(self):
        """Ürünleri segmentlere ayır"""
        
        # Önce metrikleri hesapla
        if 'velocity_score' not in self.df.columns:
            self.calculate_all_metrics()
        
        # Default segment
        self.df['segment'] = 'UNCLASSIFIED'
        
        # HOT segment
        hot_params = self.segment_params['HOT']
        hot_mask = (
            (self.df['velocity_score'] > hot_params.get('velocity_min', 1.5)) &
            (self.df['trend_score'] > hot_params.get('trend_min', 1.3)) &
            (self.df['daily_sales_avg_7d'] > hot_params.get('daily_sales_min', 15))
        )
        self.df.loc[hot_mask, 'segment'] = 'HOT'
        
        # RISING_STAR segment
        rising_params = self.segment_params['RISING_STAR']
        rising_mask = (
            (self.df['velocity_score'] > rising_params.get('velocity_min', 1.2)) &
            (self.df['velocity_score'] <= rising_params.get('velocity_max', 1.5)) &
            (self.df['trend_score'] > rising_params.get('trend_min', 1.2)) &
            (self.df['engagement_score'] > rising_params.get('engagement_min', 5))
        )
        self.df.loc[rising_mask & (self.df['segment'] == 'UNCLASSIFIED'), 'segment'] = 'RISING_STAR'
        
        # STEADY segment
        steady_params = self.segment_params['STEADY']
        steady_mask = (
            (self.df['velocity_score'] >= steady_params.get('velocity_min', 0.8)) &
            (self.df['velocity_score'] <= steady_params.get('velocity_max', 1.2)) &
            (self.df['daily_sales_avg_30d'] > steady_params.get('daily_sales_min', 5)) &
            (self.df['stock_out_days_last_30d'] < steady_params.get('stockout_max', 3))
        )
        self.df.loc[steady_mask & (self.df['segment'] == 'UNCLASSIFIED'), 'segment'] = 'STEADY'
        
        # SLOW segment
        slow_params = self.segment_params['SLOW']
        slow_mask = (
            (self.df['daily_sales_avg_7d'] < slow_params.get('daily_sales_max', 5)) &
            (self.df['daily_sales_avg_7d'] > 0) &
            (self.df['velocity_score'] >= slow_params.get('velocity_min', 0.5))
        )
        self.df.loc[slow_mask & (self.df['segment'] == 'UNCLASSIFIED'), 'segment'] = 'SLOW'
        
        # DYING segment
        dying_params = self.segment_params['DYING']
        dying_mask = (
            (self.df['velocity_score'] < dying_params.get('velocity_max', 0.5)) |
            (self.df['days_of_stock'] > dying_params.get('stock_days_min', 60))
        )
        self.df.loc[dying_mask & (self.df['segment'] == 'UNCLASSIFIED'), 'segment'] = 'DYING'
        
        # Segmentleri dictionary'e kaydet
        for segment_name in ['HOT', 'RISING_STAR', 'STEADY', 'SLOW', 'DYING', 'UNCLASSIFIED']:
            self.segments[segment_name] = self.df[self.df['segment'] == segment_name].copy()
        
        return self.df
    
    def get_segment_summary(self):
        """Segment bazlı özet istatistikler"""
        
        if 'segment' not in self.df.columns:
            self.segment_products()
        
        summary = []
        
        for segment_name, segment_df in self.segments.items():
            if len(segment_df) > 0:
                summary.append({
                    'segment': segment_name,
                    'count': len(segment_df),
                    'total_stock': segment_df['total_stock'].sum(),
                    'stock_value': (segment_df['total_stock'] * segment_df['price']).sum(),
                    'avg_velocity': segment_df['velocity_score'].mean(),
                    'avg_trend': segment_df['trend_score'].mean(),
                    'total_daily_sales': segment_df['daily_sales_avg_7d'].sum(),
                    'avg_days_of_stock': segment_df['days_of_stock'].mean(),
                    'avg_final_score': segment_df['final_score'].mean()
                })
        
        return pd.DataFrame(summary)
    
    def get_category_performance(self):
        """Kategori bazlı performans analizi"""
        
        if 'segment' not in self.df.columns:
            self.segment_products()
        
        category_perf = self.df.groupby('category').agg({
            'sku': 'count',
            'total_stock': 'sum',
            'daily_sales_avg_7d': 'sum',
            'price': 'mean',
            'velocity_score': 'mean',
            'final_score': 'mean',
            'days_of_stock': 'mean'
        }).reset_index()
        
        category_perf.columns = [
            'category', 'product_count', 'total_stock', 'daily_sales',
            'avg_price', 'avg_velocity', 'avg_score', 'avg_stock_days'
        ]
        
        # Stok değeri hesapla
        category_value = self.df.groupby('category').apply(
            lambda x: (x['total_stock'] * x['price']).sum()
        ).reset_index()
        category_value.columns = ['category', 'stock_value']
        
        category_perf = category_perf.merge(category_value, on='category')
        
        return category_perf
    
    def get_top_performers(self, n=10, metric='final_score'):
        """En iyi performans gösteren ürünler"""
        
        if metric not in self.df.columns:
            if metric == 'final_score' and 'velocity_score' not in self.df.columns:
                self.calculate_all_metrics()
        
        return self.df.nlargest(n, metric)[[
            'sku', 'product_name', 'category', 'segment', metric,
            'daily_sales_avg_7d', 'total_stock', 'days_of_stock'
        ]]
    
    def get_bottom_performers(self, n=10, metric='final_score'):
        """En düşük performans gösteren ürünler"""
        
        if metric not in self.df.columns:
            if metric == 'final_score' and 'velocity_score' not in self.df.columns:
                self.calculate_all_metrics()
        
        return self.df.nsmallest(n, metric)[[
            'sku', 'product_name', 'category', 'segment', metric,
            'daily_sales_avg_7d', 'total_stock', 'days_of_stock'
        ]]
    
    def get_critical_stock_products(self, threshold_days=7):
        """Kritik stok seviyesindeki ürünler"""
        
        if 'days_of_stock' not in self.df.columns:
            self.calculate_all_metrics()
        
        critical = self.df[
            (self.df['days_of_stock'] < threshold_days) &
            (self.df['segment'].isin(['HOT', 'RISING_STAR']))
        ].copy()
        
        critical = critical.sort_values('days_of_stock')
        
        return critical[[
            'sku', 'product_name', 'segment', 'days_of_stock',
            'daily_sales_avg_7d', 'total_stock', 'stock_akyazi',
            'stock_ana_depo', 'stock_oms_total'
        ]]
    
    def get_overstocked_products(self, threshold_days=60):
        """Fazla stoklu ürünler"""
        
        if 'days_of_stock' not in self.df.columns:
            self.calculate_all_metrics()
        
        overstocked = self.df[self.df['days_of_stock'] > threshold_days].copy()
        overstocked = overstocked.sort_values('days_of_stock', ascending=False)
        
        return overstocked[[
            'sku', 'product_name', 'segment', 'days_of_stock',
            'daily_sales_avg_7d', 'total_stock', 'price'
        ]]
