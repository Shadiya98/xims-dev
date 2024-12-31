from django.db import models
import os
import uuid

from storages.backends.s3boto3 import S3Boto3Storage

class Users(models.Model):
  
    username = models.CharField(max_length=255, unique=True, null=True) 
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)   
    gender = models.CharField(
        max_length=255,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
    
        ]
    )
    date_of_birth = models.DateField()
    address =  models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_po_box = models.CharField(max_length=20, blank=True, null=True)
    province_state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, default =True ,null=True)
    department_division = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True) 
    phone = models.CharField(max_length=15, blank=True, null=True)
    office_phone = models.CharField(max_length=15, blank=True, null=True)
    mobile_phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    secret_question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    STATUS_CHOICES = [
        ('live', 'live'),
        ('blocked', 'Blocked'),
          
         
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='live')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    


class MediaStorage(S3Boto3Storage):
    location = 'media'
def generate_unique_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('policy_documents/', unique_filename)
class PolicyDocumentation(models.Model):
    text =  models.TextField(blank=True, null=True)
    quality_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename, blank=True)
    environmental_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)
    health_safety_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)
    energy_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)
    integrated_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)
    
    def __str__(self):
        return self.text
    
def generate_unique_filename_training(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('Training_attachments/', unique_filename)
class Training(models.Model):
    STATUS_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External'),
        ('Client/Legal', 'Client/Legal'),
        ('Online', 'Online')
        
    ]
    TYPE_CHOICES = [
        ('Requested', 'Requested'),
        ('Completed', 'Completed'),
    ]
    training_title =  models.CharField(max_length=100)
    expected_results = models.TextField(blank=True, null=True)
    actual_results = models.TextField(blank=True, null=True)
    type_of_training = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Internal')
    training_attendees = models.ManyToManyField(Users, related_name='training_attendees', blank=True)
    status = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Requested')
    requested_by = models.ForeignKey(Users, related_name='training_requested_by', on_delete=models.SET_NULL, null=True, blank=True)
    date_planned = models.DateField()
    date_conducted = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = venue = models.CharField(max_length=255)
    attachment = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_training, blank=True, null=True)
    training_evaluation = models.TextField(blank=True, null=True)
    evaluation_date = models.DateField()
    evaluation_by = models.ForeignKey(Users, related_name='evaluation_by', on_delete=models.SET_NULL, null=True, blank=True)
    send_notification = models.BooleanField(default=False)
    
    def __str__(self):
        return self.training_title
    
class EmployeeEvaluation(models.Model):
    evaluation_title = models.CharField(max_length=100)
    valid_till = models.DateField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.evaluation_title
    
class EmployeeSurvey(models.Model):
    survey_title = models.CharField(max_length=100)
    valid_till = models.DateField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.survey_title


def generate_unique_filename1(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('awareness/', unique_filename)  
class AwarenessTraining(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=255,
        choices=[
            ('YouTube video', 'YouTube video'),
            ('Presentation', 'Presentation'),
            ('Web Link','Web Link')
  
        ]
    )
    youtube_link = models.URLField(blank=True, null=True)
    upload_file = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename1, blank=True, null=True)
    web_link = models.CharField(max_length=100,blank=True, null=True)
    def __str__(self):
        return self.title


class Agenda(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title
   


def generate_unique_filename_minute(instance, filename):
    
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('minutes_attached/', unique_filename)     
class Meeting(models.Model):
    TITLE_CHOICES = [
        ('Normal', 'Normal'),
        ('Specific', 'Specific'),
        
    ]
    agenda = models.ManyToManyField(Agenda, related_name='agenda', blank=True)
    title = models.CharField(max_length=255,blank=True, null=True )
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField (blank=True, null=True)
    meeting_type = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Normal')
    venue = models.CharField(max_length=255,blank=True, null=True )
    attendees = models.ManyToManyField(Users, related_name='meeting_attendees', blank=True)
    called_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    is_published = models.BooleanField(default=False )
    send_notification = models.BooleanField(default=False)
    minutes = models.TextField(blank=True,null=True)
    minutes_attached = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_minute, blank=True, null=True)
    def __str__(self):
        return self.title
    


