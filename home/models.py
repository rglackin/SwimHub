from django.db import models
import datetime
from django.utils import timezone
from django.urls import reverse
import datetime
from datetime import date, timedelta
from django.core.exceptions import ValidationError,EmptyResultSet
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext as _
from django.db.models import OuterRef, Subquery

# Create your models here.

def format_time(time):
        secs , microseconds = time.seconds, time.microseconds
        mins = secs//60
        secs = secs-(mins*60)
        millisecs  = microseconds/1000
        return "{:02}:{:02}:{:03}".format(int(mins),int(secs),int(millisecs))

class SwimmingInfo(models.Model):
    FRONTCRAWL = 'FC'
    BACKCRAWL = 'BC'
    BUTTERFLY = 'BF'
    BREASTSTROKE = 'BS'
    MEDLEY = 'IM'
    
    strokeTypes = [
    (FRONTCRAWL,'Front Crawl'),
    (BACKCRAWL,'Back Crawl'),
    (BUTTERFLY,'Butterfly'),
    (BREASTSTROKE,'Breaststroke'),
    (MEDLEY, 'Medley')
    ]
    
    #COMMENT Gives child models distance and strokeType fields
    distance = models.PositiveIntegerField(_('Distance'),null = False, default=50)
    strokeType = models.CharField(_('Stroke Type'),max_length=20, choices=strokeTypes, default=FRONTCRAWL)
    class Meta:
        abstract = True

class Swimmer(models.Model):
    first_name = models.CharField('First Name',max_length=50)
    last_name = models.CharField('Last Name',max_length=50)
    dob = models.DateField("Date Of Birth", default = datetime.date(2010,1,1))
    @property
    def get_age(self):
        today = date.today()
        age = today.year - self.dob.year
        return age
    
    def get_absolute_url(self):
        return(reverse('home:detail', kwargs={'pk':self.id}))
    
    #Validation
    def clean(self):
        currentDate = date.today()
        fiveYears=currentDate - relativedelta(years=5)

        if (self.dob>fiveYears):
            if(self.dob>currentDate):
                raise ValidationError(
                    {'dob':'Date of birth cannot be in the future'}
                )
            else:
                raise ValidationError(
                    {'dob':'Swimmer must be at least 5 years old'}
                )

    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def find_personal_best(self, distance, strokeType):
        try:
            pb = PersonalBest.objects.get(
                swimmer= self,
                swim_time__strokeType= strokeType,
                swim_time__distance= distance)
            return pb
            
        except:
            return "---"
    
    def most_recent_time(self,distance,strokeType):
        try:
            time =  self.swimtime_set.filter(distance=distance, strokeType=strokeType).order_by('-date')[0]
            return format_time(time.time)
        except:
            return "---"

class SwimTime(SwimmingInfo):
    #COMMENT One Swimmer - Many Times: Foreign Key References Swimmer who owns SwimTime
    swimmer =models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    
    time = models.DurationField(_('Time'), default= timedelta(minutes=1, seconds=1, milliseconds=10))
    
    date = models.DateField(_('Date Recorded'),default = timezone.now)
    
    #COMMENT Save called when Update/Add SwimTime form is submitted
    def save(self, *args, **kwargs):
        #COMMENT full_clean validates all data
        self.full_clean()
        super().save(*args, **kwargs)
        
        #COMMENT when saving time check if personal best needs updated
        PersonalBest.update_personal_best(self)
    
    def __str__(self): 
        #COMMENT returns readable String containing Distance and StrokeType of SwimTime
        return f"Distance: {self.distance} \nStrokeType: {self.strokeType} \nTime: {self.time}"

    def get_time(self):
        return format_time(self.time)

    def find_difference(self):
        personal_best = PersonalBest.objects.get(
                swimmer= self.swimmer,
                swim_time__strokeType= self.strokeType,
                swim_time__distance= self.distance
            )
        pbTime = personal_best.swim_time.time
        if pbTime == self.time :
            return False
        else:

            difference = self.time - pbTime
            return format_time(difference)

    
    
