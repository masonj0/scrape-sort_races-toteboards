#!/usr/bin/env python3
"""
RPB2B Query Parameter Hunter
Strategy: Use the KNOWN working endpoint /racecards/{race_id}
and systematically test query parameters to unlock odds data
"""

import json
import requests
import time
from urllib.parse import urlencode
from typing import List, Dict, Any, Optional

# Base URL and known working endpoint
BASE_URL = "https://backend-us-racecards.widget.rpb2b.com/v2"
KNOWN_ENDPOINT = "/racecards"

# Priority race IDs (focusing on "W" status = 0 MTP candidates)
PRIORITY_RACES = [
    {
        "id": "3331ba90-3b1c-4f71-9c16-eab46dc56b73",
        "track": "Parx",
        "race_num": 7,
        "status": "W",
        "time": "2025-09-09T19:26:00+00:00"
    },
    {
        "id": "c9ec4c7e-7a39-401d-ad36-3ef7f783f3b1",
        "track": "Horseshoe Indianapolis",
        "race_num": 3,
        "status": "W",
        "time": "2025-09-09T19:12:00+00:00"
    },
    {
        "id": "bcb08dee-05ff-4372-b167-0fdd43151819",
        "track": "FanDuel",
        "race_num": 1,
        "status": "W",
        "time": "2025-09-09T19:30:00+00:00"
    }
]

