from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:3000")

        # Wait for the dashboard to load and find the export button
        export_button = page.locator("text=Export to Excel")
        export_button.wait_for(state='visible')

        page.screenshot(path="jules-scratch/verification/export_button_verification.png")
        browser.close()

if __name__ == "__main__":
    run()
