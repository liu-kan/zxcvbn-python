#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of temporary user inputs with ZxcvbnInstance.

This example demonstrates:
1. Using temporary user inputs for different users in a thread pool scenario
2. Comparing set_password() and set_passwd_and_input() methods
3. Merging instance-level and temporary user inputs
4. Thread-safe operations with different user inputs
"""

from zxcvbn import ZxcvbnInstance
import threading
import time


def basic_temp_inputs_example():
    """Basic example of using temporary user inputs."""
    print("=== Basic Temporary User Inputs Example ===")
    
    # Create a zxcvbn instance without any user inputs
    zx = ZxcvbnInstance(lang='en', thread_safe=True)
    
    # Evaluate password for user Alice
    result_alice = zx.set_passwd_and_input(
        'alice123',
        temp_user_inputs=['alice', 'alice@example.com']
    )
    print(f"Alice's password 'alice123': Score = {result_alice['score']}/4")
    print(f"  Warning: {result_alice['feedback']['warning']}")
    
    # Evaluate password for user Bob - Alice's inputs are not used
    result_bob = zx.set_passwd_and_input(
        'bob456',
        temp_user_inputs=['bob', 'robert']
    )
    print(f"Bob's password 'bob456': Score = {result_bob['score']}/4")
    print(f"  Warning: {result_bob['feedback']['warning']}")
    print()


def thread_pool_simulation():
    """Simulate a thread pool handling requests from different users."""
    print("=== Thread Pool Simulation ===")
    
    # Create a shared instance for the thread pool
    zx = ZxcvbnInstance(lang='en', thread_safe=True)
    
    results = []
    
    def process_user_request(user_id, username, password):
        """Simulate processing a password evaluation request for a user."""
        user_inputs = [username, f'{username}@company.com']
        result = zx.set_passwd_and_input(password, temp_user_inputs=user_inputs)
        results.append({
            'user_id': user_id,
            'username': username,
            'password': password,
            'score': result['score'],
            'warning': result['feedback']['warning']
        })
        print(f"  Thread {user_id}: User '{username}' password evaluated, score = {result['score']}/4")
    
    # Simulate concurrent requests from different users
    threads = []
    users = [
        (1, 'alice', 'alice_secret123'),
        (2, 'bob', 'bob_password456'),
        (3, 'charlie', 'charlie789!'),
        (4, 'david', 'david_pass'),
        (5, 'emma', 'emma2024@'),
    ]
    
    print("Starting concurrent password evaluations...")
    for user_id, username, password in users:
        t = threading.Thread(target=process_user_request, args=(user_id, username, password))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print(f"All {len(results)} requests processed successfully!")
    print()


def merging_instance_and_temp_inputs():
    """Example of merging instance-level and temporary user inputs."""
    print("=== Merging Instance-Level and Temporary User Inputs ===")
    
    # Create instance with common user inputs (e.g., company name)
    zx = ZxcvbnInstance(
        user_inputs=['company', 'acmecorp', '2024'],
        lang='en',
        thread_safe=True
    )
    
    # Evaluate password for user John
    # Both company-level and user-specific inputs will be used
    result_john = zx.set_passwd_and_input(
        'john_acmecorp_123',
        temp_user_inputs=['john', 'john.doe']
    )
    print(f"John's password 'john_acmecorp_123': Score = {result_john['score']}/4")
    print(f"  (Uses both company inputs ['company', 'acmecorp', '2024']")
    print(f"   and John's inputs ['john', 'john.doe'])")
    
    # Evaluate password for user Jane
    # Company inputs are reused, but John's inputs are not
    result_jane = zx.set_passwd_and_input(
        'jane_company_456',
        temp_user_inputs=['jane', 'jane.smith']
    )
    print(f"Jane's password 'jane_company_456': Score = {result_jane['score']}/4")
    print(f"  (Uses company inputs but not John's inputs)")
    print()


def backward_compatibility_example():
    """Demonstrate backward compatibility with set_password()."""
    print("=== Backward Compatibility Example ===")
    
    zx = ZxcvbnInstance(user_inputs=['common'], lang='en')
    
    # Old method still works
    result1 = zx.set_password('password123')
    print(f"Using set_password(): Score = {result1['score']}/4")
    
    # New method without temp inputs - equivalent to old method
    result2 = zx.set_passwd_and_input('password123', temp_user_inputs=None)
    print(f"Using set_passwd_and_input(temp_user_inputs=None): Score = {result2['score']}/4")
    
    # New method with temp inputs
    result3 = zx.set_passwd_and_input('password123', temp_user_inputs=['temp'])
    print(f"Using set_passwd_and_input(temp_user_inputs=['temp']): Score = {result3['score']}/4")
    
    print("\nNote: set_password() is now a wrapper that calls set_passwd_and_input()")
    print()


def performance_comparison():
    """Compare performance of different approaches."""
    print("=== Performance Comparison ===")
    
    passwords = ['alice123', 'bob456', 'charlie789', 'david000', 'emma2024']
    user_names = ['alice', 'bob', 'charlie', 'david', 'emma']
    
    # Method 1: Using update_user_inputs (old approach - expensive)
    print("Method 1: Using update_user_inputs() for each user (expensive)")
    zx1 = ZxcvbnInstance(thread_safe=False)
    start = time.time()
    for password, username in zip(passwords, user_names):
        zx1.update_user_inputs([username])
        result = zx1.set_password(password)
    method1_time = time.time() - start
    print(f"  Time: {method1_time:.4f} seconds")
    
    # Method 2: Using temp_user_inputs (new approach - efficient)
    print("Method 2: Using temp_user_inputs with set_passwd_and_input() (efficient)")
    zx2 = ZxcvbnInstance(thread_safe=False)
    start = time.time()
    for password, username in zip(passwords, user_names):
        result = zx2.set_passwd_and_input(password, temp_user_inputs=[username])
    method2_time = time.time() - start
    print(f"  Time: {method2_time:.4f} seconds")
    
    speedup = method1_time / method2_time if method2_time > 0 else float('inf')
    print(f"\nSpeedup: {speedup:.2f}x faster")
    print(f"The new approach avoids expensive dictionary rebuilding!")
    print()


def isolation_demonstration():
    """Demonstrate that temporary inputs are truly isolated."""
    print("=== Isolation Demonstration ===")
    
    zx = ZxcvbnInstance(thread_safe=True)
    
    # Evaluate for user Alice
    result1 = zx.set_passwd_and_input('alice123', temp_user_inputs=['alice'])
    print(f"Evaluation 1 (with 'alice'): Score = {result1['score']}/4")
    
    # Evaluate for user Bob - Alice's input should not affect this
    result2 = zx.set_passwd_and_input('alice123', temp_user_inputs=['bob'])
    print(f"Evaluation 2 (with 'bob' on same password 'alice123'): Score = {result2['score']}/4")
    
    # Same password, no temp inputs
    result3 = zx.set_password('alice123')
    print(f"Evaluation 3 (no temp inputs): Score = {result3['score']}/4")
    
    print("\nNotice: The scores are different because different user inputs are used.")
    print("This demonstrates complete isolation between evaluations!")
    print()


if __name__ == "__main__":
    print("ZxcvbnInstance Temporary User Inputs Examples")
    print("=" * 60)
    print()
    
    basic_temp_inputs_example()
    thread_pool_simulation()
    merging_instance_and_temp_inputs()
    backward_compatibility_example()
    performance_comparison()
    isolation_demonstration()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("\nKey Takeaways:")
    print("1. Use set_passwd_and_input() for per-request user inputs")
    print("2. Use set_password() for simple cases (backward compatible)")
    print("3. Temporary inputs don't pollute the instance cache")
    print("4. Thread-safe for concurrent requests with different inputs")
    print("5. Much faster than repeatedly calling update_user_inputs()")
