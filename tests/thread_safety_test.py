import threading
import time
import unittest
from zxcvbn import zxcvbn, set_thread_safe
from zxcvbn.matching import get_ranked_dictionaries
import zxcvbn.matching  # Import the module to modify its state

class TestThreadSafety(unittest.TestCase):

    def setUp(self):
        # Reset the global state in the matching module before each test
        zxcvbn.matching.RANKED_DICTIONARIES = None
        set_thread_safe(False)  # Default to thread-unsafe

    def tearDown(self):
        # Clean up after tests
        zxcvbn.matching.RANKED_DICTIONARIES = None
        set_thread_safe(False)

    def _run_thread_test(self, thread_safe, mock_class, expected_success):
        """Common test logic for thread safety/unsafety cases"""
        set_thread_safe(thread_safe)

        from zxcvbn import frequency_lists
        original_freq_lists = frequency_lists.FREQUENCY_LISTS
        frequency_lists.FREQUENCY_LISTS = mock_class(original_freq_lists)

        results = []
        threads = []
        for _ in range(5):
            t = threading.Thread(target=self.worker_task, args=(results,))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()

        frequency_lists.FREQUENCY_LISTS = original_freq_lists
        
        if expected_success:
            self.assertTrue(all(results), "All threads should succeed")
        else: 
            self.assertIn(False, results, "Expected some threads to fail")

    def worker_task(self, results):
        try:
            # Each thread will try to get the dictionaries and check validity
            ranked_dicts = get_ranked_dictionaries()
            self.assertIn('passwords', ranked_dicts)
            self.assertGreater(len(ranked_dicts['passwords']), 0)
            results.append(True)
        except (KeyError, AssertionError):
            results.append(False)

    def test_thread_unsafe_behavior(self):
        """Verify that with the flag off, race conditions can occur."""
        class ToggleFrequencyLists:
            def __init__(self, original):
                self.original = original
                self.data = None
                
            def items(self):
                if self.data is None:
                    self.data = {'passwords': {}}
                    time.sleep(3)  # Simulate initialization delay
                    self.data = self.original
                return self.data.items()

        self._run_thread_test(thread_safe=False, 
                           mock_class=ToggleFrequencyLists,
                           expected_success=False)
        print("test_thread_unsafe_behavior results")

    def test_thread_safe_behavior(self):
        """Verify that with the flag on, race conditions are prevented."""
        class MockFrequencyLists:
            def __init__(self, original):
                self.original = original
                self.pause_event = threading.Event()
                self.release_event = threading.Event()

            def items(self):
                self.pause_event.set()
                self.release_event.wait(timeout=5)
                return self.original.items()

        self._run_thread_test(thread_safe=True,
                           mock_class=MockFrequencyLists,
                           expected_success=True)
        print("test_thread_safe_behavior results")

if __name__ == '__main__':
    unittest.main()
