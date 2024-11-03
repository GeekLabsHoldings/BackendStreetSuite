from django_filters import rest_framework as filters
from Alerts.models import Alert  # Replace with your actual model

class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class AlertFilters(filters.FilterSet):
    risk_level = filters.CharFilter(field_name="risk_level")
    strategy = filters.CharFilter(field_name="strategy")
    ticker__market_capital = filters.CharFilter(field_name="ticker__market_capital")
    ticker__industry = CharInFilter(field_name="ticker__industry__type", lookup_expr='in')

    class Meta:
        model = Alert 
        fields = ["risk_level", "ticker__industry", "strategy", "ticker__market_capital" , "time_frame"]
