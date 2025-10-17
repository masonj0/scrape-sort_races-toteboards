from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Navigate to the running application
    page.goto("http://localhost:3000")

    # Wait for the main heading to be visible to ensure the page has loaded
    heading = page.get_by_role("heading", name="Today's Top Race Opportunities")
    expect(heading).to_be_visible()

    # Take a screenshot of the simple mode dashboard
    page.screenshot(path="jules-scratch/verification/simple_mode_dashboard.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)