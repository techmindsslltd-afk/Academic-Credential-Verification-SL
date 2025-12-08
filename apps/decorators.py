from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
import sweetify




def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator

def unauthenticated_user(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def unauthenticated_user6666(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.is_authenticated:
			return redirect('authentication:login')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func


def bank_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.bank_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def feeStructure_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.feeStructure_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func


def tuitionfee_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.tuitionfee_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
           
def fee_exception_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.fee_exception_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def lesson_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.lesson_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def users_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def staff_bio_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.staff_bio_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def student_bio_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.student_bio_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
    

def lecturer_bio_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.lecturer_bio_data_crud :
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def campus_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.campus_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def faculty_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.faculty_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def department_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.department_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def course_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.course_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
def unit_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.unit_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

      	    
def session_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.session_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def level_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.level_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func


def year_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.year_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func



def populate_grades(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.populate_grades:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

	
def class_rooms_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.class_rooms_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func


def modules_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.modules_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def can_produceTranscript(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.produceTranscript:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def exams_timetable_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.exams_timetable_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func


def class_timetable_data_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.class_timetable_data_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func





def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):

			group = None
			if request.user.groups.exists():
				group = request.user.groups.all()[0].name

			if group in allowed_roles:
				return view_func(request, *args, **kwargs)
			else:
				return redirect('dashboard')
		return wrapper_func
	return decorator

def admin_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if group == 'customer':
			return redirect('user-page')

		if group == 'admin':
			return view_func(request, *args, **kwargs)

	return wrapper_function

def lesson_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.lesson_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def staff_bio_data_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.staff_bio_data_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                         


def student_bio_data_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.student_bio_data_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func 

def lecturer_bio_data_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.lecturer_bio_data_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func 

def users_hou_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_hou_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func 

def users_staff_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_staff_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func 
                        

def users_dean_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_dean_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func 

def users_dean_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_dean_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func 

 
def users_hod_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_hod_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                        
                        
  
def users_ictstaff_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_ictstaff_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                       
                       
    
def users_lecturer_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_lecturer_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                      
                        
    
def users_student_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_student_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                      
                                       
     
def users_view(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_view:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                      
       
def users_student_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_student_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                                              
                       
def users_lecturer_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_lecturer_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                                              
                        
def users_ictstaff_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_ictstaff_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                                              
                         
def users_hod_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_hod_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                             
                          
def users_dean_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_dean_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func  

def users_staff_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_staff_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func   

def users_hou_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_hou_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func  


def users_hou_crud(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not request.user.users_hou_crud:
			return redirect('dashboard')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func                            
                         
