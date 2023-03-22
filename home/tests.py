import datetime
from django.test import TestCase, RequestFactory
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError,EmptyResultSet
from .models import Swimmer,SwimTime,PersonalBest,Race,Competition
from django.urls import reverse

# Create your tests here.
def createSwimmer(date):
     return Swimmer.objects.create(first_name='firstname', last_name='surname',dob=date)

def createSwimTime(swimmer,distance):
    return SwimTime.objects.create(swimmer=swimmer,distance = distance,strokeType="FC",date=datetime.datetime(2020,1,1),time=datetime.timedelta(seconds=60))
def createSwimTimeWithSecs(swimmer,distance,seconds):
    return SwimTime.objects.create(swimmer=swimmer,distance = distance,strokeType="FC",date=datetime.datetime(2020,1,1),time=datetime.timedelta(seconds=seconds))
def createGenericRace():
    comp = Competition.objects.create(comp_name="TestComp",location="TestLoc",start_date=datetime.datetime(2023,1,1),end_date=datetime.datetime(2023,2,2))
    return Race.objects.create(distance=50,strokeType='FC',competition_id=comp.id,age_range_lower=12,age_range_upper=12,is_relay=False)
def setup_view(view, request, *args, **kwargs):
        """
        Mimic ``as_view()``, but returns view instance.  Use this function to get view instances on which you can run unit tests,    by testing specific methods.
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

def createSwimmerWithDob():
    dateBirth = datetime.datetime.now() - relativedelta(years=5)
    return Swimmer.objects.create(first_name='firstname', last_name='surname',dob=dateBirth)


class SwimmerModelTests(TestCase):
    def test_dob_is_5_years_old(self):
        """
        if user enters swimmer younger than 5 years old raise validation error
        """
        dateBirth = datetime.datetime.now() - relativedelta(years=5)
        dateBirth+= relativedelta(days=1)
        self.assertRaises(ValidationError,createSwimmer, dateBirth)
    def test_future_dob(self):
        """
        if user enters date of birth in future raise validation error
        """
        dateBirth = datetime.datetime.now() + relativedelta(years=5)
        self.assertRaises(ValidationError,createSwimmer, dateBirth)
    def test_can_create_swimmer(self):
        """
        Swimmer can be created with valid fields
        """
        dateBirth = datetime.datetime.now() - relativedelta(years=5)
        createSwimmer(dateBirth)

class SwimmerListTests(TestCase):
    def test_view_url_accesible_by_name(self):
        """
        SwimmerListView url accessible by reverse('name')
        """
        response = self.client.get(reverse('home:swimmers'))
        self.assertEqual(response.status_code,200)

    def test_view_uses_correct_template(self):
        """
        SwimmerListView uses correct template
        """
        response =self.client.get(reverse('home:swimmers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/swimmer_list.html')

    def test_no_swimmers(self):
        """
        If no swimmers exist,appropriate message displayed 
        """
        response = self.client.get(reverse('home:swimmers'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "No swimmers are available")
        self.assertQuerysetEqual(response.context['swimmers_list'],[])
    def test_swimmer_displayed(self):
        """
        If a swimmer exists, display them
        """
        swimmer = createSwimmerWithDob()
        response = self.client.get(reverse('home:swimmers'))
        self.assertQuerysetEqual(
            response.context['swimmers_list'],[swimmer]
        )
    def test_swimmers_displayed(self):
        """
        If multiple swimmers exist, display them
        """
        swimmer1 = createSwimmerWithDob()
        swimmer2 = createSwimmerWithDob()
        response = self.client.get(reverse('home:swimmers'))
        self.assertQuerysetEqual(
            response.context['swimmers_list'],[swimmer2,swimmer1], ordered=False
        )
    def test_view_url_exists_at_desired_location(self):
        """
        SwimmerList view exists at desired location
        """
        response = self.client.get('/swimmers/')
        self.assertEqual(response.status_code,200)

    
class SwimmerDetailView(TestCase):
    
    def setUp(self):
        # create a parent object and some child objects
        self.parent_object = createSwimmerWithDob()
        self.child_objects = [
            createSwimTime(self.parent_object,50),
            createSwimTime(self.parent_object,1024)
            ]
        #print(self.child_objects)
        
    def test_view_url_accessible_by_name(self):
        """
        SwimmerDetailView url accessible by reverse('name', pk)
        """

        response= self.client.get(reverse('home:detail', kwargs={'pk':self.parent_object.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        SwimmerDetailView uses correct template
        """
        
        response =self.client.get(reverse('home:detail', kwargs={'pk':self.parent_object.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/swimmer_detail.html')
    def test_view_url_exists_at_desired_location(self):
        """
        SwimmerDetail view exists at desired location
        """
        response = self.client.get(f'/swimmer/detail/{self.parent_object.id}/')
        self.assertEqual(response.status_code,200)

    
    
    def test_get_child_objects(self):
        response = self.client.get('/swimmer/detail/1/')
        
        # make sure the response contains the expected child objects
        self.assertContains(response, '50')
        self.assertContains(response, '1024')
    
class PersonalBestModelTests(TestCase):
    def setUp(self):
        #create Swimmer with times
        self.swimmer = createSwimmerWithDob()
        createSwimTime(self.swimmer,100)
    def test_delete_checks_existing_times(self):
        """
        
        """
        #Create Second Time
        createSwimTimeWithSecs(self.swimmer ,100,70)
        time = SwimTime.objects.filter(swimmer=1)[0]
        t2 = SwimTime.objects.filter(swimmer=1)[1]
        #assign pb to PersonalBest of swimmer
        pb = PersonalBest.objects.get(swimmer = self.swimmer)
        #assert pb is referencing original swimTime
        self.assertEqual(pb.swim_time.id, time.id)
        #deleting time calls pre_delete signal
        time.delete()
        #re-assign pb to new PersonalBest
        pb = PersonalBest.objects.get(swimmer = self.swimmer)
        #print(f"{pb}")
        self.assertEqual(pb.swim_time.id, t2.id)
    
class RaceModelTests(TestCase):
    def setUp(self):
        
        self.race = createGenericRace()
    
    def test_no_eligible_swimmers(self):
        """
        If no eligible swimmers exist for Race,return false
        """
        x =self.race.get_eligible_swimmers()
        self.assertFalse(x)
    def test_fastest_IM(self):
        """
       
        """
        #TODO
        x = self.race.get_fastest_IM()