import requests
import concurrent.futures
import time
import sys

def check_proxy_simple(proxy):
    """
    Simple, reliable proxy check
    """
    # Prepare proxy format for requests
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    # Multiple test URLs - if one fails, try another
    test_urls = [
        "http://httpbin.org/ip",           # Basic test
        "https://api.ipify.org?format=json",  # IP check
        "http://icanhazip.com",            # Simple IP response
        "https://checkip.amazonaws.com"    # Amazon IP check
    ]
    
    for url in test_urls:
        try:
            # Try without and with different timeouts
            response = requests.get(
                url,
                proxies=proxies,
                timeout=7,  # Longer timeout
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            if response.status_code == 200:
                # Get the IP to verify it's actually using proxy
                content = response.text.strip()
                print(f"✓ WORKING: {proxy} | Response: {content[:50]}...")
                return True, proxy
                
        except requests.exceptions.ConnectTimeout:
            print(f"✗ Timeout: {proxy}")
            break
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection failed: {proxy}")
            break
        except requests.exceptions.ProxyError:
            print(f"✗ Proxy error: {proxy}")
            break
        except Exception as e:
            # Try next URL
            continue
    
    return False, proxy

def main():
    print("=" * 60)
    print("PROXY CHECKER - Simple & Reliable")
    print("=" * 60)
    
    # Read proxies from file
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("ERROR: proxies.txt file not found!")
        print("Make sure proxies.txt is in the same folder as this script.")
        input("Press Enter to exit...")
        return
    
    print(f"Loaded {len(proxies)} proxies from proxies.txt")
    print("Checking... This may take a few minutes.\n")
    
    working_proxies = []
    total = len(proxies)
    
    # Check proxies with threading
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        # Submit all checks
        future_to_proxy = {executor.submit(check_proxy_simple, proxy): proxy for proxy in proxies}
        
        # Process results
        for i, future in enumerate(concurrent.futures.as_completed(future_to_proxy)):
            is_working, proxy = future.result()
            if is_working:
                working_proxies.append(proxy)
            
            # Show progress
            sys.stdout.write(f"\rProgress: {i+1}/{total} | Working: {len(working_proxies)}")
            sys.stdout.flush()
    
    print(f"\n\n{'='*60}")
    print(f"RESULTS:")
    print(f"Total proxies checked: {total}")
    print(f"Working proxies found: {len(working_proxies)}")
    print(f"Success rate: {(len(working_proxies)/total*100):.1f}%")
    print(f"{'='*60}\n")
    
    # Save working proxies
    if working_proxies:
        with open("working_proxies.txt", "w") as f:
            for proxy in working_proxies:
                f.write(proxy + "\n")
        print(f"✓ Working proxies saved to: working_proxies.txt")
        
        # Show first 10 working proxies
        print("\nFirst 10 working proxies:")
        for i, proxy in enumerate(working_proxies[:10], 1):
            print(f"{i}. {proxy}")
    else:
        print("✗ No working proxies found!")
        print("\nPossible reasons:")
        print("1. All proxies are actually dead")
        print("2. Your internet connection is blocking proxy checks")
        print("3. Try running as administrator")
        print("4. Try disabling firewall/antivirus temporarily")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()