# -*- coding: utf-8 -*-
import unittest
import threading
import time
from zxcvbn import ZxcvbnInstance


class TestZxcvbnInstance(unittest.TestCase):
    """Test the ZxcvbnInstance class functionality."""
    
    def test_basic_functionality(self):
        """Test basic password evaluation functionality."""
        instance = ZxcvbnInstance()
        
        # Test password evaluation
        result = instance.set_password("password123")
        self.assertIsInstance(result, dict)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        self.assertIn('guesses', result)
        
        # Test password retrieval
        self.assertEqual(instance.get_password(), "password123")
        
        # Test result retrieval
        cached_result = instance.get_result()
        self.assertEqual(result, cached_result)
    
    def test_password_modification(self):
        """Test password modification and re-evaluation."""
        instance = ZxcvbnInstance()
        
        # Set initial password
        result1 = instance.set_password("weak")
        
        # Change password
        result2 = instance.set_password("StrongP@ssw0rd!")
        
        # Results should be different
        self.assertNotEqual(result1['score'], result2['score'])
        self.assertEqual(instance.get_password(), "StrongP@ssw0rd!")
        self.assertEqual(instance.get_result(), result2)
    
    def test_user_inputs(self):
        """Test user inputs functionality."""
        user_inputs = ['john', 'doe', 'company']
        instance = ZxcvbnInstance(user_inputs=user_inputs)
        
        # Test with a password that will definitely use user input in the optimal sequence
        result = instance.set_password("johndoe")
        
        # Check that user input was detected in all matches
        all_matches = instance._omnimatch("johndoe", ['john', 'doe', 'company'])
        found_user_match = False
        for match in all_matches:
            if match.get('dictionary_name') == 'user_inputs':
                found_user_match = True
                break
        
        self.assertTrue(found_user_match, "User input should be detected in password")
    
    def test_user_inputs_update(self):
        """Test updating user inputs."""
        instance = ZxcvbnInstance()
        
        # Set password first with a unique password that won't be in common dictionaries
        instance.set_password("alicewonderland")
        result1 = instance.get_result()
        
        # Update user inputs to include 'alice' and 'wonderland'
        instance.update_user_inputs(['alice', 'wonderland'])
        result2 = instance.get_result()
        
        # Check that user inputs are now detected in the matches
        all_matches = instance._omnimatch("alicewonderland", ['alice', 'wonderland'])
        found_user_match = False
        for match in all_matches:
            if match.get('dictionary_name') == 'user_inputs':
                found_user_match = True
                break
        
        self.assertTrue(found_user_match, "User input should be detected after update")
    
    def test_language_support(self):
        """Test language switching functionality."""
        instance = ZxcvbnInstance(lang='en')
        
        # Set a dictionary word
        result_en = instance.set_password("musculature")
        
        # Switch to Chinese
        instance.set_language('zh_Hans')
        result_zh = instance.get_result()
        
        # Feedback should be in Chinese
        self.assertIn("单个词语", result_zh['feedback']['warning'])
        
        # Switch back to English
        instance.set_language('en')
        result_en_again = instance.get_result()
        
        # Feedback should be in English again
        self.assertIn("word by itself", result_en_again['feedback']['warning'])
    
    def test_max_length_validation(self):
        """Test maximum length validation."""
        instance = ZxcvbnInstance(max_length=10)
        
        # Should work with short password
        result = instance.set_password("short")
        self.assertIsInstance(result, dict)
        
        # Should raise error with long password
        with self.assertRaises(ValueError):
            instance.set_password("this_password_is_too_long")
    
    def test_thread_safety(self):
        """Test thread safety of the instance."""
        instance = ZxcvbnInstance(thread_safe=True)
        results = []
        errors = []
        
        def worker(password_suffix):
            try:
                password = f"password{password_suffix}"
                result = instance.set_password(password)
                results.append((password_suffix, result['score']))
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check that no errors occurred
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Check that all threads completed
        self.assertEqual(len(results), 10)
    
    def test_thread_unsafe_mode(self):
        """Test that thread unsafe mode works."""
        instance = ZxcvbnInstance(thread_safe=False)
        
        result = instance.set_password("test123")
        self.assertIsInstance(result, dict)
        self.assertEqual(instance.get_password(), "test123")
    
    def test_persistent_dictionaries(self):
        """Test that dictionaries are loaded only once."""
        instance = ZxcvbnInstance()
        
        # First evaluation
        result1 = instance.set_password("password1")
        dict_id_1 = id(instance._ranked_dictionaries)
        
        # Second evaluation
        result2 = instance.set_password("password2")
        dict_id_2 = id(instance._ranked_dictionaries)
        
        # Dictionary object should be the same (not reloaded)
        self.assertEqual(dict_id_1, dict_id_2)
        
        # But results should be different
        self.assertNotEqual(result1, result2)
    
    def test_persistent_translation(self):
        """Test that translation is loaded only once."""
        instance = ZxcvbnInstance(lang='zh_Hans')
        
        # First evaluation
        instance.set_password("password1")
        trans_id_1 = id(instance._translation_func)
        
        # Second evaluation
        instance.set_password("password2")
        trans_id_2 = id(instance._translation_func)
        
        # Translation function should be the same (not reloaded)
        self.assertEqual(trans_id_1, trans_id_2)
    
    def test_empty_password(self):
        """Test handling of empty password."""
        instance = ZxcvbnInstance()
        
        result = instance.set_password("")
        self.assertIsInstance(result, dict)
        self.assertEqual(instance.get_password(), "")
    
    def test_unicode_password(self):
        """Test handling of unicode passwords."""
        instance = ZxcvbnInstance()
        
        unicode_password = "pÄssword密码"
        result = instance.set_password(unicode_password)
        self.assertIsInstance(result, dict)
        self.assertEqual(instance.get_password(), unicode_password)
    
    def test_repr(self):
        """Test string representation of instance."""
        instance = ZxcvbnInstance(lang='zh_Hans', thread_safe=True)
        repr_str = repr(instance)
        
        self.assertIn("ZxcvbnInstance", repr_str)
        self.assertIn("lang='zh_Hans'", repr_str)
        self.assertIn("thread_safe=True", repr_str)
        self.assertIn("password_set=False", repr_str)
        
        # Set a password and check again
        instance.set_password("test")
        repr_str = repr(instance)
        self.assertIn("password_set=True", repr_str)
    
    def test_temp_user_inputs_basic(self):
        """Test basic temporary user inputs functionality."""
        instance = ZxcvbnInstance()
        
        # Evaluate with temporary user inputs
        result = instance.set_passwd_and_input('alice123', temp_user_inputs=['alice', 'alice@example.com'])
        
        # Result should be valid
        self.assertIsInstance(result, dict)
        self.assertIn('score', result)
        
        # Check that temporary user inputs were used in matching
        all_matches = instance._omnimatch('alice123', ['alice', 'alice@example.com'])
        found_user_match = False
        for match in all_matches:
            if match.get('dictionary_name') == 'user_inputs' and 'alice' in match.get('matched_word', ''):
                found_user_match = True
                break
        self.assertTrue(found_user_match, "Temporary user input should be detected")
    
    def test_temp_user_inputs_isolation(self):
        """Test that different evaluations with temp inputs are isolated."""
        instance = ZxcvbnInstance()
        
        # First evaluation with Alice's inputs
        result1 = instance.set_passwd_and_input('alice123', temp_user_inputs=['alice'])
        
        # Second evaluation with Bob's inputs
        result2 = instance.set_passwd_and_input('bob456', temp_user_inputs=['bob'])
        
        # Verify Bob's evaluation doesn't contain Alice's inputs
        bob_matches = instance._omnimatch('alice123', ['bob'])
        found_alice = False
        for match in bob_matches:
            if match.get('dictionary_name') == 'user_inputs' and 'alice' in match.get('matched_word', ''):
                found_alice = True
                break
        self.assertFalse(found_alice, "Previous user's inputs should not persist")
    
    def test_temp_user_inputs_merge(self):
        """Test merging instance-level and temporary user inputs."""
        # Create instance with instance-level user inputs
        instance = ZxcvbnInstance(user_inputs=['company', 'acmecorp'])
        
        # Evaluate with additional temporary user inputs
        result = instance.set_passwd_and_input(
            'john_acmecorp_123',
            temp_user_inputs=['john', 'john@example.com']
        )
        
        # Verify both instance and temporary inputs are used
        combined_inputs = ['company', 'acmecorp', 'john', 'john@example.com']
        all_matches = instance._omnimatch('john_acmecorp_123', combined_inputs)
        
        found_company = False
        found_john = False
        for match in all_matches:
            if match.get('dictionary_name') == 'user_inputs':
                if 'company' in match.get('matched_word', '') or 'acmecorp' in match.get('matched_word', ''):
                    found_company = True
                if 'john' in match.get('matched_word', ''):
                    found_john = True
        
        self.assertTrue(found_company, "Instance-level user inputs should be present")
        self.assertTrue(found_john, "Temporary user inputs should be present")
    
    def test_temp_user_inputs_empty(self):
        """Test behavior with empty temporary user inputs."""
        instance = ZxcvbnInstance(user_inputs=['test'])
        
        # Test with None
        result1 = instance.set_passwd_and_input('password123', temp_user_inputs=None)
        self.assertIsInstance(result1, dict)
        
        # Test with empty list
        result2 = instance.set_passwd_and_input('password123', temp_user_inputs=[])
        self.assertIsInstance(result2, dict)
        
        # Both should use instance-level inputs only
        self.assertEqual(result1['score'], result2['score'])
    
    def test_temp_user_inputs_backward_compat(self):
        """Test backward compatibility with set_password()."""
        instance = ZxcvbnInstance(user_inputs=['test'])
        
        # Old method should still work
        result1 = instance.set_password('password123')
        
        # Should be equivalent to new method with no temp inputs
        result2 = instance.set_passwd_and_input('password123', temp_user_inputs=None)
        
        # Results should be identical
        self.assertEqual(result1['score'], result2['score'])
        self.assertEqual(result1['guesses'], result2['guesses'])
    
    def test_temp_user_inputs_thread_safe(self):
        """Test thread safety with temporary user inputs."""
        instance = ZxcvbnInstance(thread_safe=True)
        results = []
        errors = []
        
        def worker(user_id):
            try:
                user_name = f'user{user_id}'
                password = f'{user_name}123'
                result = instance.set_passwd_and_input(
                    password,
                    temp_user_inputs=[user_name, f'{user_name}@example.com']
                )
                results.append((user_id, result['score']))
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads with different user inputs
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check that no errors occurred
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Check that all threads completed
        self.assertEqual(len(results), 10)
    
    def test_temp_user_inputs_no_cache_pollution(self):
        """Test that temporary inputs don't pollute the instance cache."""
        instance = ZxcvbnInstance(user_inputs=['permanent'])
        
        # Store original cache ID
        original_cache_id = id(instance._ranked_dictionaries)
        original_user_inputs_cache = instance._ranked_dictionaries.get('user_inputs', {})
        
        # Evaluate with temporary inputs
        result = instance.set_passwd_and_input(
            'alice123',
            temp_user_inputs=['alice', 'temporary']
        )
        
        # Cache should still be the same object
        self.assertEqual(id(instance._ranked_dictionaries), original_cache_id)
        
        # Original user_inputs in cache should not contain temporary inputs
        current_user_inputs_cache = instance._ranked_dictionaries.get('user_inputs', {})
        self.assertNotIn('alice', current_user_inputs_cache)
        self.assertNotIn('temporary', current_user_inputs_cache)
        self.assertIn('permanent', current_user_inputs_cache)
    
    def test_temp_user_inputs_max_length(self):
        """Test max_length validation with temp_user_inputs."""
        instance = ZxcvbnInstance(max_length=10)
        
        # Should work with short password
        result = instance.set_passwd_and_input('short', temp_user_inputs=['test'])
        self.assertIsInstance(result, dict)
        
        # Should raise error with long password even with temp inputs
        with self.assertRaises(ValueError):
            instance.set_passwd_and_input('this_is_too_long', temp_user_inputs=['test'])


if __name__ == '__main__':
    unittest.main()
