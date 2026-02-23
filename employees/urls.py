

from django.urls import path
from employees.views import BenchmarkingView,test



urlpatterns = [
    path('employees/<int:dept_id>/', BenchmarkingView.as_view(), name='benchmarking'),
    path('test/', test.as_view(), name='benchmarking'),    

]
