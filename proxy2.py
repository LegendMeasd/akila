import requests
import concurrent.futures
import time
import sys
from urllib.parse import urlparse

def check_proxy_thorough(proxy):
    """
    More thorough proxy check that tests both HTTP and HTTPS sites
    """
    # Parse proxy to determine type
    parsed = urlparse(proxy)
    proxy_type = parsed.scheme if parsed.scheme else 'http'
    
    # Format proxy for requests
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    # Test with REAL websites that you'd actually browse
    # Mix of HTTP and HTTPS to ensure both work
    test_sites = [
        ('https://www.google.com', 'Google'),
        ('https://www.wikipedia.org', 'Wikipedia'),
        ('http://example.com', 'Example.com'),
    ]
    
    results = {'passed': 0, 'failed': 0, 'errors': []}
    
    for url, name in test_sites:
        try:
            response = requests.get(
                url,
                proxies=proxies,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                allow_redirects=True,
                verify=True  # Verify SSL certificates
            )
            
            if response.status_code == 200:
                results['passed'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"{name}: Status {response.status_code}")
                
        except requests.exceptions.SSLError:
            results['failed'] += 1
            results['errors'].append(f"{name}: SSL Error")
        except requests.exceptions.ProxyError:
            results['failed'] += 1
            results['errors'].append(f"{name}: Proxy Error")
        except requests.exceptions.ConnectTimeout:
            results['failed'] += 1
            results['errors'].append(f"{name}: Timeout")
        except requests.exceptions.ConnectionError:
            results['failed'] += 1
            results['errors'].append(f"{name}: Connection Failed")
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{name}: {type(e).__name__}")
    
    # Only consider it working if it passed ALL tests
    is_working = results['passed'] == len(test_sites) and results['failed'] == 0
    
    if is_working:
        print(f"✓ WORKING: {proxy}")
    else:
        print(f"✗ FAILED: {proxy} (Passed {results['passed']}/{len(test_sites)})")
        if results['errors']:
            print(f"  Errors: {', '.join(results['errors'][:2])}")
    
    return is_working, proxy, results

def main():
    print("=" * 60)
    print("IMPROVED PROXY CHECKER - Real Website Testing")
    print("=" * 60)
    
    # Read proxies from file
    try:
        with open("working_proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("ERROR: working_proxies.txt file not found!")
        input("Press Enter to exit...")
        return
    
    print(f"Loaded {len(proxies)} proxies from working_proxies.txt")
    print("Testing with real websites (Google, Wikipedia, Example.com)...")
    print("This will take longer but be more accurate.\n")
    
    working_proxies = []
    total = len(proxies)
    
    # Check proxies with threading (fewer workers for more thorough checks)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(check_proxy_thorough, proxy): proxy for proxy in proxies}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_proxy)):
            is_working, proxy, results = future.result()
            if is_working:
                working_proxies.append(proxy)
            
            # Show progress
            sys.stdout.write(f"\rProgress: {i+1}/{total} | Working: {len(working_proxies)}")
            sys.stdout.flush()
    
    print(f"\n\n{'='*60}")
    print(f"RESULTS:")
    print(f"Total proxies tested: {total}")
    print(f"Actually working proxies: {len(working_proxies)}")
    print(f"Success rate: {(len(working_proxies)/total*100):.1f}%")
    print(f"{'='*60}\n")
    
    # Save actually working proxies
    if working_proxies:
        with open("verified_working_proxies.txt", "w") as f:
            for proxy in working_proxies:
                f.write(proxy + "\n")
        print(f"✓ Verified working proxies saved to: verified_working_proxies.txt")
        
        # Show all working proxies
        print(f"\nAll {len(working_proxies)} verified working proxies:")
        for i, proxy in enumerate(working_proxies, 1):
            print(f"{i}. {proxy}")
    else:
        print("✗ No fully working proxies found!")
        print("\nThis means:")
        print("1. The proxies can respond to API endpoints but not real websites")
        print("2. They might be HTTP-only proxies that don't support HTTPS")
        print("3. They might have SSL/TLS issues")
        print("4. They might be geo-restricted or rate-limited")
        print("\nRecommendation: Try finding proxies from more reliable sources")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
