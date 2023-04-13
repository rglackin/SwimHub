from django.shortcuts import render, redirect
from .models import Swimmer, SwimTime, PersonalBest, Competition,Race
from django.views import generic
#from django.http import HttpResponse
from .forms import SwimmerForm, TimeFormSet,CompForm,RaceForm,LinkSwimmersToRaceForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django_tables2 import SingleTableView
from .tables import SwimmerTable,CompTable
from django.utils import timezone


# Create your views here.



#----------------Home Page View
class HomePageView(generic.TemplateView):
    template_name = "home/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["noSwimmers"] = Swimmer.objects.all().count()
        context["noTimes"]= SwimTime.objects.all().count()
        nextComp = self.get_next_comp()
        compDate = f"Start Date: {nextComp.start_date}"
        context["nextComp"] = nextComp
        context["compDate"]=compDate
        return context
    def get_next_comp(self):
        today = timezone.datetime.today()
        nextComp = Competition.objects.filter(start_date__gte=today).order_by("start_date").first()
        return nextComp
#----------------Swimmer List View
class SwimmerListView(SingleTableView):
    model = Swimmer
    context_object_name = "swimmers_list"

    table_class = SwimmerTable
    def get_queryset(self):
        fname = self.request.GET.get("fname")
        lname = self.request.GET.get("lname")
        if not fname and not lname:
            fname = ""
            lname = ""
            return super().get_queryset()
        object_list = Swimmer.objects.filter(
            Q(first_name__istartswith=fname)&Q(last_name__istartswith=lname))
        return object_list
    
        

#----------------Add Swimmer View
class SwimmerFormView(generic.FormView):
    form_class=SwimmerForm
    template_name = 'home/add_swimmer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prevAdded"] = Swimmer.objects.all().order_by('-id')[:5]
        return context
    
    def form_valid(self, form):
        object =form.save()
        pk = object.id
        if self.request.POST.get('view'):
            self.success_url= reverse('home:update', kwargs={'pk':pk})
        elif self.request.POST.get('continue'):
            self.success_url= reverse('home:add swimmer')
        return super(SwimmerFormView, self).form_valid(form)

#----------------Swimmer Detail View
class SwimmerDetailView(generic.DetailView):
    model = Swimmer
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        #COMMENT get_child_objects() returns queryset of swimTimes for access in template
        context['swimTimes']=self.get_child_objects()
        return context
   
    def get_child_objects(self):
        #COMMENT gets swimmer from detailView
        swimmer_object = self.get_object()
        #COMMENT gets queryset of times
        times_objects = swimmer_object.swimtime_set.all()

        if self.request.method == 'GET':
            #COMMENT gets strokeType and distance from search form
            strokeType = self.request.GET.get("strokeType")
            distance = self.request.GET.get("distance")
            #COMMENT if no input in search form set equal to whitespace
            if not strokeType and not distance:
                strokeType=""
                distance=""
            #COMMENT filters through all times for requested times
            times_objects = times_objects.filter(
            Q(strokeType__icontains=strokeType)&Q(distance__icontains=distance))
            
        return times_objects   
    
    #TODO In future, swimmer detail should display upcoming races for swimmers.

#----------------Swimmer Update View
class SwimmerUpdateView(generic.UpdateView):
    model = Swimmer
    template_name = "home/swimmer_update.html"
    form_class = SwimmerForm
    def get_success_url(self):
        return (Swimmer.get_absolute_url(self.object))

    def get_formsets(self):
        return TimeFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='times')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #COMMENT passes CUD time formset to context so it is accessible in template by name formset
        context["formset"] = self.get_formsets()
        return context

    def post(self, request, pk):
        #COMMENT gets Swimmer object, context list, form and formset
        self.object = self.get_object()
        context = self.get_context_data()
        form = SwimmerForm(request.POST, instance=self.object)
        formset = self.get_formsets()
        #COMMENT if Swimmer form invalid re-render template with error
        if not form.is_valid():
            return render(request, self.template_name, context)
        #COMMENT if all swimTime forms (formset) is valid call formset_times_valid() passing formset in
        if formset.is_valid():
            self.formset_times_valid(formset)
        #COMMENT else re-render template with error
        else:
            return render(request, self.template_name, context)
        return super().form_valid(form)

    def formset_times_valid(self, formset):
        #COMMENT instantiates formset as variable
        times = formset.save(commit=False) 
        for obj in formset.deleted_objects:
            obj.delete()
        for time in times:
            time.product = self.object
            time.save()
#----------------Competition Menu View
class CompetitonMenu(generic.TemplateView):
    template_name = "home/competition_menu.html"

#----------------Competition List View
class CompetitionList(SingleTableView):
    model = Competition
    context_object_name ="comp_list"
    table_class = CompTable

    def get_queryset(self):
        status = self.request.GET.get('status', '')
        now = timezone.now()
        if status == 'finished':
            return Competition.objects.filter(end_date__lt=now)
        elif status == 'upcoming_ongoing':
            return Competition.objects.exclude(end_date__lt=now)
        else:
            return Competition.objects.all()
#----------------Competition Create View
class CompetitionCreateView(generic.CreateView):
    model= Competition
    template_name_suffix = '_create'  
    form_class = CompForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prevAdded"] = Competition.objects.all().order_by('-id')[:5]
        return context

