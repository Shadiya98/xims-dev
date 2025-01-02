<<<<<<< HEAD
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
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    
    def __str__(self):
        return str(self.customer.name)


class Question(models.Model):
    question_text = models.TextField(blank=True, null=True)
   

    def __str__(self):
        return self.question_text 
    
class CustomerSatisfaction(models.Model):
    title = models.CharField(max_length=50,blank =True,null = True)
    calid_till  = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    questions = models.ForeignKey(Question, blank=True,null=True ,on_delete=models.SET_NULL,)
    answer = models.IntegerField(blank=True, null=True) 
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True )
    

    def __str__(self):
        return self.title
    

class Supplier(models.Model):
    company_name = models.CharField(max_length=50,blank =True,null = True)
    email = models.EmailField(blank =True,null = True) 
    address = models.TextField(blank=True,null=True)
    state = models.CharField(max_length=50,blank =True,null = True)
    country = models.CharField(max_length=50,blank =True,null = True)
    website = models.TextField(blank=True,null=True)
    city =  models.CharField(max_length=50,blank =True,null = True)
    postal_code = models.CharField(max_length=50,blank =True,null = True)
    phone = models.CharField(max_length=50,blank =True,null = True)
    alternate_phone =models.CharField(max_length=50,blank =True,null = True)
    fax =models.CharField(max_length=50,blank =True,null = True)
    contact_person = models.CharField(max_length=50,blank =True,null = True)
    qualified_to_supply = models.CharField(max_length=50,blank =True,null = True)
    notes = models.TextField(blank=True,null=True)
    analysis_needed = models.BooleanField(default=False)
    resolution = models.CharField(max_length=50,blank =True,null = True)
    active = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    selection_criteria = models.CharField(max_length=50,blank =True,null = True)
    STATUS_CHOICES = [
        ('Approved', 'Approved'),
        ('Provisional', 'Provisional'),
        ('Not Approved','Not Approved')
          
         
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Approved')
    approved_date =  models.DateField(blank=True, null=True)
    pre_qualification = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    

    def __str__(self):
        return self.company_name

class SupplierProblem(models.Model):
    TITLE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True )
    problem = models.TextField(blank=True,null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    corrective_action_need = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    date =  models.DateField(blank=True, null=True)
    immediate_action = models.TextField(blank=True,null=True)
    solved = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    no_car = models.ForeignKey(CarNumber, on_delete=models.SET_NULL, null=True )

    def __str__(self):
        return self.supplier.company_name
    
class Compliance(models.Model):
    compliance_no = models.CharField(max_length=50,blank =True,null = True)
    compliance_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Legal', 'Legal'),
            ('Business', 'Business'),
            ('Client','Client'),
            ('Process/Specification','Process/Specification')
  
        ]
    )
    attach_document = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    compliance_remarks =  models.TextField(blank=True,null=True)
    rivision = models.CharField(max_length=50,blank =True,null = True)
    compliance_name =  models.CharField(max_length=50,blank =True,null = True)
    date = models.DateField(blank=True, null=True)
    relate_business_process = models.CharField(max_length=50,blank =True,null = True)
    relate_document =  models.TextField(blank=True,null=True)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.compliance_name
    
class LegalRequirements(models.Model):
    legal_no = models.CharField(max_length=50,blank =True,null = True)
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    attach_document = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    rivision = models.CharField(max_length=50,blank =True,null = True)
    legal_name =  models.CharField(max_length=50,blank =True,null = True)
    date = models.DateField(blank=True, null=True)
    related_record_format =  models.CharField(max_length=50,blank =True,null = True)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.legal_name
    

class ComplianceEvaluation(models.Model):
    compliance_no = models.ForeignKey(
        Compliance, on_delete=models.SET_NULL, null=True, related_name="compliance_evaluations"
    )
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_compliance_evaluations"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_compliance_evaluations"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_compliance_evaluations"
    )
    date = models.DateField(blank=True, null=True)
    relate_document = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    complaice_name = models.CharField(max_length=50, blank=True, null=True)
    compliance_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Legal', 'Legal'),
            ('Business', 'Business'),
            ('Client', 'Client'),
            ('Process/Specification', 'Process/Specification')
        ]
    )
    rivision = models.CharField(max_length=50, blank=True, null=True)
    attach_document = models.FileField(
        storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True
    )
    publish = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.complaice_name
    

