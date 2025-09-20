from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to the running Dash application
        page.goto("http://0.0.0.0:8050")

        # Wait for the "Live Tipsheet" heading to be visible.
        # This confirms that the initial callback has fired and the page is loaded.
        # We'll set a longer timeout just in case the API is slow to respond.
        expect(page.get_by_role("heading", name="Live Tipsheet")).to_be_visible(timeout=15000)

        # Take a screenshot of the entire page to verify the new layout and components.
        page.screenshot(path="jules-scratch/verification/cockpit_verification.png")

        browser.close()

if __name__ == "__main__":
    run_verification()
