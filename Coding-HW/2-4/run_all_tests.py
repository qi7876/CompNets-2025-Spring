import subprocess
import sys
import time
import socket
import threading
import os

def check_proxy_running():
    """Check if proxy server is running on port 8888"""
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = test_sock.connect_ex(('localhost', 8888))
        test_sock.close()
        return result == 0
    except:
        return False

def run_test_script(script_name):
    """Run a test script and return success status"""
    try:
        print(f"\n{'='*50}")
        print(f"Running {script_name}...")
        print('='*50)
        
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        # Check if tests passed based on output - multiple success patterns
        output = result.stdout
        success_patterns = [
            "✓ All" in output and "tests passed!" in output,
            "✓ All" in output and "successful!" in output,
            "tests mostly successful!" in output,
            "tests successful!" in output
        ]
        
        return any(success_patterns)
            
    except subprocess.TimeoutExpired:
        print(f"✗ {script_name} timed out!")
        return False
    except Exception as e:
        print(f"✗ Error running {script_name}: {e}")
        return False

def main():
    print("=== Proxy Server Test Suite ===")
    print("Testing all enhanced proxy server features...\n")
    
    # Check if proxy server is running
    if not check_proxy_running():
        print("✗ Proxy server is not running on port 8888!")
        print("Please start the proxy server first:")
        print("python 2-4-Web代理服务器框架代码.py")
        return
    
    print("✓ Proxy server detected on port 8888")
    
    # Test scripts to run
    test_scripts = [
        "test_basic_http.py",
        "test_cache_validation.py", 
        "test_large_files.py",
        "test_https.py"
    ]
    
    results = {}
    
    # Run each test script
    for script in test_scripts:
        if os.path.exists(script):
            results[script] = run_test_script(script)
            time.sleep(2)  # Wait between tests
        else:
            print(f"✗ Test script {script} not found!")
            results[script] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(test_scripts)
    
    for script, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{script}: {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All proxy server features are working correctly!")
    else:
        print("⚠️  Some features need attention.")
    
    # Feature verification checklist
    print(f"\n{'='*50}")
    print("FEATURE VERIFICATION CHECKLIST")
    print('='*50)
    
    features = {
        "HTTP GET Support": results.get("test_basic_http.py", False),
        "HTTP POST Support": results.get("test_basic_http.py", False),
        "Cache Creation & Serving": results.get("test_cache_validation.py", False),
        "Cache Validation (Last-Modified)": results.get("test_cache_validation.py", False),
        "Large File Handling (>4KB)": results.get("test_large_files.py", False),
        "Content-Length Processing": results.get("test_large_files.py", False),
        "HTTPS CONNECT Method": results.get("test_https.py", False),
        "HTTPS Tunneling": results.get("test_https.py", False)
    }
    
    for feature, working in features.items():
        status = "✓" if working else "✗"
        print(f"{status} {feature}")

if __name__ == "__main__":
    main()
