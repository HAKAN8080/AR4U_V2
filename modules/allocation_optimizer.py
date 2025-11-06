"""
Allocation Optimizer - Sevkiyat Stratejisi Modülü
Transfer Lead Time ile Güncellenmiş Versiyon
"""
import pandas as pd
from utils.constants import DEFAULT_SEGMENT_PARAMS, TRANSFER_LEAD_TIME_DAYS

class AllocationOptimizer:
    """Sevkiyat ve transfer optimizasyonu"""
    
    def __init__(self, df, segment_params=None, transfer_lead_time=TRANSFER_LEAD_TIME_DAYS):
        """
        Args:
            df: Analytics engine'den gelen dataframe (segmentlenmiş)
            segment_params: Segment parametreleri
            transfer_lead_time: Transfer süresi (gün) - default 5
        """
        self.df = df.copy()
        self.segment_params = segment_params or DEFAULT_SEGMENT_PARAMS
        self.transfer_lead_time = transfer_lead_time
        self.allocation_plan = None
    
    def generate_allocation_strategy(self):
        """Her ürün için sevkiyat stratejisi oluştur"""
        
        allocation_list = []
        
        for idx, row in self.df.iterrows():
            segment = row.get('segment', 'UNCLASSIFIED')
            params = self.segment_params.get(segment, self.segment_params['STEADY'])
            
            # Günlük satış tahmini (trend ile)
            forecasted_daily_sales = row['daily_sales_avg_7d'] * row.get('trend_score', 1.0)
            
            # İhtiyaç hesaplamaları
            safety_stock_needed = forecasted_daily_sales * params['safety_stock_days']
            reorder_point = forecasted_daily_sales * params['reorder_days']
            
            # Mevcut stok
            current_total = row['total_stock']
            
            # Optimal Akyazı stoğu
            optimal_akyazi = current_total * params['allocation_pct']
            
            # 🚛 LEAD TIME HESABI
            # Transfer sırasında tüketilecek stok (5 gün * günlük satış)
            stock_consumed_during_transfer = forecasted_daily_sales * self.transfer_lead_time
            
            # Transfer ihtiyacı (lead time dahil)
            # Transfer bittiğinde Akyazı'da olması gereken = optimal + lead time tüketimi
            target_akyazi_after_transfer = optimal_akyazi
            transfer_from_ana_depo = max(0, 
                target_akyazi_after_transfer + stock_consumed_during_transfer - row['stock_akyazi']
            )
            
            # Ana depoda yeterli stok var mı kontrol et
            if transfer_from_ana_depo > row['stock_ana_depo']:
                transfer_from_ana_depo = row['stock_ana_depo']  # Maksimum ne varsa
            
            transfer_from_oms = 0  # Şimdilik manuel
            
            # Kritik durum
            is_critical = current_total < reorder_point
            
            # Lead time riskini değerlendir
            # Eğer mevcut Akyazı stoğu lead time boyunca yeterli değilse -> URGENT
            days_until_stockout_akyazi = row['stock_akyazi'] / (forecasted_daily_sales + 0.1)
            is_urgent_transfer = days_until_stockout_akyazi < self.transfer_lead_time
            
            # Sevkiyat önceliği
            if row['stock_akyazi'] > forecasted_daily_sales:
                primary_depot = 'akyazi'
            elif row['stock_ana_depo'] > 0:
                primary_depot = 'ana_depo'
            else:
                primary_depot = 'oms'
            
            # Markdown önerisi
            if segment == 'DYING':
                markdown_rec = 'URGENT'
            elif row['days_of_stock'] > params['markdown_day']:
                markdown_rec = 'CONSIDER'
            else:
                markdown_rec = 'NO'
            
            allocation_list.append({
                'sku': row['sku'],
                'product_name': row['product_name'],
                'category': row['category'],
                'segment': segment,
                'current_stock': current_total,
                'stock_akyazi': row['stock_akyazi'],
                'stock_ana_depo': row['stock_ana_depo'],
                'stock_oms': row['stock_oms_total'],
                'forecasted_daily_sales': round(forecasted_daily_sales, 2),
                'days_of_stock': round(row['days_of_stock'], 1),
                'days_until_stockout_akyazi': round(days_until_stockout_akyazi, 1),
                'safety_stock_needed': round(safety_stock_needed, 0),
                'reorder_point': round(reorder_point, 0),
                'is_critical': is_critical,
                'is_urgent_transfer': is_urgent_transfer,
                'primary_depot': primary_depot,
                'depot_priority': ', '.join(params['depot_priority']),
                'transfer_from_ana_depo': round(transfer_from_ana_depo, 0),
                'stock_consumed_during_transfer': round(stock_consumed_during_transfer, 1),
                'transfer_from_oms': transfer_from_oms,
                'auto_transfer': params['auto_transfer'],
                'markdown_recommendation': markdown_rec,
                'optimal_akyazi_stock': round(optimal_akyazi, 0)
            })
        
        self.allocation_plan = pd.DataFrame(allocation_list)
        return self.allocation_plan
    
    def get_transfer_recommendations(self, min_transfer=10, priority='urgent'):
        """
        Transfer önerileri listesi
        
        Args:
            min_transfer: Minimum transfer miktarı
            priority: 'urgent' (acil), 'auto' (otomatik), 'all' (hepsi)
        """
        
        if self.allocation_plan is None:
            self.generate_allocation_strategy()
        
        # Filtreler
        if priority == 'urgent':
            transfers = self.allocation_plan[
                (self.allocation_plan['is_urgent_transfer'] == True) &
                (self.allocation_plan['transfer_from_ana_depo'] >= min_transfer)
            ].copy()
        elif priority == 'auto':
            transfers = self.allocation_plan[
                (self.allocation_plan['auto_transfer'] == True) &
                (self.allocation_plan['transfer_from_ana_depo'] >= min_transfer)
            ].copy()
        else:  # all
            transfers = self.allocation_plan[
                self.allocation_plan['transfer_from_ana_depo'] >= min_transfer
            ].copy()
        
        # Öncelik skoruna göre sırala
        # Urgency + segment priority + days until stockout
        transfers = transfers.sort_values(
            ['is_urgent_transfer', 'days_until_stockout_akyazi'], 
            ascending=[False, True]
        )
        
        return transfers[[
            'sku', 'product_name', 'segment', 'primary_depot',
            'transfer_from_ana_depo', 'days_until_stockout_akyazi', 
            'stock_consumed_during_transfer', 'forecasted_daily_sales',
            'is_urgent_transfer'
        ]]
    
    def get_reorder_recommendations(self):
        """Sipariş önerileri"""
        
        if self.allocation_plan is None:
            self.generate_allocation_strategy()
        
        reorders = self.allocation_plan[
            self.allocation_plan['is_critical'] == True
        ].copy()
        
        reorders = reorders.sort_values('days_of_stock')
        
        # Sipariş miktarı önerisi
        reorders['suggested_order_qty'] = (
            reorders['safety_stock_needed'] - reorders['current_stock']
        ).clip(lower=0)
        
        return reorders[[
            'sku', 'product_name', 'segment', 'current_stock',
            'reorder_point', 'days_of_stock', 'suggested_order_qty'
        ]]
    
    def get_markdown_candidates(self):
        """Markdown adayları"""
        
        if self.allocation_plan is None:
            self.generate_allocation_strategy()
        
        markdown = self.allocation_plan[
            self.allocation_plan['markdown_recommendation'].isin(['URGENT', 'CONSIDER'])
        ].copy()
        
        markdown = markdown.sort_values('days_of_stock', ascending=False)
        
        # Potansiyel kayıp hesapla
        markdown['potential_loss'] = self.df.set_index('sku').loc[
            markdown['sku'].values, 'price'
        ].values * markdown['current_stock'] * 0.3  # %30 indirim varsayımı
        
        return markdown[[
            'sku', 'product_name', 'segment', 'current_stock',
            'days_of_stock', 'markdown_recommendation', 'potential_loss'
        ]]
    
    def simulate_transfer(self, sku, from_depot, to_depot, quantity):
        """Transfer simülasyonu yap"""
        
        product = self.df[self.df['sku'] == sku].iloc[0]
        
        # Mevcut durum
        current_from = product[f'stock_{from_depot}']
        current_to = product[f'stock_{to_depot}']
        
        # Transfer sonrası
        new_from = max(0, current_from - quantity)
        new_to = current_to + quantity
        
        # Yeni days_of_stock hesapla
        forecasted_daily = product['daily_sales_avg_7d'] * product.get('trend_score', 1.0)
        new_total_stock = new_from + new_to + product['stock_oms_total']
        new_days = new_total_stock / (forecasted_daily + 0.1)
        
        # Lead time riskini hesapla
        if to_depot == 'akyazi':
            # Transfer bitene kadar Akyazı'da tüketilecek stok
            stock_at_transfer_completion = current_to - (forecasted_daily * self.transfer_lead_time)
            will_stockout_during_transfer = stock_at_transfer_completion < 0
        else:
            will_stockout_during_transfer = False
        
        return {
            'sku': sku,
            'product_name': product['product_name'],
            'from_depot': from_depot,
            'to_depot': to_depot,
            'quantity': quantity,
            'current_from': current_from,
            'new_from': new_from,
            'current_to': current_to,
            'new_to': new_to,
            'current_days_of_stock': product['days_of_stock'],
            'new_days_of_stock': round(new_days, 1),
            'transfer_lead_time': self.transfer_lead_time,
            'will_stockout_during_transfer': will_stockout_during_transfer,
            'daily_sales_forecast': round(forecasted_daily, 2)
        }
    
    def optimize_depot_allocation(self):
        """
        Tüm depolar için optimal dağılımı hesapla
        Returns: Reallocation planı
        """
        
        if self.allocation_plan is None:
            self.generate_allocation_strategy()
        
        # Segment bazlı optimal dağılım
        reallocation = []
        
        for segment in ['HOT', 'RISING_STAR', 'STEADY']:
            segment_products = self.allocation_plan[
                self.allocation_plan['segment'] == segment
            ]
            
            for idx, product in segment_products.iterrows():
                current_akyazi_pct = product['stock_akyazi'] / (product['current_stock'] + 1)
                optimal_pct = self.segment_params[segment]['allocation_pct']
                
                # %10'dan fazla sapma varsa reallocation öner
                if abs(current_akyazi_pct - optimal_pct) > 0.10:
                    reallocation.append({
                        'sku': product['sku'],
                        'product_name': product['product_name'],
                        'segment': segment,
                        'current_akyazi_pct': round(current_akyazi_pct * 100, 1),
                        'optimal_akyazi_pct': round(optimal_pct * 100, 1),
                        'action_needed': 'Transfer to Akyazı' if current_akyazi_pct < optimal_pct else 'Reduce Akyazı',
                        'suggested_transfer': product['transfer_from_ana_depo']
                    })
        
        return pd.DataFrame(reallocation)
    
    def get_transfer_summary_stats(self):
        """Transfer özet istatistikleri"""
        
        if self.allocation_plan is None:
            self.generate_allocation_strategy()
        
        urgent_count = len(self.allocation_plan[self.allocation_plan['is_urgent_transfer'] == True])
        auto_count = len(self.allocation_plan[
            (self.allocation_plan['auto_transfer'] == True) & 
            (self.allocation_plan['transfer_from_ana_depo'] > 0)
        ])
        total_transfer_volume = self.allocation_plan['transfer_from_ana_depo'].sum()
        
        return {
            'urgent_transfers': urgent_count,
            'auto_transfers': auto_count,
            'total_transfer_volume': round(total_transfer_volume, 0),
            'avg_transfer_size': round(total_transfer_volume / max(auto_count, 1), 0),
            'lead_time_days': self.transfer_lead_time
        }
