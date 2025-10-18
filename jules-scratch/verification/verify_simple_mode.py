from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the home page
    page.goto("http://localhost:3000")

    # Take a screenshot of the default 'Simple Mode'
    page.screenshot(path="jules-scratch/verification/simple_mode.png")

    # Click the button to switch to 'Advanced Mode'
    page.get_by_role("button", name="Switch to Advanced Mode").click()

    # Take a screenshot of the 'Advanced Mode'
    page.screenshot(path="jules-scratch/verification/advanced_mode.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
