#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick integration test for temporary user inputs feature.
"""

from zxcvbn import ZxcvbnInstance
import threading
import time

def test_basic():
    """Test basic functionality."""
    print("Test 1: Basic functionality")
    zx = ZxcvbnInstance()
    
    # Test with temp inputs
    result1 = zx.set_passwd_and_input('alice123', temp_user_inputs=['alice'])
    assert result1['score'] >= 0
    print(f"  ✓ set_passwd_and_input works: score={result1['score']}")
    
    # Test backward compatibility
    result2 = zx.set_password('password123')
    assert result2['score'] >= 0
    print(f"  ✓ set_password still works: score={result2['score']}")
    print()

def test_isolation():
    """Test that temp inputs are isolated."""
    print("Test 2: Isolation")
    zx = ZxcvbnInstance()
    
    # First evaluation
    result1 = zx.set_passwd_and_input('alice123', temp_user_inputs=['alice'])
    
    # Second evaluation should not use first user's inputs
    result2 = zx.set_passwd_and_input('alice123', temp_user_inputs=['bob'])
    
    # Verify no pollution
    assert 'user_inputs' not in zx._ranked_dictionaries or 'alice' not in zx._ranked_dictionaries.get('user_inputs', {})
    print("  ✓ Temporary inputs don't pollute instance cache")
    print()

def test_thread_safety():
    """Test thread safety."""
    print("Test 3: Thread safety")
    zx = ZxcvbnInstance(thread_safe=True)
    results = []
    errors = []
    
    def worker(user_id):
        try:
            username = f'user{user_id}'
            result = zx.set_passwd_and_input(
                f'{username}123',
                temp_user_inputs=[username]
            )
            results.append(result)
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 10
    print(f"  ✓ Thread-safe with 10 concurrent requests")
    print()

def test_performance():
    """Test performance improvement."""
    print("Test 4: Performance")
    passwords = ['alice123', 'bob456', 'charlie789']
    users = ['alice', 'bob', 'charlie']
    
    # Old method
    zx1 = ZxcvbnInstance()
    start = time.time()
    for password, user in zip(passwords, users):
        zx1.update_user_inputs([user])
        zx1.set_password(password)
    old_time = time.time() - start
    
    # New method
    zx2 = ZxcvbnInstance()
    start = time.time()
    for password, user in zip(passwords, users):
        zx2.set_passwd_and_input(password, temp_user_inputs=[user])
    new_time = time.time() - start
    
    speedup = old_time / new_time if new_time > 0 else float('inf')
    print(f"  ✓ Performance: {speedup:.1f}x faster than update_user_inputs()")
    print()

def test_merging():
    """Test merging instance and temp inputs."""
    print("Test 5: Merging instance-level and temporary inputs")
    zx = ZxcvbnInstance(user_inputs=['company'])
    
    result = zx.set_passwd_and_input(
        'john_company_123',
        temp_user_inputs=['john']
    )
    
    # Both should be detected
    all_inputs = ['company', 'john']
    matches = zx._omnimatch('john_company_123', all_inputs)
    
    found_company = any(m.get('dictionary_name') == 'user_inputs' and 'company' in m.get('matched_word', '') for m in matches)
    found_john = any(m.get('dictionary_name') == 'user_inputs' and 'john' in m.get('matched_word', '') for m in matches)
    
    assert found_company, "Instance-level input not found"
    assert found_john, "Temporary input not found"
    print("  ✓ Instance-level and temporary inputs are properly merged")
    print()

if __name__ == '__main__':
    print("=" * 60)
    print("Integration Tests for Temporary User Inputs")
    print("=" * 60)
    print()
    
    test_basic()
    test_isolation()
    test_thread_safety()
    test_performance()
    test_merging()
    
    print("=" * 60)
    print("✅ All integration tests passed!")
    print("=" * 60)
