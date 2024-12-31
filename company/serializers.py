from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password


 
 
 

 
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)   
    confirm_email = serializers.EmailField(write_only=True)   

    class Meta:
        model = Users
        fields = '__all__'  

    def validate(self, data):
        
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")

       
        if data.get('email') != data.get('confirm_email'):
            raise serializers.ValidationError("Email addresses do not match.")

        
        data['password'] = make_password(data['password'])

        
        data.pop('confirm_password', None)
        data.pop('confirm_email', None)

        return data
    
    
class DocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocumentation
        fields = '__all__'  

class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'  
        
class EmployeeEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEvaluation
        fields = '__all__'
        
class EmployeeSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSurvey
        fields = '__all__'

class AwarenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwarenessTraining
        fields = '__all__'
        
class AgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agenda
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'
        
class CauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cause
        fields = '__all__'

class InternalProblemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProblems
        fields = '__all__'
        
class CarNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarNumber
        fields = '__all__' 

class AuditSerializer(serializers.ModelSerializer):
    audit_from_internal_name = serializers.CharField(source='audit_from_internal.username', read_only=True)  

    class Meta:
        model = Audit
        fields = '__all__' 
        
class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = '__all__'
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'