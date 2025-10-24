"""
Görselleştirme Modülü - Plotly Charts
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.constants import SEGMENT_COLORS, SEGMENT_EMOJI
from utils.helpers import format_number, format_currency

class Visualizations:
    """Interactive chart oluşturucu"""
    
    @staticmethod
    def segment_pie_chart(df):
        """Segment dağılımı pasta grafik"""
        segment_counts = df['segment'].value_counts()
        
        colors = [SEGMENT_COLORS.get(seg, '#CCCCCC') for seg in segment_counts.index]
        labels = [f"{SEGMENT_EMOJI.get(seg, '❓')} {seg}" for seg in segment_counts.index]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=segment_counts.values,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>Ürün Sayısı: %{value}<br>Oran: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Segment Dağılımı",
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def velocity_histogram(df):
        """Velocity score dağılımı"""
        fig = px.histogram(
            df,
            x='velocity_score',
            nbins=20,
            title='Satış Hızı (Velocity) Dağılımı',
            labels={'velocity_score': 'Velocity Score', 'count': 'Ürün Sayısı'},
            color_discrete_sequence=['#4CAF50']
        )
        
        # Normal ve HOT eşik çizgileri
        fig.add_vline(x=1.0, line_dash="dash", line_color="red", 
                     annotation_text="Normal (1.0)")
        fig.add_vline(x=1.5, line_dash="dash", line_color="orange",
                     annotation_text="HOT Eşik (1.5)")
        
        fig.update_layout(height=400, showlegend=False)
        
        return fig
    
    @staticmethod
    def stock_health_scatter(df):
        """Stok sağlığı scatter plot"""
        fig = px.scatter(
            df,
            x='days_of_stock',
            y='daily_sales_avg_7d',
            color='segment',
            size='total_stock',
            hover_data=['product_name', 'category', 'velocity_score'],
            title='Stok Sağlığı Analizi',
            labels={
                'days_of_stock': 'Stok Günü',
                'daily_sales_avg_7d': 'Günlük Satış (7g ort.)',
                'segment': 'Segment'
            },
            color_discrete_map=SEGMENT_COLORS
        )
        
        # Kritik ve ideal çizgiler
        fig.add_vline(x=7, line_dash="dash", line_color="red",
                     annotation_text="Kritik (7 gün)")
        fig.add_vline(x=30, line_dash="dash", line_color="green",
                     annotation_text="İdeal (30 gün)")
        
        fig.update_layout(height=500)
        
        return fig
    
    @staticmethod
    def category_performance_bar(df):
        """Kategori performansı grouped bar"""
        category_perf = df.groupby('category').agg({
            'daily_sales_avg_7d': 'sum',
            'total_stock': 'sum'
        }).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=category_perf['category'],
                y=category_perf['daily_sales_avg_7d'],
                name='Günlük Satış',
                marker_color='#2196F3'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Bar(
                x=category_perf['category'],
                y=category_perf['total_stock'],
                name='Toplam Stok',
                marker_color='#FF9800'
            ),
            secondary_y=True
        )
        
        fig.update_xaxes(title_text="Kategori")
        fig.update_yaxes(title_text="Günlük Satış", secondary_y=False)
        fig.update_yaxes(title_text="Stok Miktarı", secondary_y=True)
        
        fig.update_layout(
            title="Kategori Bazlı Performans",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def top_products_bar(df, n=10, metric='daily_sales_avg_7d', title="Top Ürünler"):
        """Top ürünler bar chart"""
        top_df = df.nlargest(n, metric)[['product_name', metric, 'segment']]
        
        colors = [SEGMENT_COLORS.get(seg, '#CCCCCC') for seg in top_df['segment']]
        
        fig = go.Figure(data=[go.Bar(
            y=top_df['product_name'],
            x=top_df[metric],
            orientation='h',
            marker=dict(color=colors),
            text=top_df[metric].apply(lambda x: format_number(x, 1)),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Değer: %{x:.2f}<extra></extra>'
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title=metric.replace('_', ' ').title(),
            yaxis_title="",
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def depot_stacked_bar(df, n=10):
        """Depo bazlı stok dağılımı stacked bar"""
        top_stock = df.nlargest(n, 'total_stock')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Akyazı',
            y=top_stock['product_name'],
            x=top_stock['stock_akyazi'],
            orientation='h',
            marker=dict(color='#4CAF50'),
            text=top_stock['stock_akyazi'],
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            name='Ana Depo',
            y=top_stock['product_name'],
            x=top_stock['stock_ana_depo'],
            orientation='h',
            marker=dict(color='#2196F3'),
            text=top_stock['stock_ana_depo'],
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            name='OMS',
            y=top_stock['product_name'],
            x=top_stock['stock_oms_total'],
            orientation='h',
            marker=dict(color='#FF9800'),
            text=top_stock['stock_oms_total'],
            textposition='inside'
        ))
        
        fig.update_layout(
            title='Depo Bazlı Stok Dağılımı (Top 10)',
            barmode='stack',
            xaxis_title='Stok Miktarı',
            height=400,
            hovermode='y unified'
        )
        
        return fig
    
    @staticmethod
    def engagement_conversion_scatter(df):
        """Engagement vs Conversion scatter"""
        fig = px.scatter(
            df,
            x='engagement_score',
            y='conversion_rate',
            color='final_score',
            size='daily_sales_avg_7d',
            hover_data=['product_name', 'segment'],
            title='Engagement vs Conversion Analizi',
            labels={
                'engagement_score': 'Engagement Score (%)',
                'conversion_rate': 'Conversion Rate (%)',
                'final_score': 'Final Score'
            },
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=500)
        
        return fig
    
    @staticmethod
    def transfer_needs_bar(allocation_df, n=10):
        """Transfer ihtiyacı bar chart"""
        transfer_df = allocation_df[allocation_df['transfer_from_ana_depo'] > 0].nlargest(
            n, 'transfer_from_ana_depo'
        )
        
        if len(transfer_df) == 0:
            # Boş grafik
            fig = go.Figure()
            fig.add_annotation(
                text="Transfer ihtiyacı yok",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title='Transfer İhtiyacı',
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        colors = [SEGMENT_COLORS.get(seg, '#CCCCCC') for seg in transfer_df['segment']]
        
        fig = go.Figure(data=[go.Bar(
            y=transfer_df['product_name'],
            x=transfer_df['transfer_from_ana_depo'],
            orientation='h',
            marker=dict(color=colors),
            text=transfer_df['transfer_from_ana_depo'].apply(lambda x: format_number(x, 0)),
            textposition='outside'
        )])
        
        fig.update_layout(
            title='Transfer İhtiyacı (Ana Depo → Akyazı)',
            xaxis_title='Transfer Miktarı',
            yaxis_title="",
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def segment_trend_line(df_with_history):
        """Segment bazlı satış trendi (eğer tarihsel veri varsa)"""
        # Bu fonksiyon gelecekte tarihsel veri eklendiğinde kullanılabilir
        pass
    
    @staticmethod
    def kpi_gauge(value, target, title, color='#4CAF50'):
        """KPI gauge chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            delta={'reference': target},
            gauge={
                'axis': {'range': [None, target * 1.5]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, target * 0.7], 'color': "lightgray"},
                    {'range': [target * 0.7, target], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': target
                }
            }
        ))
        
        fig.update_layout(height=250)
        
        return fig