class ManagementChange(models.Model):
    moc_no = models.CharField(max_length=50, blank=True, null=True)
    moc_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Manual/Procedure', 'Manual/Procedure'),
            ('Guideline/Policy', 'Guideline/Policy'),
            ('Specification/Standards', 'Specification/Standards'),
            ('Facility/Equipment', 'Facility/Equipment'),
            ('System/Process', 'System/Process'),
        ]
    )

    attach_document = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    purpose_of_chnage = models.CharField(max_length=50, blank=True, null=True)
    potential_cosequences =models.CharField(max_length=50, blank=True, null=True)
    moc_remarks = models.CharField(max_length=50, blank=True, null=True)
    moc_title =models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    related_record_format = models.CharField(max_length=50, blank=True, null=True)
    resources_required = models.CharField(max_length=50, blank=True, null=True)
    impact_on_process = models.CharField(max_length=50, blank=True, null=True)
    rivision =models.CharField(max_length=50, blank=True, null=True)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.moc_title
    

class Sustainability(models.Model):
    sustainability_no = models.ForeignKey(
        Compliance, on_delete=models.SET_NULL, null=True, related_name="sustainability"
    )
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_sustainability"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_sustainability"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_sustainability"
    )
    date = models.DateField(blank=True, null=True)
    relate_document = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    sustainability_name = models.CharField(max_length=50, blank=True, null=True)
    sustainability_type =  models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    attach_document = models.FileField(
        storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True
    )
    publish = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.sustainability_name
    

class ProcessActivity(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "No Title Provided"
    

class EnvironmentalAspect(models.Model):
    aspect_source = models.CharField(max_length=50, blank=True, null=True)
    aspect = models.CharField(max_length=50, blank=True, null=True)
    process_activity = models.ForeignKey(ProcessActivity, on_delete=models.SET_NULL, null=True )
    description =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_aspect"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_aspect"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_aspect"
    )
    level_of_impact = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Significant', 'Significant'),
            ('Non Significant', 'Non Significant'),
    
        ]
    )
    aspect_name = models.CharField(max_length=50, blank=True, null=True)
    legal_requirement = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    
    def __str__(self):
        return self.aspect_name
    


class EnvironmentalImpact(models.Model):
    impact_assessment = models.CharField(max_length=50, blank=True, null=True)
    related_record = models.CharField(max_length=50, blank=True, null=True)   
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_impact"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_impact"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_impact"
    )
  
    assessment_name = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    attach_document = models.FileField(
        storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    send_notification = models.BooleanField(default=False)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.impact_assessment
    


class RootCause(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title or "No Title Provided" 
    

class EnvironmentalIncidents(models.Model):
    source = models.CharField(max_length=50, blank=True, null=True)
    incident = models.CharField(max_length=50, blank=True, null=True)
    root_cause = models.ForeignKey(RootCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted')        
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    reported_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_incidents"
    )
    action =  models.TextField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.source  


class EnvironmentalWaste(models.Model):
    wmp = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_waste"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_waste"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_waste"
    )
    originator = models.CharField(max_length=50, blank=True, null=True)
    waste_type = models.CharField(max_length=50, blank=True, null=True)
    waste_quantity = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    waste_handling = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Company', 'Company'),
            ('Client', 'Client'),
            ('Contractor','Contractor'),
            ('Third Party/Others','Third Party/Others')
  
        ]
    )
    waste_category = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Hazardous', 'Hazardous'),
            ('Non Hazardous', 'Non Hazardous'),  
        ]
    )
    waste_minimization = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Reuse', 'Reuse'),
            ('Recycle', 'Recycle'),
            ('Recovery','Recovery'),
            ('Disposal','Disposal'),
            ('Non Disposable','Non Disposable'),
        ]
    )
    responsible_party = models.CharField(max_length=50, blank=True, null=True)
    legal_requirement = models.CharField(max_length=50, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.wmp  
    
class ProcessHealth(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title  
    
class HealthSafety(models.Model):
    hazard_source = models.CharField(max_length=50, blank=True, null=True)
    hazard = models.CharField(max_length=50, blank=True, null=True)
    process_activity = models.ForeignKey(ProcessHealth, on_delete=models.SET_NULL, null=True )
    description =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_hazard"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_hazard"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_hazard"
    )
    level_of_risk = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('High', 'High'),
            ('Medium', 'Medium'),
            ('Low','Low')
    
        ]
    )
    hazard_name = models.CharField(max_length=50, blank=True, null=True)
    legal_requirement = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    
    
    def __str__(self):
        return self.hazard_name
    