class RPB2BQueryParameterHunter:
    """Systematically test query parameters on known working endpoints"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Referer": "https://widget.rpb2b.com/",
            "Origin": "https://widget.rpb2b.com"
        })

        self.successful_params = []
        self.odds_containing_responses = []
        self.baseline_response = None

    def hunt_parameters(self):
        """Main hunting method - systematically test parameter combinations"""

        print("🔍 RPB2B QUERY PARAMETER HUNTER")
        print("Strategy: Unlock hidden data views in known working endpoints")
        print("=" * 80)

        # Step 1: Establish baseline (no parameters)
        print("\n📊 STEP 1: ESTABLISHING BASELINE")
        self.establish_baseline()

        # Step 2: Test single parameters
        print("\n🎯 STEP 2: TESTING SINGLE PARAMETERS")
        self.test_single_parameters()

        # Step 3: Test parameter combinations
        print("\n🔄 STEP 3: TESTING PARAMETER COMBINATIONS")
        self.test_parameter_combinations()

        # Step 4: Test advanced patterns
        print("\n⚡ STEP 4: TESTING ADVANCED PATTERNS")
        self.test_advanced_patterns()

        # Step 5: Summary and recommendations
        print("\n📈 STEP 5: ANALYSIS & RECOMMENDATIONS")
        self.analyze_results()

    def establish_baseline(self):
        """Get baseline response from known working endpoint"""

        race = PRIORITY_RACES[0]  # Use Parx Race 7 as baseline
        url = f"{BASE_URL}{KNOWN_ENDPOINT}/{race['id']}"

        print(f"🎯 Testing baseline: {race['track']} Race {race['race_num']}")
        print(f"   URL: {url}")

        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                self.baseline_response = response.json()
                print(f"✅ Baseline established: {len(str(self.baseline_response))} chars")

                # Analyze baseline structure
                if isinstance(self.baseline_response, dict):
                    keys = list(self.baseline_response.keys())
                    print(f"   Keys: {keys}")

                    # Look for existing odds-related fields
                    odds_fields = [k for k in keys if any(word in k.lower()
                                 for word in ['odd', 'price', 'bet', 'pool', 'tote', 'market', 'line'])]
                    if odds_fields:
                        print(f"   🎯 Existing odds fields: {odds_fields}")
                    else:
                        print(f"   📝 No obvious odds fields in baseline")

            else:
                print(f"❌ Baseline failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"💥 Baseline error: {e}")
            return False

        time.sleep(1)
        return True

    def test_single_parameters(self):
        """Test single query parameters"""

        # Comprehensive list of potential parameters
        single_params = [
            # Data inclusion parameters
            ("include", "odds"), ("include", "prices"), ("include", "betting"),
            ("include", "tote"), ("include", "pools"), ("include", "live"),
            ("include", "current"), ("include", "runners"), ("include", "entries"),
            ("include", "all"), ("include", "full"), ("include", "complete"),

            # View/format parameters
            ("view", "odds"), ("view", "betting"), ("view", "live"),
            ("view", "full"), ("view", "detailed"), ("view", "complete"),
            ("view", "tote"), ("view", "pools"), ("view", "current"),

            # Data/content parameters
            ("data", "odds"), ("data", "live"), ("data", "betting"),
            ("data", "full"), ("data", "all"), ("data", "tote"),
            ("data", "current"), ("data", "complete"),

            # Format parameters
            ("format", "full"), ("format", "detailed"), ("format", "live"),
            ("format", "odds"), ("format", "betting"),

            # Expand/detail parameters
            ("expand", "odds"), ("expand", "betting"), ("expand", "all"),
            ("expand", "live"), ("expand", "tote"), ("expand", "runners"),
            ("detail", "full"), ("detail", "odds"), ("detail", "live"),

            # Show/display parameters
            ("show", "odds"), ("show", "betting"), ("show", "live"),
            ("show", "all"), ("show", "tote"), ("show", "current"),

            # Type parameters
            ("type", "live"), ("type", "odds"), ("type", "betting"),
            ("type", "tote"), ("type", "full"),

            # Mode parameters
            ("mode", "live"), ("mode", "betting"), ("mode", "odds"),
            ("mode", "full"), ("mode", "detailed"),

            # Boolean flags (common patterns)
            ("odds", "true"), ("odds", "1"), ("odds", "yes"),
            ("live", "true"), ("live", "1"), ("live", "yes"),
            ("betting", "true"), ("betting", "1"), ("betting", "yes"),
            ("tote", "true"), ("tote", "1"), ("tote", "yes"),
            ("full", "true"), ("full", "1"), ("full", "yes"),
            ("detailed", "true"), ("detailed", "1"),
            ("current", "true"), ("current", "1"),

            # Time-related parameters
            ("time", "current"), ("time", "live"), ("time", "now"),
            ("timestamp", "current"), ("ts", "now"),

            # API versioning
            ("version", "2"), ("version", "live"), ("v", "2"),
            ("api", "live"), ("api", "betting"),

            # Output parameters
            ("output", "full"), ("output", "detailed"), ("output", "odds"),

            # Common API patterns
            ("fields", "odds"), ("fields", "all"), ("fields", "betting"),
            ("select", "odds"), ("select", "all"),
            ("with", "odds"), ("with", "betting"), ("with", "live")
        ]

        print(f"📋 Testing {len(single_params)} single parameter combinations...")

        race = PRIORITY_RACES[0]  # Test with Parx Race 7

        for param_name, param_value in single_params:
            self.test_parameter_combination(race, {param_name: param_value})
            time.sleep(0.3)  # Be respectful

    def test_parameter_combinations(self):
        """Test combinations of parameters"""

        print(f"🔄 Testing parameter combinations...")

        # High-value parameter combinations
        param_combinations = [
            # Multi-include patterns
            {"include": "odds,betting", "format": "full"},
            {"include": "live,odds", "view": "current"},
            {"include": "all", "detail": "full"},
            {"include": "tote,pools", "format": "live"},

            # View + data patterns
            {"view": "odds", "data": "live"},
            {"view": "betting", "data": "current"},
            {"view": "live", "format": "detailed"},
            {"view": "full", "include": "odds"},

            # Boolean flag combinations
            {"odds": "true", "live": "true"},
            {"betting": "true", "current": "true"},
            {"tote": "true", "live": "true"},
            {"full": "true", "detailed": "true"},

            # API-style combinations
            {"fields": "odds,betting,live", "format": "json"},
            {"select": "odds,runners", "expand": "all"},
            {"with": "odds,tote", "mode": "live"},

            # Time-sensitive combinations
            {"time": "current", "include": "odds"},
            {"live": "true", "timestamp": "now"},
            {"current": "true", "view": "odds"},

            # Comprehensive requests
            {"include": "all", "expand": "full", "detail": "complete"},
            {"view": "live", "data": "full", "format": "detailed"},
            {"odds": "true", "betting": "true", "tote": "true", "live": "true"}
        ]

        race = PRIORITY_RACES[0]  # Test with Parx Race 7

        for params in param_combinations:
            self.test_parameter_combination(race, params)
            time.sleep(0.5)  # Slightly longer delay for combinations

    def test_advanced_patterns(self):
        """Test advanced parameter patterns"""

        print(f"⚡ Testing advanced parameter patterns...")

        race = PRIORITY_RACES[0]

        # Test with different races to see if parameter behavior varies
        print(f"\n🏇 Testing parameters across different race statuses...")

        advanced_params = [
            {"include": "odds", "format": "live"},
            {"view": "betting", "data": "current"},
            {"odds": "true", "live": "true", "format": "detailed"}
        ]

        for params in advanced_params:
            print(f"\n🧪 Testing params {params} across races:")

            for race in PRIORITY_RACES:
                print(f"   🎯 {race['track']} Race {race['race_num']} ({race['status']}): ", end="")
                result = self.test_parameter_combination(race, params, verbose=False)
                if result and result.get('different_from_baseline'):
                    print("🎯 DIFFERENT DATA!")
                elif result and result.get('success'):
                    print("✅ Same")
                else:
                    print("❌ Failed")
                time.sleep(0.3)

    def test_parameter_combination(self, race: Dict, params: Dict, verbose: bool = True) -> Optional[Dict]:
        """Test a specific parameter combination"""

        url = f"{BASE_URL}{KNOWN_ENDPOINT}/{race['id']}"
        if params:
            url += "?" + urlencode(params)

        if verbose:
            param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
            print(f"\n🧪 Testing: {param_str}")
            print(f"   URL: {url}")

        try:
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                try:
                    data = response.json()

                    # Compare with baseline
                    different_from_baseline = self.is_different_from_baseline(data)
                    contains_odds = self.contains_odds_data(data)

                    if verbose:
                        print(f"   ✅ Success: {len(str(data))} chars")

                        if different_from_baseline:
                            print(f"   🎯 DIFFERENT FROM BASELINE!")

                        if contains_odds:
                            print(f"   💰 CONTAINS ODDS DATA!")

                    # Track successful parameters
                    if different_from_baseline or contains_odds:
                        self.successful_params.append({
                            'race': race,
                            'params': params,
                            'url': url,
                            'response_size': len(str(data)),
                            'different': different_from_baseline,
                            'has_odds': contains_odds,
                            'data_sample': str(data)[:500]
                        })

                    if contains_odds:
                        self.odds_containing_responses.append({
                            'race': race,
                            'params': params,
                            'url': url,
                            'data': data
                        })

                    return {
                        'success': True,
                        'data': data,
                        'different_from_baseline': different_from_baseline,
                        'contains_odds': contains_odds
                    }

                except json.JSONDecodeError:
                    if verbose:
                        print(f"   ⚠️  Non-JSON response: {response.text[:100]}")
                    return {'success': True, 'data': response.text}

            else:
                if verbose:
                    print(f"   ❌ Status: {response.status_code}")
                    if "Invalid endpoint" in response.text:
                        print(f"      (Same invalid endpoint error)")
                return {'success': False, 'status': response.status_code}

        except Exception as e:
            if verbose:
                print(f"   💥 Error: {str(e)[:50]}")
            return {'success': False, 'error': str(e)}

    def is_different_from_baseline(self, data: Any) -> bool:
        """Compare response data with baseline to detect differences"""

        if not self.baseline_response or not data:
            return False

        # Simple comparison - different size or structure
        baseline_str = json.dumps(self.baseline_response, sort_keys=True)
        data_str = json.dumps(data, sort_keys=True)

        return baseline_str != data_str

    def contains_odds_data(self, data: Any) -> bool:
        """Check if response contains odds/betting data"""

        if not data:
            return False

        data_str = json.dumps(data).lower() if isinstance(data, (dict, list)) else str(data).lower()

        odds_keywords = [
            'odd', 'odds', 'price', 'morning line', 'ml', 'current',
            'win', 'place', 'show', 'exacta', 'trifecta', 'superfecta',
            'bet', 'betting', 'wager', 'pool', 'tote', 'toteboard',
            'market', 'line', 'payout', 'return', 'dividend'
        ]

        return any(keyword in data_str for keyword in odds_keywords)

    def analyze_results(self):
        """Analyze and report findings"""

        print("📊 QUERY PARAMETER HUNT RESULTS")
        print("=" * 60)

        print(f"\n📈 SUMMARY:")
        print(f"   • Parameters tested: ~100+")
        print(f"   • Successful variations: {len(self.successful_params)}")
        print(f"   • Responses with odds data: {len(self.odds_containing_responses)}")

        if self.successful_params:
            print(f"\n✅ SUCCESSFUL PARAMETER VARIATIONS:")
            for i, result in enumerate(self.successful_params, 1):
                race = result['race']
                params = result['params']

                print(f"\n   {i:2d}. {race['track']} Race {race['race_num']} ({race['status']})")
                print(f"       Parameters: {params}")
                print(f"       URL: {result['url']}")
                print(f"       Response size: {result['response_size']} chars")

                if result['different']:
                    print(f"       🎯 Different from baseline!")
                if result['has_odds']:
                    print(f"       💰 Contains odds data!")

                print(f"       Sample: {result['data_sample'][:200]}...")

        if self.odds_containing_responses:
            print(f"\n🎯 ENDPOINTS WITH ODDS DATA:")
            for i, odds_result in enumerate(self.odds_containing_responses, 1):
                race = odds_result['race']
                print(f"\n   {i:2d}. 💰 {race['track']} Race {race['race_num']} - LIVE ODDS FOUND!")
                print(f"       URL: {odds_result['url']}")
                print(f"       Parameters: {odds_result['params']}")

        # Generate recommendations
        print(f"\n🎯 RECOMMENDATIONS:")

        if self.successful_params:
            print(f"   ✅ SUCCESS! Found working parameter variations!")
            print(f"   📋 Next steps:")
            print(f"      1. Test these successful parameters on other race IDs")
            print(f"      2. Look for patterns in working parameters")
            print(f"      3. Try similar parameter variations")

            # Extract common patterns
            successful_param_names = set()
            for result in self.successful_params:
                successful_param_names.update(result['params'].keys())

            if successful_param_names:
                print(f"   🔑 Successful parameter names: {sorted(successful_param_names)}")

        else:
            print(f"   📝 No parameter variations found that change the response")
            print(f"   🔄 Alternative strategies to try:")
            print(f"      1. Test parameters on /racecards/daily/YYYY-MM-DD endpoint")
            print(f"      2. Try HTTP headers instead of query parameters")
            print(f"      3. Look for WebSocket endpoints")
            print(f"      4. Check for required authentication tokens")
            print(f"      5. Monitor browser network traffic on widget.rpb2b.com")

        # Generate copy-paste URLs for further testing
        if self.successful_params:
            print(f"\n📋 COPY-PASTE URLS FOR FURTHER TESTING:")
            for result in self.successful_params[:5]:  # Top 5
                print(f"   • {result['url']}")

def main():
    """Main execution function"""

    hunter = RPB2BQueryParameterHunter()

    print("🚀 Starting systematic query parameter hunt...")
    print("Strategy: Use known working endpoint with parameter variations")
    print("Target: Unlock live odds data for 0 MTP races\n")

    hunter.hunt_parameters()

    print(f"\n🎉 Parameter hunt complete!")

    # Offer to test specific parameters
    print(f"\n💡 Want to test specific parameter ideas? (y/N): ", end="")
    test_custom = input().lower().strip()

    if test_custom == 'y':
        print(f"\nEnter parameter combinations to test (format: key=value,key2=value2):")
        custom_params_str = input("Parameters: ").strip()

        if custom_params_str:
            try:
                custom_params = {}
                for pair in custom_params_str.split(','):
                    k, v = pair.split('=', 1)
                    custom_params[k.strip()] = v.strip()

                print(f"\n🧪 Testing custom parameters: {custom_params}")
                result = hunter.test_parameter_combination(PRIORITY_RACES[0], custom_params)

                if result and result.get('different_from_baseline'):
                    print(f"🎯 SUCCESS! Different data found!")
                elif result and result.get('contains_odds'):
                    print(f"💰 ODDS DATA DETECTED!")

            except Exception as e:
                print(f"❌ Error testing custom parameters: {e}")

if __name__ == "__main__":
    main()
