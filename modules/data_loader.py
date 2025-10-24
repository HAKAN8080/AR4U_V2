"""
Veri Yükleme ve Validasyon Modülü
"""
import pandas as pd
import streamlit as st
from utils.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from utils.helpers import show_error, show_success, show_warning

class DataLoader:
    """CSV verisi yükleme ve validasyon sınıfı"""
    
    def __init__(self):
        self.df = None
        self.validation_errors = []
        self.validation_warnings = []
    
    def load_from_file(self, uploaded_file):
        """
        Yüklenen dosyadan veri oku
        
        Args:
            uploaded_file: Streamlit file uploader object
            
        Returns:
            pd.DataFrame veya None
        """
        try:
            self.df = pd.read_csv(uploaded_file)
            show_success(f"✅ Dosya yüklendi: {len(self.df)} ürün")
            
            # Validasyon yap
            if self.validate_data():
                return self.preprocess_data()
            else:
                return None
                
        except Exception as e:
            show_error(f"Dosya yükleme hatası: {str(e)}")
            return None
    
    def load_sample_data(self):
        """Örnek veriyi yükle"""
        try:
            self.df = pd.read_csv('data/sample_data.csv')
            show_success(f"✅ Örnek veri yüklendi: {len(self.df)} ürün")
            
            if self.validate_data():
                return self.preprocess_data()
            else:
                return None
                
        except Exception as e:
            show_error(f"Örnek veri yükleme hatası: {str(e)}")
            return None
    
    def validate_data(self):
        """
        Veri validasyonu yap
        
        Returns:
            bool: Validasyon başarılı mı?
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        if self.df is None or len(self.df) == 0:
            self.validation_errors.append("Veri boş!")
            return False
        
        # Zorunlu kolonları kontrol et
        missing_columns = []
        for col in REQUIRED_COLUMNS:
            if col not in self.df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            self.validation_errors.append(
                f"Zorunlu kolonlar eksik: {', '.join(missing_columns)}"
            )
            return False
        
        # Opsiyonel kolonları kontrol et ve ekle
        for col, default_value in OPTIONAL_COLUMNS.items():
            if col not in self.df.columns:
                self.df[col] = default_value
                self.validation_warnings.append(
                    f"'{col}' kolonu bulunamadı, varsayılan değer ({default_value}) kullanılıyor"
                )
        
        # Veri tipleri kontrolü
        numeric_columns = [
            'price', 'stock_akyazi', 'stock_ana_depo', 'stock_oms_total',
            'daily_sales_avg_30d', 'daily_sales_avg_7d', 'daily_sales_yesterday'
        ]
        
        for col in numeric_columns:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    
                    # Negatif değer kontrolü
                    if (self.df[col] < 0).any():
                        self.validation_warnings.append(
                            f"'{col}' kolonunda negatif değerler var, 0 yapılıyor"
                        )
                        self.df[col] = self.df[col].clip(lower=0)
                        
                except Exception as e:
                    self.validation_errors.append(
                        f"'{col}' kolonu sayısal değere çevrilemedi: {str(e)}"
                    )
                    return False
        
        # Boş değer kontrolü
        critical_nulls = self.df[REQUIRED_COLUMNS].isnull().sum()
        if critical_nulls.any():
            null_cols = critical_nulls[critical_nulls > 0]
            self.validation_warnings.append(
                f"Zorunlu kolonlarda boş değerler var: {dict(null_cols)}"
            )
        
        # Validasyon sonuçlarını göster
        if self.validation_warnings:
            for warning in self.validation_warnings:
                show_warning(warning)
        
        if self.validation_errors:
            for error in self.validation_errors:
                show_error(error)
            return False
        
        return True
    
    def preprocess_data(self):
        """
        Veriyi işle ve temizle
        
        Returns:
            pd.DataFrame
        """
        if self.df is None:
            return None
        
        # Boş değerleri doldur
        self.df = self.df.fillna({
            'margin_pct': 40,
            'view_count_7d': 0,
            'add_to_cart_7d': 0,
            'favorites_7d': 0,
            'review_count': 0,
            'avg_rating': 4.0,
            'stock_out_days_last_30d': 0,
            'campaign_flag': 0
        })
        
        # Toplam stok hesapla
        self.df['total_stock'] = (
            self.df['stock_akyazi'] + 
            self.df['stock_ana_depo'] + 
            self.df['stock_oms_total']
        )
        
        # Tip kolonu kontrolü (1 veya 2 olmalı)
        if 'tip' in self.df.columns:
            self.df['tip'] = self.df['tip'].apply(lambda x: 2 if x not in [1, 2] else x)
        
        # SKU'ları string yap
        self.df['sku'] = self.df['sku'].astype(str)
        
        # Tarih kolonlarını dönüştür
        if 'last_restock_date' in self.df.columns:
            self.df['last_restock_date'] = pd.to_datetime(
                self.df['last_restock_date'], 
                errors='coerce'
            )
        
        return self.df
    
    def get_data_summary(self):
        """
        Veri özeti döndür
        
        Returns:
            dict: Veri istatistikleri
        """
        if self.df is None:
            return None
        
        summary = {
            'total_products': len(self.df),
            'total_stock_value': (self.df['total_stock'] * self.df['price']).sum(),
            'avg_price': self.df['price'].mean(),
            'total_categories': self.df['category'].nunique(),
            'categories': self.df['category'].unique().tolist(),
            'tip_distribution': self.df['tip'].value_counts().to_dict(),
            'avg_daily_sales': self.df['daily_sales_avg_7d'].sum(),
            'total_akyazi_stock': self.df['stock_akyazi'].sum(),
            'total_ana_depo_stock': self.df['stock_ana_depo'].sum(),
            'total_oms_stock': self.df['stock_oms_total'].sum(),
        }
        
        return summary
    
    def filter_data(self, **filters):
        """
        Veriyi filtrele
        
        Args:
            **filters: Filtre parametreleri
            
        Returns:
            pd.DataFrame: Filtrelenmiş veri
        """
        if self.df is None:
            return None
        
        filtered_df = self.df.copy()
        
        # Kategori filtresi
        if 'category' in filters and filters['category']:
            if isinstance(filters['category'], list):
                filtered_df = filtered_df[filtered_df['category'].isin(filters['category'])]
            else:
                filtered_df = filtered_df[filtered_df['category'] == filters['category']]
        
        # Segment filtresi
        if 'segment' in filters and filters['segment'] and 'segment' in filtered_df.columns:
            if isinstance(filters['segment'], list):
                filtered_df = filtered_df[filtered_df['segment'].isin(filters['segment'])]
            else:
                filtered_df = filtered_df[filtered_df['segment'] == filters['segment']]
        
        # Tip filtresi
        if 'tip' in filters and filters['tip']:
            filtered_df = filtered_df[filtered_df['tip'] == filters['tip']]
        
        # SKU araması
        if 'sku_search' in filters and filters['sku_search']:
            search_term = filters['sku_search'].lower()
            filtered_df = filtered_df[
                filtered_df['sku'].str.lower().str.contains(search_term) |
                filtered_df['product_name'].str.lower().str.contains(search_term)
            ]
        
        # Satış aralığı
        if 'sales_min' in filters and filters['sales_min'] is not None:
            filtered_df = filtered_df[filtered_df['daily_sales_avg_7d'] >= filters['sales_min']]
        
        if 'sales_max' in filters and filters['sales_max'] is not None:
            filtered_df = filtered_df[filtered_df['daily_sales_avg_7d'] <= filters['sales_max']]
        
        return filtered_df