class RiskAssessment(models.Model):
    assessment_no = models.CharField(max_length=50, blank=True, null=True)
    related_record_format = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_assessment"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_assessment"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_assessment"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    assessment_name = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)   
    rivision = models.CharField(max_length=50, blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.assessment_name

class HealthRootCause(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title  
    
class HealthIncidents(models.Model):
    source = models.CharField(max_length=50, blank=True, null=True)
    incident = models.CharField(max_length=50, blank=True, null=True)
    root_cause = models.ForeignKey(HealthRootCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted')        
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    reported_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_health_incidents"
    )
    action =  models.TextField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.source  
    

class BusinessRisk(models.Model):
    risk_no = models.CharField(max_length=50, blank=True, null=True)
    business_process = models.CharField(max_length=50, blank=True, null=True)
 
    remark =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_risk"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_risk"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_risk"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    level_of_risk = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('High', 'High'),
            ('Medium', 'Medium'),
            ('Low','Low')
    
        ]
    )
    business_name = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)   
    send_notification = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.business_name
    

class ReviewType(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title  

class EnergyReview(models.Model):
    review_no = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    review_type = models.ForeignKey(ReviewType, on_delete=models.SET_NULL, null=True )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)    
    date  = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    energy_name = models.CharField(max_length=50, blank=True, null=True) 
    relate_business_process = models.CharField(max_length=20, blank=True, null=True )
    relate_document_process = models.CharField(max_length=20, blank=True, null=True )
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.energy_name   
    
class BaselineReview(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title or "No Title Provided"
    
class Baseline(models.Model):
    basline_title = models.CharField(max_length=50, blank=True, null=True)
    established_basline = models.CharField(max_length=50, blank=True, null=True)
    remarks =  models.TextField(blank=True, null=True)
    energy_review = models.ForeignKey(BaselineReview, on_delete=models.SET_NULL, null=True )
    date  = models.DateField(blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_baseline"
    )

    def __str__(self):
      return self.basline_title or "No Title Provided"


class Enpis(models.Model):
    enpi = models.CharField(max_length=50, blank=True, null=True)
    baseline = models.ForeignKey(
        Baseline, on_delete=models.CASCADE, null=True, related_name="enpis"
    )

    def __str__(self):
        return f"Additional enpi for {self.baseline.basline_title if self.baseline else 'No Baseline'}"



class EnergySource(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title or "No Title Provided"
    
class SignificantEnergy(models.Model):
    significant = models.CharField(max_length=50, blank=True, null=True)
    source_type = models.ForeignKey(EnergySource, on_delete=models.SET_NULL, null=True )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)    
    consumption =  models.CharField(max_length=50, blank=True, null=True)
    consequences =  models.CharField(max_length=50, blank=True, null=True)
    remarks =  models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    facility = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    impact = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    publish = models.BooleanField(default=False)


    def __str__(self):
        return self.significant or "No Title Provided"


class EnergyImprovement(models.Model):
    eio = models.CharField(max_length=50, blank=True, null=True)
    target = models.CharField(max_length=50, blank=True, null=True)
    results =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('On Going', 'On Going'),
        ('Achieved', 'Achieved'),
        ('Not Achieved', 'Not Achieved'),
        ('Modified', 'Modified'),       
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Going')
    eio_title = models.CharField(max_length=50, blank=True, null=True)
    associated_objective = models.CharField(max_length=50, blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_energy_improvements"
    )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)

    def __str__(self):
        return self.eio or "No Title Provided"
    

