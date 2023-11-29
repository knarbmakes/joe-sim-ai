import unittest
from core.idgen import generate_id  # Replace 'your_module' with the actual name of your module

class TestGenerateId(unittest.TestCase):

    def test_id_length(self):
        """Test that the generated ID has the correct length."""
        expected_length = 8
        generated_id = generate_id()
        self.assertEqual(len(generated_id), expected_length, 
                         f"Generated ID should be {expected_length} characters long")

    def test_unique_ids(self):
        """Test that multiple calls to generate_id produce different IDs."""
        id_set = set(generate_id() for _ in range(100))
        self.assertEqual(len(id_set), 100, 
                         "All generated IDs should be unique")

    def test_custom_length_id(self):
        """Test that the generated ID with custom length is correct."""
        custom_length = 5
        generated_id = generate_id(custom_length)
        self.assertEqual(len(generated_id), custom_length, 
                         f"Generated ID should be {custom_length} characters long")

if __name__ == '__main__':
    unittest.main()
