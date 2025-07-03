#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of the improved ZxcvbnInstance class.

This example demonstrates:
1. Creating a persistent zxcvbn instance
2. Evaluating passwords with cached dictionaries and translations
3. Modifying passwords and re-evaluating
4. Thread-safe operations
5. Language switching
6. User input management
"""

from zxcvbn import ZxcvbnInstance
import threading
import time


def basic_usage_example():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Create a zxcvbn instance with Chinese language support
    zx = ZxcvbnInstance(lang='zh_Hans', thread_safe=True)
    
    # Evaluate a password
    result = zx.set_password("password123")
    print(f"Password: {zx.get_password()}")
    print(f"Score: {result['score']}/4")
    print(f"Warning: {result['feedback']['warning']}")
    print(f"Suggestions: {result['feedback']['suggestions']}")
    print()
    
    # Change password and re-evaluate
    result = zx.set_password("MyStr0ng!P@ssw0rd")
    print(f"New password: {zx.get_password()}")
    print(f"Score: {result['score']}/4")
    print(f"Warning: {result['feedback']['warning']}")
    print(f"Suggestions: {result['feedback']['suggestions']}")
    print()


def user_inputs_example():
    """Example with user inputs."""
    print("=== User Inputs Example ===")
    
    # Create instance with user-specific inputs
    user_data = ['john', 'doe', 'acme', 'company', '1990']
    zx = ZxcvbnInstance(user_inputs=user_data, lang='en')
    
    # Test password containing user data
    result = zx.set_password("john1990")
    print(f"Password with user data: {zx.get_password()}")
    print(f"Score: {result['score']}/4")
    print(f"Warning: {result['feedback']['warning']}")
    print()
    
    # Update user inputs
    zx.update_user_inputs(['alice', 'wonderland', '2000'])
    result = zx.get_result()  # Get re-evaluated result
    print(f"After updating user inputs:")
    print(f"Score: {result['score']}/4")
    print()


def language_switching_example():
    """Example of language switching."""
    print("=== Language Switching Example ===")
    
    zx = ZxcvbnInstance(lang='en')
    
    # Evaluate in English
    zx.set_password("musculature")
    result = zx.get_result()
    print(f"English feedback: {result['feedback']['warning']}")
    
    # Switch to Chinese
    zx.set_language('zh_Hans')
    result = zx.get_result()
    print(f"Chinese feedback: {result['feedback']['warning']}")
    
    # Switch back to English
    zx.set_language('en')
    result = zx.get_result()
    print(f"English feedback again: {result['feedback']['warning']}")
    print()


def thread_safety_example():
    """Example of thread-safe operations."""
    print("=== Thread Safety Example ===")
    
    # Create a thread-safe instance
    zx = ZxcvbnInstance(thread_safe=True, lang='en')
    results = []
    
    def worker(thread_id):
        """Worker function for threading test."""
        password = f"password{thread_id}"
        result = zx.set_password(password)
        results.append((thread_id, result['score']))
        print(f"Thread {thread_id}: {password} -> Score: {result['score']}")
    
    # Create and start multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print(f"All {len(results)} threads completed successfully")
    print()


def performance_comparison():
    """Compare performance between function and instance approaches."""
    print("=== Performance Comparison ===")
    
    from zxcvbn import zxcvbn  # Original function
    
    passwords = ["password123", "MyStr0ng!P@ssw0rd", "weak", "complex!Password123"]
    
    # Test original function (reloads dictionaries each time)
    start_time = time.time()
    for password in passwords:
        result = zxcvbn(password, lang='zh_Hans')
    function_time = time.time() - start_time
    
    # Test instance approach (cached dictionaries)
    zx = ZxcvbnInstance(lang='zh_Hans')
    start_time = time.time()
    for password in passwords:
        result = zx.set_password(password)
    instance_time = time.time() - start_time
    
    print(f"Original function time: {function_time:.4f} seconds")
    print(f"Instance approach time: {instance_time:.4f} seconds")
    print(f"Speedup: {function_time/instance_time:.2f}x faster")
    print()


def advanced_usage_example():
    """Advanced usage with multiple instances."""
    print("=== Advanced Usage Example ===")
    
    # Create different instances for different contexts
    admin_zx = ZxcvbnInstance(
        user_inputs=['admin', 'administrator', 'root'],
        lang='en',
        max_length=50
    )
    
    user_zx = ZxcvbnInstance(
        user_inputs=['user', 'guest'],
        lang='zh_Hans',
        max_length=100
    )
    
    # Test admin password
    admin_result = admin_zx.set_password("admin123")
    print(f"Admin password evaluation:")
    print(f"  Score: {admin_result['score']}/4")
    print(f"  Warning: {admin_result['feedback']['warning']}")
    
    # Test user password
    user_result = user_zx.set_password("user123")
    print(f"User password evaluation:")
    print(f"  Score: {user_result['score']}/4")
    print(f"  Warning: {user_result['feedback']['warning']}")
    print()


if __name__ == "__main__":
    print("ZxcvbnInstance Usage Examples")
    print("=" * 50)
    print()
    
    basic_usage_example()
    user_inputs_example()
    language_switching_example()
    thread_safety_example()
    performance_comparison()
    advanced_usage_example()
    
    print("All examples completed successfully!")