class EnergyAction(models.Model):
    action_plan =  models.CharField(max_length=50, blank=True, null=True)
    associative_objective =  models.CharField(max_length=50, blank=True, null=True)
    legal_requirements =  models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    energy_improvements = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    means = models.CharField(max_length=50, blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_energy_action_plan"
    )
    statement = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.action_plan or "No Title Provided"
    
class Program(models.Model):
    Program = models.CharField(max_length=50, blank=True, null=True)
    energy_action = models.ForeignKey(
    EnergyAction, on_delete=models.CASCADE, null=True, related_name="programs"
)

    def __str__(self):
        return f"Additional program for {self.energy_action.action_plan if self.energy_action else 'No Baseline'}"
    

class CorrectionCause(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title or "No Title Provided"

class CorrectiveAction(models.Model): 
    source = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Audit', 'Audit'),
            ('Customer', 'Customer'),
            ('Internal','Internal'),
            ('Supplier','Supplier')  
        ]
    )
    action = models.CharField(max_length=255,blank=True, null=True)
    root_cause = models.ForeignKey(CorrectionCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted')        
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    title = models.CharField(max_length=255,blank=True, null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    action_corrections =  models.TextField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title or "No Title Provided"
    
class PreventiveAction(models.Model): 
    title =  models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed')
            
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    action =  models.TextField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.title or "No Title Provided"


class Objectives(models.Model): 
    objective = models.CharField(max_length=255,blank=True, null=True)
    performance = models.TextField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    reminder_date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('On Going', 'On Going'),
        ('Achieved', 'Achieved'),
        ('Not Achieved', 'Not Achieved'),
        ('Modified', 'Modified'),       
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Going')
    indicator = models.CharField(max_length=255,blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_planobjectives")
    

    def __str__(self):
        return self.objective or "No Title Provided"


class TargetsP(models.Model):
    target =  models.CharField(max_length=50, blank=True, null=True)
    associative_objective =  models.CharField(max_length=50, blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    reminder_date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('On Going', 'On Going'),
        ('Achieved', 'Achieved'),
        ('Not Achieved', 'Not Achieved'),
        ('Modified', 'Modified'),       
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Going')
    results = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)    
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_targets"
    )
    

    def __str__(self):
        return self.target or "No Title Provided"
    
class TProgram(models.Model):
    Program = models.CharField(max_length=50, blank=True, null=True)
    targets = models.ForeignKey(
    TargetsP, on_delete=models.CASCADE, null=True, related_name="programs"
)

    def __str__(self):
        return f"Additional program for {self.targets.target if self.targets else 'No Targets'}"


class ConformityCause(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title

class Conformity(models.Model):
    source = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Audit', 'Audit'),
            ('Customer', 'Customer'),
            ('Internal','Internal'),
            ('Supplier','Supplier')  
        ]
    )
    ncr = models.CharField(max_length=50, blank=True, null=True)
    root_cause = models.ForeignKey(ConformityCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    Status_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted','Deleted')
        
    ]
    status = models.CharField(max_length=20, choices=Status_CHOICES, default='Pending')
    title = models.CharField(max_length=50, blank=True, null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    resolution = models.TextField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Manual(models.Model):
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_manual"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_manual"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_manual"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Procedure(models.Model):
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_procedure"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_procedure"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_procedure"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    relate_format = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class RecordFormat(models.Model):
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_record"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_record"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checkedrecord"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    retention = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title
=======
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
>>>>>>> ac5ee3b06f8168cf659365588c193e4a1d2ef6e9
