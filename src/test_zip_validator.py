from zip_validator import ZIPValidator

def test_zip_validator():
    validator = ZIPValidator()
    
    # Test cases
    test_cases = [
        ('10001', True),  # Valid NYC ZIP
        ('90210', True),  # Valid Beverly Hills ZIP
        ('1234', False),  # Too short
        ('123456', False),  # Too long
        ('abcde', False),  # Non-numeric
        ('99999', False),  # Valid format but not in database
    ]
    
    print("Testing ZIP Validator:")
    print("-" * 50)
    
    for zip_code, expected_valid in test_cases:
        is_valid, message, info = validator.validate_zip(zip_code)
        print(f"ZIP Code: {zip_code}")
        print(f"Expected Valid: {expected_valid}")
        print(f"Actual Valid: {is_valid}")
        print(f"Message: {message}")
        if info:
            print(f"Info: {info}")
        print("-" * 50)

if __name__ == "__main__":
    test_zip_validator() 