class PersonalBest(models.Model):
    #COMMENT One Swimmer - Many PBs: Foreign key references parent swimmer  
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    #COMMENT swimTime contains reference to time in swimTime table  
    swim_time = models.ForeignKey(SwimTime, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('swimmer','swim_time')
    
    @classmethod
    def update_personal_best(cls,swimTime):
        #COMMENT tries to get personal best of same swimmer, stroketype and distance 
        try:        
            personal_best = cls.objects.get(
                swimmer= swimTime.swimmer,
                swim_time__strokeType= swimTime.strokeType,
                swim_time__distance= swimTime.distance
            )
        #COMMENT if Personal Best not yet recorded, creates personal best
        except cls.DoesNotExist:
            personal_best = cls.objects.create(
                swimmer=swimTime.swimmer,
                swim_time = swimTime
            )
        #COMMENT if no error, time of newly recorded stroke and PB are comapared.
        #COMMENT PB updated if necessary
        else:
            if swimTime.time < personal_best.swim_time.time:
                personal_best.swim_time = swimTime
                personal_best.save()
    
    def delete(self, *args,**kwargs):
        #COMMENT if time deleted, check for other times of same stroke and distance
        
        try:
            times = SwimTime.objects.filter(
            swimmer=self.swimmer,
            strokeType=self.swim_time.strokeType,
            distance=self.swim_time.distance,
        )
            
        #COMMENT except delete personal best if no times found
        except SwimTime.DoesNotExist:
            return super().delete(*args,**kwargs)
        #COMMENT else times exist call update_personal_best() for quickest time
        else:
            times = times.order_by('time')
            #COMMENT Get the fastest swim time
            fastest_time = times.first()
            self.update_personal_best(fastest_time)
    
    def __str__(self) :
        return f"{format_time(self.swim_time.time)}"
       
    
class Competition(models.Model):
    comp_name  = models.CharField('Competition Name', max_length=50)
    #TODO in future, address will be used with google maps api to display location of competition with a map
    location = models.CharField('Competition Location',max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def get_absolute_url(self):
        return(reverse('home:comp_detail', kwargs={'pk':self.id}))
    
    def get_status(self):
        today = date.today()
        start = self.start_date
        end = self.end_date
        if start<today:
            if end<today:
                return ("<span class='text-danger'>Finished</span>")
            else:
                return ("<span class='text-warning'>Ongoing</span>" )
        else:
            return ("<span class='text-success'>Upcoming</span>") 
    def __str__(self) :
         return f"{self.comp_name}, {self.location}"

class Race(SwimmingInfo):
    #COMMENT inherits distance and strokeType from SwimmingInfo
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    swimmers = models.ManyToManyField(Swimmer)
    age_range_lower = models.PositiveSmallIntegerField(_('Lower Age Range'),default=12)
    age_range_upper = models.PositiveSmallIntegerField(_('Upper Age Range'),default=15)
    is_relay = models.BooleanField(_('Relay'),default=False)
    def get_absolute_url(self):
        return(reverse('home:race_detail', kwargs={'pk':self.id}))

    def __str__(self) :
        return f"{self.id},Comp:{self.competition}, Age Range :{self.age_range_lower}-{self.age_range_upper}, Stroketype:{self.strokeType}"

    def get_eligible_swimmers(self):
        all_swimmers = Swimmer.objects.all()
        swimmers = []
        #Only gets swimmers in age range
        for swimmer in all_swimmers:
            age = swimmer.get_age               
            if age>=self.age_range_lower and age<=self.age_range_upper:
                swimmers.append(swimmer.id)
        eligible_swimmers = Swimmer.objects.filter(id__in=swimmers)
        #Excludes any swimmers that are already entered in the race from selection on the form
        eligible_swimmers = eligible_swimmers.exclude(id__in =self.swimmers.all())
        fastest_times = PersonalBest.objects.filter(
            swim_time__distance=self.distance,
            swim_time__strokeType=self.strokeType
        ).order_by('swim_time__time').values('swim_time__time', 'swim_time__swimmer')
        
        #Orders eligible swimmers by fastest time
        #OuterRef ensures only times with matching Primary Keys are filtered
        eligible_swimmers = eligible_swimmers.order_by(
            Subquery(fastest_times.filter(swimmer=OuterRef('pk')).values('swim_time__time')[:1]).asc(nulls_last= True)
        )
        return eligible_swimmers

    def get_fastest_IM(self):
        try:
            swimmers = self.get_eligible_swimmers()
            if not swimmers:
                raise EmptyResultSet

        except:
              return