#----------------Competition Detail View
class CompetitionDetailView(generic.DetailView):
    
    model = Competition

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        #COMMENT get_child_objects() returns queryset of swimTimes for access in template
        context['race_form']= RaceForm()
        context['races']=self.get_child_objects()
        return context
    
    def get_child_objects(self):
        #COMMENT gets competition from detailView
        comp_object = self.get_object()
        #COMMENT gets queryset of races
        race_objects = comp_object.race_set.all()

        if self.request.method == 'GET':
            #COMMENT gets strokeType and distance from search form
            strokeType = self.request.GET.get("strokeType")
            distance = self.request.GET.get("distance")
            #COMMENT if no input in search form set equal to whitespace
            if not strokeType and not distance:
                strokeType=""
                distance=""
            #COMMENT filters through all times for requested times
            race_objects = race_objects.filter(
            Q(strokeType__icontains=strokeType)&Q(distance__icontains=distance))
            
        return race_objects   

#----------------Competition Update View
class CompetitionUpdateView(generic.UpdateView):
    model = Competition
    form_class = CompForm
    #COMMENT uses generic update template - DRY
    template_name = "home/generic_update.html"
    #COMMENT passes data in as context to distinguish between models
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = "Competition"
        context['model'] = self.get_object()
        return context
#----------------Create Race View
class RaceCreateView(generic.CreateView):
    model= Race
      
    template_name = "home/link_swimmers.html"
    form_class = RaceForm
    
    def form_valid(self, form):
        #COMMENT Set the competition for the new race
        form.instance.competition = Competition.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        #COMMENT Redirect to the competition detail page after creating a new race
        return reverse_lazy('home:comp_detail', kwargs={'pk': self.kwargs['pk']})

class RaceUpdateView(generic.UpdateView):
    model = Race
    form_class = RaceForm
    template_name = "home/generic_update.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = "Race"
        context['model'] = self.get_object()
        return context
#----------------Competition Detail and Create Race Combined View
class CompRaceView(generic.View):
    def get(self, request, *args, **kwargs):
         view = CompetitionDetailView.as_view()
         return view(request, *args, **kwargs) 

    def post(self, request, *args, **kwargs) :
         view = RaceCreateView.as_view()
         return view(request, *args, **kwargs) 

#----------------Race Detail View
class RaceDetailView(generic.DetailView):
    model= Race
    #TODO IM Calculation of fastest combination
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        self.race = self.get_object()
        #COMMENT Creates form, with the race being initially assigned to the current object
        
        form = LinkSwimmersToRaceForm(instance = self.race)

        #COMMENT Updates the queryset of the swimmer field to contain only swimmers eligible for the race
        eligible_swimmers =self.race.get_eligible_swimmers()
        form.fields['swimmers'].queryset = eligible_swimmers
        context['eligible_swimmers'] = eligible_swimmers
        # form.fields['competition'].initial = self.race.competition()
        context['race_swimmer_form']= form
        context['swimmers']=self.race.swimmers.all
        return context
    
#----------------Add swimmer to race view 
class RaceSwimmerAddView(generic.UpdateView): 
    model = Race
    form_class = LinkSwimmersToRaceForm
    template_name = "home/link_swimmers.html"
        
    def form_valid(self, form):
        #COMMENT Set the race for the swimmer
        form.instance.race = Race.objects.get(id=self.kwargs['pk'])
        
        self.get_context_data()
        form.save()
        return super().form_valid(form)
    def get_success_url(self):
        #COMMENT Redirect to the competition detail page after creating a new race
        
        return reverse('home:race_detail', kwargs={'pk': self.kwargs['pk']})

#----------------Race Detail and Add Swimmer to Race View
class RaceView(generic.View):
    
    def get(self, request, *args, **kwargs):
         view = RaceDetailView.as_view()
         return view(request, *args, **kwargs) 

    def post(self, request, *args, **kwargs) :
         view = RaceSwimmerAddView.as_view()
         return view(request, *args, **kwargs) 

#----------------Delete Swimmer Method  
def delete_swimmer(request, pk):
    try:
        swimmer = Swimmer.objects.get(id=pk)
    except Swimmer.DoesNotExist:
        messages.success(request, 'Object Does not exist' )
        return redirect('home:update', pk=swimmer.id)
    
    swimmer.delete()
    messages.success(
        request,'Swimmer deleted successfully'
    )
    return redirect('home:swimmers')
#----------------Delete Competition Method  
def delete_competition(request, pk):
    try:
        comp = Competition.objects.get(id=pk)
    except Competition.DoesNotExist:
        messages.success(request, 'Object Does not exist' )
        return redirect('home:index')
    
    comp.delete()
    messages.success(
        request,'Competition deleted successfully'
    )
    return redirect('home:comp_menu')

#----------------Delete Race Method  
def delete_race(request, pk):
    try:
        race = Race.objects.get(id=pk)
    except Race.DoesNotExist:
        messages.success(request, 'Object Does not exist' )
        return redirect('home:index')
    
    race.delete()
    messages.success(
        request,'Race deleted successfully'
    )
    return redirect(race.competition.get_absolute_url())