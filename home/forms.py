
from django import forms
from django.forms import inlineformset_factory
import datetime
from .models import Swimmer, SwimTime,Competition,Race
from django.utils.translation import gettext as _
from .widgets import MicrosecondWidget
from django.core.exceptions import ValidationError
# create a ModelForm
now =datetime.datetime.now()
class SwimmerForm(forms.ModelForm):
    # specify the name of model to use
    
    class Meta:
        model = Swimmer
        fields = "__all__"
        
        widgets = {
            'dob': forms.SelectDateWidget(years=range(2002,now.year-4))
        }
    
class TimeForm(forms.ModelForm):
    # specify the name of model to use
    
    class Meta:
        model = SwimTime
        fields = ('time', 'distance', 'strokeType', 'date')
        now =datetime.datetime.now()
        widgets = {
            'date': forms.SelectDateWidget(years=range(now.year-5,now.year+1)),
            #TODO time formatting needs to be changed to mm:ss:ms
            #'time': MicrosecondWidget
        }
TimeFormSet = inlineformset_factory(Swimmer,SwimTime,form = TimeForm, extra=0, can_delete = True,can_delete_extra=True)

class CompForm(forms.ModelForm):
    class Meta:
        model= Competition
        fields = ('comp_name','location','start_date','end_date')
        
        widgets = {
            'start_date': forms.SelectDateWidget(),
            'end_date': forms.SelectDateWidget(),
        }
    def clean(self):
        super(CompForm, self).clean()
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if(start_date>end_date):
            raise ValidationError(
                _("Error: Start date must be before end date")
            )
        
        
class RaceForm(forms.ModelForm):
    class Meta:
        model= Race
        fields = ('distance','strokeType','age_range_lower','age_range_upper','is_relay')
        
class LinkSwimmersToRaceForm(forms.ModelForm):
    
    class Meta:
        model = Race
        fields = ('swimmers','competition')
        widgets = {
            'swimmers': forms.CheckboxSelectMultiple,
            'competition':forms.HiddenInput
        }
        labels = {
            'swimmers': 'Select swimmers to link to race',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['swimmers'].queryset = Swimmer.objects.all()
        
        self.fields['swimmers'].label_from_instance = lambda obj: f"<td>{obj}</td><td>{obj.find_personal_best(self.instance.distance, self.instance.strokeType)}</td><td>{obj.most_recent_time(self.instance.distance, self.instance.strokeType)}</td>"
        
    
    def save(self):
        swimmers = self.cleaned_data['swimmers']
        #print("\n--------------\nSave func of Link Form\n\n")
        #COMMENT This adds the record(s) to the manytomany link table
        race = self.instance
        race.swimmers.add(*swimmers)