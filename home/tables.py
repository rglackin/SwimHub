import django_tables2 as tables
from .models import Swimmer, Competition
from django_tables2.utils import A

class SwimmerTable(tables.Table):
    
    class Meta:
        model = Swimmer
        template_name = "django_tables2/bootstrap4.html"
        fields = ("first_name","last_name","dob", )
        attrs = {
            "class":"table table-striped shadow table-hover sortable",
            "thead":{
                "class":"thead-dark text-white"
            }
            }    
        row_attrs = {'data-href': lambda record: record.get_absolute_url}

class CompTable(tables.Table):
    class Meta:
        model = Competition
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        fields = ("comp_name","location","start_date","end_date", )
        attrs = {
            "class":"table table-striped shadow table-hover",
            "thead":{
                "class":"thead-dark text-white"
            }
            }    
        row_attrs = {'data-href': lambda record: record.get_absolute_url}