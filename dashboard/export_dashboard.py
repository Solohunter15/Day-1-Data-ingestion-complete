import subprocess
import time
import os
import sys
from playwright.sync_api import sync_playwright
from PIL import Image

# Config
BASE_DIR = r"c:\Users\jibum\OneDrive\Desktop\Bluestock Internship"
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

print("Starting Streamlit server in the background...")
# Run Streamlit on port 8501
streamlit_process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "dashboard/dashboard_app.py", "--server.port", "8501", "--server.headless", "true"],
    cwd=BASE_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for Streamlit to start
print("Waiting for Streamlit server to boot (6 seconds)...")
time.sleep(6)

try:
    with sync_playwright() as p:
        print("Launching headless Chromium...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1536, "height": 960})
        
        print("Navigating to local Streamlit dashboard...")
        page.goto("http://localhost:8501")
        time.sleep(5)  # Wait for first load and animations
        
        # Capture Page 1
        print("Capturing Page 1: Industry Overview...")
        page_1_path = os.path.join(BASE_DIR, "page_1.png")
        page_1_dash = os.path.join(DASHBOARD_DIR, "page_1.png")
        page.screenshot(path=page_1_path, full_page=True)
        page.screenshot(path=page_1_dash, full_page=True)
        
        # Click and Capture Page 2
        print("Switching to Page 2: Fund Performance...")
        page.locator('label:has-text("Fund Performance")').click()
        time.sleep(4)
        page_2_path = os.path.join(BASE_DIR, "page_2.png")
        page_2_dash = os.path.join(DASHBOARD_DIR, "page_2.png")
        page.screenshot(path=page_2_path, full_page=True)
        page.screenshot(path=page_2_dash, full_page=True)
        
        # Click and Capture Page 3
        print("Switching to Page 3: Investor Analytics...")
        page.locator('label:has-text("Investor Analytics")').click()
        time.sleep(4)
        page_3_path = os.path.join(BASE_DIR, "page_3.png")
        page_3_dash = os.path.join(DASHBOARD_DIR, "page_3.png")
        page.screenshot(path=page_3_path, full_page=True)
        page.screenshot(path=page_3_dash, full_page=True)
        
        # Click and Capture Page 4
        print("Switching to Page 4: SIP & Market Trends...")
        page.locator('label:has-text("SIP & Market Trends")').click()
        time.sleep(4)
        page_4_path = os.path.join(BASE_DIR, "page_4.png")
        page_4_dash = os.path.join(DASHBOARD_DIR, "page_4.png")
        page.screenshot(path=page_4_path, full_page=True)
        page.screenshot(path=page_4_dash, full_page=True)
        
        browser.close()
        print("Headless browser closed successfully.")
        
    # Compile screenshots into a single Dashboard.pdf using matplotlib to bypass PIL JPEG issues
    print("Compiling captured pages into unified Dashboard.pdf...")
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    
    pdf_path_root = os.path.join(BASE_DIR, "Dashboard.pdf")
    pdf_path_dash = os.path.join(DASHBOARD_DIR, "Dashboard.pdf")
    
    for pdf_path in [pdf_path_root, pdf_path_dash]:
        with PdfPages(pdf_path) as pdf:
            for img_path in [page_1_path, page_2_path, page_3_path, page_4_path]:
                img = mpimg.imread(img_path)
                fig, ax = plt.subplots(figsize=(16, 10))
                ax.imshow(img)
                ax.axis('off')
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
                pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
                plt.close(fig)
    
    print(f"Successfully generated final combined report: {pdf_path_root}")
    
finally:
    print("Stopping Streamlit server...")
    streamlit_process.terminate()
    try:
        streamlit_process.wait(timeout=3)
        print("Streamlit process stopped successfully.")
    except subprocess.TimeoutExpired:
        streamlit_process.kill()
        print("Streamlit process killed successfully.")
