import sys
import time
sys.path.insert(0, '.')
from zxcvbn import zxcvbn, ZxcvbnInstance

# Performance comparison test
passwords = ['password123', 'hello123', 'test456', 'admin123', 'user789','jianlegui8822']*2

# Test original function
start_time = time.time()
for password in passwords:
    result = zxcvbn(password)
original_time = time.time() - start_time

# Test ZxcvbnInstance
zx = ZxcvbnInstance()
start_time = time.time()
for password in passwords:
    result = zx.set_password(password)
instance_time = time.time() - start_time

print(f'Original function time: {original_time:.4f} seconds')
print(f'ZxcvbnInstance time: {instance_time:.4f} seconds')
print(f'Speedup: {original_time/instance_time:.2f}x faster')
print('Performance test completed successfully!')

# Test original function
start_time = time.time()
for password in passwords:
    result = zxcvbn(password,lang='zh')
original_time = time.time() - start_time

# Test ZxcvbnInstance
zx = ZxcvbnInstance(lang='zh',thread_safe=True)
start_time = time.time()
for password in passwords:
    result = zx.set_password(password)
instance_time = time.time() - start_time

print(f'Original function time with lang and thread_safe: {original_time:.4f} seconds')
print(f'ZxcvbnInstance time with lang and thread_safe: {instance_time:.4f} seconds')
print(f'Speedup: {original_time/instance_time:.2f}x faster')
print('Performance test completed successfully!')