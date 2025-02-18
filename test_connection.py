import os
import sys
import psycopg2
import redis
from selenium import webdriver
from dotenv import load_dotenv
import requests

def test_environment():
    """Test if environment variables are loaded"""
    load_dotenv()
    required_vars = [
        'INSTAGRAM_USERNAME',
        'INSTAGRAM_PASSWORD',
        'SUPABASE_DB_NAME',
        'SUPABASE_DB_USER',
        'SUPABASE_DB_PASSWORD',
        'SUPABASE_DB_HOST',
        'REDIS_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:", missing_vars)
        return False
    print("✅ Environment variables loaded successfully")
    return True

def test_database():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('SUPABASE_DB_NAME'),
            user=os.getenv('SUPABASE_DB_USER'),
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            host=os.getenv('SUPABASE_DB_HOST'),
            port=os.getenv('SUPABASE_DB_PORT', '5432')
        )
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print("❌ Database connection failed:", str(e))
        return False

def test_redis():
    """Test Redis connection"""
    try:
        r = redis.from_url(os.getenv('REDIS_URL'))
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print("❌ Redis connection failed:", str(e))
        return False

def test_selenium():
    """Test Selenium and Chrome setup"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for testing
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ Selenium and Chrome setup successful")
        return True
    except Exception as e:
        print("❌ Selenium setup failed:", str(e))
        return False

def test_internet():
    """Test internet connection and Instagram accessibility"""
    try:
        response = requests.get('https://www.instagram.com', timeout=5)
        if response.status_code == 200:
            print("✅ Instagram is accessible")
            return True
        else:
            print(f"❌ Instagram returned status code: {response.status_code}")
            return False
    except Exception as e:
        print("❌ Internet connection or Instagram access failed:", str(e))
        return False

def main():
    print("\n=== Testing Server Configuration ===\n")
    
    # Track test results
    results = {
        "Environment": test_environment(),
        "Database": test_database(),
        "Redis": test_redis(),
        "Selenium": test_selenium(),
        "Internet": test_internet()
    }
    
    print("\n=== Test Summary ===")
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test}: {status}")
        if not passed:
            all_passed = False
    
    print("\n=== Final Result ===")
    if all_passed:
        print("✅ All systems are ready!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main() 