class Cause(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title


class CarNumber(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True )
    source = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Audit', 'Audit'),
            ('Presentation', 'Presentation'),
            ('Web Link','Web Link')
  
        ]
    )
    root_cause = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Test', 'Test')])
    
    description = models.TextField(blank=True,null=True)
    date_raised = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    Status_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted','Deleted')
        
    ]
    status = models.CharField(max_length=20, choices=Status_CHOICES, default='Pending')
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    action = models.IntegerField(blank = True,null=True)
    action_or_corrections = models.TextField(blank=True,null=True)
    send_notification = models.BooleanField(default=False)
    def __str__(self):
        return self.title



class  InternalProblems(models.Model):
    TITLE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        
    ] 
    cause = models.ManyToManyField(Cause, related_name='agenda', blank=True)
    action_taken = models.TextField(blank=True,null=True)
    date = models.DateField(blank=True, null=True)
    corrective_action = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    problem = models.TextField(blank=True,null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    solved_after_action = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    corrections = models.TextField(blank=True,null=True)
    no_car = models.ForeignKey(CarNumber, on_delete=models.SET_NULL, null=True )
    def __str__(self):
        return self.action_taken


def generate_unique_filename_audit(instance, filename):
    
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('audit/', unique_filename)     
class Audit(models.Model):
    TITLE_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External'),
        
    ]
    title = models.CharField(max_length=50,blank =True,null = True)
    audit_from = models.CharField(max_length=50,blank =True,null = True)
    audit_from_internal =  models.ManyToManyField(Users, related_name='users' ,blank =True)
    area = models.CharField(max_length=50,blank =True,null = True)
    proposed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True,null=True)
    certification_body  =  models.CharField(max_length=50,blank =True,null = True)
    audit_type =  models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Internal')
    procedures = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Test', 'Test')])
        
    date_conducted = models.DateField(blank=True, null=True)
    upload_audit_report = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    upload_non_coformities_report =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    
    def __str__(self):
        return self.title
    

class Inspection(models.Model):
    
    title = models.CharField(max_length=50,blank =True,null = True)
    inspector_from = models.CharField(max_length=50,blank =True,null = True)
    inspector_from_internal =  models.ManyToManyField(Users, related_name='inspector_users' ,blank =True)
    area = models.CharField(max_length=50,blank =True,null = True)
    proposed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True,null=True)
    certification_body  =  models.CharField(max_length=50,blank =True,null = True)
    inspector_type = models.CharField(max_length=50,blank =True,null = True)
    procedures = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Test', 'Test')])
        
    date_conducted = models.DateField(blank=True, null=True)
    upload_inspection_report = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    upload_non_coformities_report =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    
    def __str__(self):
        return self.title
    

class Customer(models.Model):
    name = models.CharField(max_length=50,blank =True,null = True)
    address =  models.TextField(blank=True,null=True)
    city = models.CharField(max_length=50,blank =True,null = True)
    state = models.CharField(max_length=50,blank =True,null = True)
    zipcode = models.CharField(max_length=50,blank =True,null = True)
    country = models.CharField(max_length=50,blank =True,null = True)
    email = models.EmailField(blank =True,null = True)
    contact_person = models.CharField(max_length=50,blank =True,null = True)
    phone = models.CharField(max_length=20, blank=True) 
    alternate_phone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=50,blank =True,null = True)
    notes = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return self.name
    
class Category(models.Model):
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title

class Complaints(models.Model):
    TITLE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        
    ] 
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True )
    details = models.TextField(blank=True,null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    corrections = models.CharField(max_length=50,blank =True,null = True)
    solved_after_action =  models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    category = models.ManyToManyField(Category, related_name='category' ,blank =True)
    immediate_action = models.TextField(blank=True,null=True)
    date = models.DateField(blank=True, null=True)
    corrective_action_need = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    no_car = models.ForeignKey(CarNumber, on_delete=models.SET_NULL, null=True )
    
    def __str__(self):
        return self.customer