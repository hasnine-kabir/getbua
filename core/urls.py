from django.urls import path
from . import views

urlpatterns = [
    path('',              views.home,               name='home'),
    path('register/',     views.register_view,      name='register'),
    path('login/',        views.login_view,          name='login'),
    path('logout/',       views.logout_view,         name='logout'),
    path('profile/',      views.profile_view,        name='profile'),
    path('profile/edit/', views.profile_edit,        name='profile_edit'),
    path('reset-password/',views.custom_password_reset,name='custom_password_reset'),
    path('training/',     views.training_page,       name='training'),

    path('workers/',          views.worker_list,    name='worker_list'),
    path('workers/<int:pk>/', views.worker_detail,  name='worker_detail'),
    path('short-term/',       views.short_term_list,name='short_term_list'),

    path('hire/<int:worker_id>/',   views.hire_worker,         name='hire_worker'),
    path('my-hires/',               views.my_hires,            name='my_hires'),
    path('contract/<int:hire_id>/', views.view_contract,       name='view_contract'),
    path('rate/<int:hire_id>/',     views.submit_rating,       name='submit_rating'),
    path('replace/<int:hire_id>/',  views.request_replacement, name='request_replacement'),

    path('salary/add/<int:hire_id>/',     views.add_salary_payment, name='add_salary_payment'),
    path('salary/history/<int:hire_id>/', views.salary_history,     name='salary_history'),

    path('dashboard/',                       views.admin_dashboard,    name='admin_dashboard'),
    path('dashboard/approve/<int:hire_id>/', views.approve_hire,       name='approve_hire'),
    path('dashboard/reject/<int:hire_id>/',  views.reject_hire,        name='reject_hire'),
    path('dashboard/resolve/<int:rep_id>/',  views.resolve_replacement,name='resolve_replacement'),
]