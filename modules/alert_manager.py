"""
Alert Manager - Kritik Uyarı Sistemi
"""
import pandas as pd
from datetime import datetime

class AlertManager:
    """Kritik durum uyarıları ve yönetimi"""
    
    def __init__(self, df, allocation_df):
        """
        Args:
            df: Analytics dataframe
            allocation_df: Allocation strategy dataframe
        """
        self.df = df
        self.allocation_df = allocation_df
        self.alerts = []
    
    def generate_all_alerts(self):
        """Tüm uyarıları oluştur"""
        
        self.alerts = []
        
        # 1. Kritik stok uyarıları
        self._generate_critical_stock_alerts()
        
        # 2. Trend uyarıları
        self._generate_trend_alerts()
        
        # 3. Markdown uyarıları
        self._generate_markdown_alerts()
        
        # 4. Stoksuzluk uyarıları
        self._generate_stockout_alerts()
        
        # 5. Transfer uyarıları
        self._generate_transfer_alerts()
        
        # DataFrame'e çevir ve önceliklendir
        if self.alerts:
            alerts_df = pd.DataFrame(self.alerts)
            alerts_df = self._prioritize_alerts(alerts_df)
            return alerts_df
        else:
            return pd.DataFrame(columns=[
                'level', 'priority', 'category', 'sku', 'product_name',
                'message', 'action', 'created_at'
            ])
    
    def _generate_critical_stock_alerts(self):
        """🔴 Kritik stok seviyesi uyarıları"""
        
        critical_products = self.allocation_df[
            (self.allocation_df['days_of_stock'] < 3) &
            (self.allocation_df['segment'].isin(['HOT', 'RISING_STAR']))
        ]
        
        for idx, product in critical_products.iterrows():
            self.alerts.append({
                'level': 'CRITICAL',
                'category': 'STOCK',
                'sku': product['sku'],
                'product_name': product['product_name'],
                'segment': product['segment'],
                'message': f"Kritik stok! Sadece {product['days_of_stock']:.1f} günlük stok kaldı. Günlük satış: {product['forecasted_daily_sales']:.0f}",
                'action': f"ACİL: Ana depodan {product['transfer_from_ana_depo']:.0f} adet transfer başlat",
                'created_at': datetime.now(),
                'days_of_stock': product['days_of_stock'],
                'forecasted_sales': product['forecasted_daily_sales']
            })
    
    def _generate_trend_alerts(self):
        """🟡 Yüksek trend uyarıları"""
        
        trending = self.allocation_df[
            (self.allocation_df['days_of_stock'] < 7) &
            (self.allocation_df['segment'] == 'HOT')
        ]
        
        for idx, product in trending.iterrows():
            # Eğer zaten critical alert varsa skip et
            if product['days_of_stock'] < 3:
                continue
                
            self.alerts.append({
                'level': 'WARNING',
                'category': 'TREND',
                'sku': product['sku'],
                'product_name': product['product_name'],
                'segment': product['segment'],
                'message': f"HOT ürün, {product['days_of_stock']:.1f} günlük stok var",
                'action': f"Transfer hazırla: {product['transfer_from_ana_depo']:.0f} adet",
                'created_at': datetime.now(),
                'days_of_stock': product['days_of_stock'],
                'forecasted_sales': product['forecasted_daily_sales']
            })
    
    def _generate_markdown_alerts(self):
        """🔵 Markdown önerileri"""
        
        markdown_urgent = self.allocation_df[
            self.allocation_df['markdown_recommendation'] == 'URGENT'
        ]
        
        for idx, product in markdown_urgent.iterrows():
            # Price bilgisini df'den al
            price = self.df[self.df['sku'] == product['sku']]['price'].iloc[0]
            potential_loss = price * product['current_stock'] * 0.3
            
            self.alerts.append({
                'level': 'INFO',
                'category': 'MARKDOWN',
                'sku': product['sku'],
                'product_name': product['product_name'],
                'segment': product['segment'],
                'message': f"Ürün ölüyor. {product['days_of_stock']:.0f} günlük stok fazlası var",
                'action': f"MARKDOWN başlat: %30-50 indirim öner (Potansiyel kayıp: ₺{potential_loss:,.0f})",
                'created_at': datetime.now(),
                'days_of_stock': product['days_of_stock'],
                'forecasted_sales': product['forecasted_daily_sales']
            })
    
    def _generate_stockout_alerts(self):
        """🔴 Geçmiş stoksuzluk uyarıları"""
        
        frequent_stockouts = self.df[
            (self.df['stock_out_days_last_30d'] > 5) &
            (self.df['segment'].isin(['HOT', 'RISING_STAR', 'STEADY']))
        ]
        
        for idx, product in frequent_stockouts.iterrows():
            self.alerts.append({
                'level': 'WARNING',
                'category': 'STOCKOUT_HISTORY',
                'sku': product['sku'],
                'product_name': product['product_name'],
                'segment': product['segment'],
                'message': f"Son 30 günde {product['stock_out_days_last_30d']} gün stoksuzluk yaşandı",
                'action': "Safety stock seviyesini yükselt, tedarikçi lead time'ı gözden geçir",
                'created_at': datetime.now(),
                'days_of_stock': product['days_of_stock'],
                'forecasted_sales': product['daily_sales_avg_7d']
            })
    
    def _generate_transfer_alerts(self):
        """🟡 Büyük transfer ihtiyacı uyarıları"""
        
        large_transfers = self.allocation_df[
            (self.allocation_df['transfer_from_ana_depo'] > 100) &
            (self.allocation_df['auto_transfer'] == True)
        ]
        
        for idx, product in large_transfers.iterrows():
            self.alerts.append({
                'level': 'WARNING',
                'category': 'TRANSFER',
                'sku': product['sku'],
                'product_name': product['product_name'],
                'segment': product['segment'],
                'message': f"Büyük transfer ihtiyacı: {product['transfer_from_ana_depo']:.0f} adet",
                'action': f"Transfer planla (Ana Depo → Akyazı). Mevcut Akyazı: {product['stock_akyazi']:.0f}",
                'created_at': datetime.now(),
                'days_of_stock': product['days_of_stock'],
                'forecasted_sales': product['forecasted_daily_sales']
            })
    
    def _prioritize_alerts(self, alerts_df):
        """Uyarıları önceliklendir"""
        
        # Priority score hesapla
        priority_map = {
            'CRITICAL': 100,
            'WARNING': 50,
            'INFO': 10
        }
        
        alerts_df['priority_base'] = alerts_df['level'].map(priority_map)
        
        # Days of stock'a göre ek öncelik
        alerts_df['priority'] = alerts_df['priority_base'] + (
            10 - alerts_df['days_of_stock'].clip(0, 10)
        )
        
        # Sırala: Önce priority, sonra days_of_stock
        alerts_df = alerts_df.sort_values(['priority', 'days_of_stock'], ascending=[False, True])
        
        return alerts_df
    
    def filter_alerts(self, level=None, category=None, segment=None):
        """Uyarıları filtrele"""
        
        if not hasattr(self, 'alerts_df') or self.alerts_df is None:
            return None
        
        filtered = self.alerts_df.copy()
        
        if level:
            if isinstance(level, list):
                filtered = filtered[filtered['level'].isin(level)]
            else:
                filtered = filtered[filtered['level'] == level]
        
        if category:
            if isinstance(category, list):
                filtered = filtered[filtered['category'].isin(category)]
            else:
                filtered = filtered[filtered['category'] == category]
        
        if segment:
            if isinstance(segment, list):
                filtered = filtered[filtered['segment'].isin(segment)]
            else:
                filtered = filtered[filtered['segment'] == segment]
        
        return filtered
    
    def get_alert_summary(self):
        """Uyarı özeti"""
        
        if not self.alerts:
            alerts_df = self.generate_all_alerts()
        else:
            alerts_df = pd.DataFrame(self.alerts)
        
        if len(alerts_df) == 0:
            return {
                'total': 0,
                'critical': 0,
                'warning': 0,
                'info': 0,
                'by_category': {}
            }
        
        summary = {
            'total': len(alerts_df),
            'critical': len(alerts_df[alerts_df['level'] == 'CRITICAL']),
            'warning': len(alerts_df[alerts_df['level'] == 'WARNING']),
            'info': len(alerts_df[alerts_df['level'] == 'INFO']),
            'by_category': alerts_df['category'].value_counts().to_dict()
        }
        
        return summary
    
    def export_alerts_report(self):
        """Alert raporunu export et"""
        
        if not self.alerts:
            alerts_df = self.generate_all_alerts()
        else:
            alerts_df = pd.DataFrame(self.alerts)
        
        return alerts_df[[
            'level', 'category', 'sku', 'product_name', 'segment',
            'message', 'action', 'created_at'
        ]]
