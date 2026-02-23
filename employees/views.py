import time
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import get_employees_standard, get_employees_fast
import json
# Create your views here.




class BenchmarkingView(APIView):
    
    def get(self, request, dept_id):
        # 1. Benchmark Standard Path
        start_std = time.perf_counter()
        data_std = get_employees_standard(dept_id)
        end_std = time.perf_counter()
        
        # 2. Benchmark Fast Path
        start_fast = time.perf_counter()
        data_fast = get_employees_fast(dept_id)
        
        end_fast = time.perf_counter()

        return Response({
            "standard_path_ms": (end_std - start_std) * 1000,
            "fast_path_ms": (end_fast - start_fast) * 1000,
            "speed_increase_percent": round(((end_std - start_std) / (end_fast - start_fast) - 1) * 100, 2),
            "row_count": len(data_std)
           
        })

class test(APIView):
   
   def get(self,request):
       return Response({
           "message":"working"
           
       })