from rest_framework import serializers   
from apps.accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    def get_groups(self, obj):
        return obj.groups.values_list('name', flat=True)
            
    def full_name(self, obj):
        return '%s %s %s' % (obj.name, obj.other_name, obj.surname)

    def get_short_name(self, obj):
        return '%s  %s' % (obj.name,  obj.surname)
    def get_is_staff(self, obj):
        if obj.is_admin:
            return True
        return obj.is_staff

    def get_is_admin(self, obj):
        return obj.is_admin



    class Meta:
        model = User
        fields = [
            'email',
            'passwaord',
            'prefix' , 
            'name', 
            'other_name' 
            'surname', 
            'gender' , 
            'dob', 
            'file' ,
            'telephone', 
            'data_color' ,
            'data_background_color' ,
            'data_image', 
            'data_color_general',
            'is_active', 
            'is_staff', 
            'is_admin' ,
            'is_block',
            'last_activity',
            'change_views',
            'lab_test_crud', 
            'lab_crud',  
            'lab_result_crud' ,
            'diagnosis_crud' ,
            'lab_test_view' , 
            'lab_view',  
            'lab_result_view' 
            'diagnosis_view', 
            'drug_type_crud',  
            'drug_crud' , 
            'drug_prescrition_crud' ,
            'drug_type_view' , 
            'drug_view',  
            'drug_prescrition_view' ,
            'patient_crud', 
            'patient_view' ,
            'staff_crud' ,
            'staff_view' ,
            'staff_payroll_view', 
            'staff_payroll_crud', 
            'user_crud', 
            'user_view', 
            'vital_view', 
            'vital_crud', 
            'view_all_appointment' ,
            'doctor_view',
            'finance_view' ,
            'finance_crud', 
            'phamarcy_view', 
            'manage_phamarcy_view', 
            'settings_view', 
            'appointment_crud' ,
            'appointment_view' ,
            'encounter_crud' ,
            'encounter_view' ,
            'management_plan_crud', 
            'management_plan_crud', 
            'Plan_Treatment', 
            'Embryologist' ,
            'OB_GYN' ,
            'lab_draw_blood', 
            'Receptionist', 
            'user_signature', 
            'recordOwner', 
            'timestamp', 
            'chat_volume' ,
            'groups',
            ]

