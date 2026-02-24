from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501", timeout=60000)

            # Wait for header
            print("Waiting for header...")
            page.wait_for_selector("text=SMART LEARNING CENTER", timeout=60000)

            # Click "1-sinf" button
            # It's a button with text "1-sinf"
            print("Clicking 1-sinf...")
            # There are multiple buttons with "1-sinf" (sidebar and main card)
            # We can just click the first one or specifically the card.
            # Usually main content buttons are more prominent.
            # But let's try get_by_role("button", name="1-sinf").first
            page.get_by_role("button", name="1-sinf").first.click()

            # Wait for class view
            print("Waiting for class view...")
            page.wait_for_selector("text=1-sinf Matematika", timeout=60000)

            # Now entering name
            print("Entering name...")
            page.get_by_role("textbox").fill("Tester")

            # Click "Boshlash"
            print("Clicking Boshlash...")
            page.get_by_role("button", name="Boshlash").click()

            # Wait for quiz to start (e.g., "Savol 1/")
            print("Waiting for quiz start...")
            page.wait_for_selector("text=Savol 1/", timeout=60000)

            print("Quiz started successfully! Random works.")
            page.screenshot(path="verification_quiz_success.png")

        except Exception as e:
            print(f"Error: {e}")
            try:
                page.screenshot(path="verification_error.png")
            except:
                pass
        finally:
            browser.close()

if __name__ == "__main__":
    run()
