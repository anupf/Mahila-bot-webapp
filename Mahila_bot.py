from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, csv

# Load applicant data
with open("Applicant_Names.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    applicants = list(reader)

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

url = "https://uat-mahakrishi.mahaitgov.in/mahila-shetkari-service/status/"
driver.get(url)

wait = WebDriverWait(driver, 15)
results = []

for applicant in applicants:
    try:
        # ✅ Click "By name & location" option before filling details
        mode_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lookupModeSeg"]/label[2]/span')))
        driver.execute_script("arguments[0].click();", mode_btn)

        # Fill Applicant Name first
        name_field = wait.until(EC.element_to_be_clickable((By.ID, "s_name")))
        driver.execute_script("arguments[0].scrollIntoView(true);", name_field)
        name_field.clear()
        name_field.send_keys(applicant["Name of Applicant"])

        # Select District
        Select(wait.until(EC.element_to_be_clickable((By.ID, "s_district")))).select_by_visible_text("Yavatmal")

        # Wait for Taluka options
        wait.until(lambda d: len(Select(d.find_element(By.ID, "s_taluka")).options) > 1)
        Select(driver.find_element(By.ID, "s_taluka")).select_by_visible_text("Pandharkawda")

        # Wait for Village options
        wait.until(lambda d: len(Select(d.find_element(By.ID, "s_village")).options) > 1)
        Select(driver.find_element(By.ID, "s_village")).select_by_visible_text("Tad Umari")

        # Extra wait: confirm Village is selected
        wait.until(lambda d: Select(d.find_element(By.ID, "s_village")).first_selected_option.text == "Tad Umari")

        # Click Track Application button via XPath
        track_btn = driver.find_element(By.XPATH, '//*[@id="nameForm"]/button')
        driver.execute_script("arguments[0].click();", track_btn)

        # Stay on result page for 30 seconds
        time.sleep(2)

        # Wait for result block
        status_block = wait.until(
            EC.presence_of_element_located((By.XPATH, "//p[span[contains(text(),'Acknowledgment No')]]"))
        )

        # Extract acknowledgment number
        ack_no = status_block.find_element(
            By.XPATH, ".//span[contains(text(),'Acknowledgment No')]/following-sibling::strong"
        ).text.strip()

        print(f"{applicant['Name of Applicant']} → Ack: {ack_no}")
        results.append({
            "Name": applicant["Name of Applicant"],
            "AckNumber": ack_no
        })

        # Reset back to form for next applicant
        driver.get(url)
        time.sleep(2)

    except Exception as e:
        print(f"Error for {applicant['Name of Applicant']}: {e}")

# Save results
with open("Acknowledgments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "AckNumber"])
    writer.writeheader()
    writer.writerows(results)

driver.quit()
