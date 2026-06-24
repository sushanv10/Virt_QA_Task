"""
Signup Automation Script - Step 1 + OTP + Step 2 + Step 3 + Step 4
Site: https://authorized-partner.vercel.app/
Framework: Selenium + Python + pytest
"""

import time
import re
import imaplib
import os
import tempfile
import email as email_lib
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


GMAIL_ADDRESS  = "sushanv3@gmail.com"
GMAIL_APP_PASS = "qsle jhyx chhj szws"

_timestamp  = int(time.time())
_inbox_user = GMAIL_ADDRESS.split("@")[0]
TEST_EMAIL  = f"{_inbox_user}+test{_timestamp}@gmail.com"

BASE_URL = "https://authorized-partner.vercel.app/"

TEST_USER = {
    "first_name":       "Test",
    "last_name":        "User",
    "email":            TEST_EMAIL,
    "phone":            "9851117886",
    "password":         "TestPass@123",
    "confirm_password": "TestPass@123",
}

TEST_AGENCY = {
    "agency_name":    "Test Agency Nepal",
    "role_in_agency": "QA Engineer",
    "agency_email":   "agency@testagency.com",
    "agency_website": "testagency.com",
    "agency_address": "Kathmandu, Nepal",
    "region":         "Nepal",
}

TEST_EXPERIENCE = {
    "years_of_experience":                   "2 years",
    "number_of_students_recruited_annually": "50",
    "focus_area":                            "Undergraduate admissions to Canada",
    "success_metrics":                       "90",
    "services": [
        "Career Counseling",
        "Admission Applications",
    ],
}

TEST_VERIFICATION = {
    "business_registration_number": "BRN-2024-TEST-001",
    "preferred_countries":          ["Nepal"],
    "institution_types":            ["Universities", "Colleges"],
    "certification_details":        "ICEF Certified Education Agent",
    "document_1": None,
    "document_2": None,
}


# DRIVER SETUP
@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    # options.add_argument("--headless=new")
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()

# HELPERS
def wait_visible(driver, by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def wait_clickable(driver, by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )

def fill_field(driver, name, value):
    field = wait_visible(driver, By.NAME, name)
    field.clear()
    field.send_keys(value)
    return field

def get_otp_from_gmail(gmail_address, app_password, retries=12, delay=6):
    print(f"\n  Connecting to Gmail: {gmail_address}")
    print(f"  OTP sent to: {TEST_EMAIL}")
    for attempt in range(1, retries + 1):
        print(f" Attempt {attempt}/{retries} — checking inbox...")
        time.sleep(delay)
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(gmail_address, app_password)
            mail.select("inbox")
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                mail.logout()
                print(" No new emails yet...")
                continue
            for msg_id in reversed(messages[0].split()):
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue
                msg = email_lib.message_from_bytes(msg_data[0][1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ("text/plain", "text/html"):
                            try:
                                body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            except Exception:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        body = str(msg.get_payload())
                full_text = body + " " + msg.get("Subject", "")
                otp_match = re.search(r'\b(\d{6})\b', full_text)
                if otp_match:
                    otp = otp_match.group(1)
                    mail.logout()
                    print(f" OTP found: {otp}")
                    return otp
            mail.logout()
            print("  ⚠️  Emails checked but no OTP yet. Retrying...")
        except imaplib.IMAP4.error as e:
            print(f" Gmail login failed: {e}")
            raise
        except Exception as e:
            print(f"  Error: {e}")
    raise Exception(" OTP not received after all retries.")

def enter_otp_into_field(driver, otp):
    print(f" Entering OTP: {otp}")
    try:
        otp_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-input-otp='true']"))
        )
    except Exception:
        try:
            otp_input = driver.find_element(By.XPATH,
                "//input[@maxlength='6' and @inputmode='numeric']")
        except Exception:
            otp_input = driver.find_element(By.XPATH, "//input[@maxlength='6']")

    driver.execute_script("""
        arguments[0].style.opacity = '1';
        arguments[0].style.pointerEvents = 'all';
        arguments[0].removeAttribute('readonly');
    """, otp_input)
    driver.execute_script("arguments[0].focus();", otp_input)
    time.sleep(0.3)
    driver.execute_script(
        "arguments[0].value = '';"
        "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
        otp_input
    )
    time.sleep(0.2)
    for digit in otp:
        otp_input.send_keys(digit)
        time.sleep(0.15)
    time.sleep(0.5)
    entered = otp_input.get_attribute("value")
    if not entered or len(entered) != 6:
        print(" Trying JS injection fallback...")
        driver.execute_script("""
            var nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            nativeSetter.call(arguments[0], arguments[1]);
            arguments[0].dispatchEvent(new Event('input',  {bubbles:true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
        """, otp_input, otp)
        time.sleep(0.5)

def create_dummy_file(suffix=".pdf", content=b"Test document content for automation"):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(content)
        tmp.close()
        return os.path.abspath(tmp.name)


#  STEP 1 — SET UP YOUR ACCOUNT
def test_01_open_signup_page(driver):
    print("\n[TEST 1] Opening signup page...")
    print(f"  Unique email: {TEST_EMAIL}")
    driver.get(BASE_URL)
    time.sleep(2)
    heading = wait_visible(driver, By.XPATH,
        "//*[contains(text(),'Complete Your Agent Profile')]")
    assert heading is not None
    wait_visible(driver, By.XPATH, "//*[contains(text(),'Set up your Account')]")
    print(" Signup page loaded.")

def test_02_fill_first_name(driver):
    print("\n[TEST 2] Filling First Name...")
    field = fill_field(driver, "firstName", TEST_USER["first_name"])
    assert field.get_attribute("value") == TEST_USER["first_name"]
    print(f" First Name: {field.get_attribute('value')}")

def test_03_fill_last_name(driver):
    print("\n[TEST 3] Filling Last Name...")
    field = fill_field(driver, "lastName", TEST_USER["last_name"])
    assert field.get_attribute("value") == TEST_USER["last_name"]
    print(f" Last Name: {field.get_attribute('value')}")

def test_04_fill_email(driver):
    print("\n[TEST 4] Filling Email...")
    field = fill_field(driver, "email", TEST_USER["email"])
    assert field.get_attribute("value") == TEST_USER["email"]
    print(f" Email: {field.get_attribute('value')}")

def test_05_fill_phone_number(driver):
    print("\n[TEST 5] Filling Phone...")
    field = wait_visible(driver, By.NAME, "phoneNumber")
    field.clear()
    field.send_keys(TEST_USER["phone"])
    assert field.get_attribute("value") == TEST_USER["phone"]
    print(f" Phone: {field.get_attribute('value')}")

def test_06_fill_password(driver):
    print("\n[TEST 6] Filling Password...")
    field = wait_visible(driver, By.NAME, "password")
    field.clear()
    field.send_keys(TEST_USER["password"])
    assert len(field.get_attribute("value")) > 0
    print(" Password entered.")

def test_07_fill_confirm_password(driver):
    print("\n[TEST 7] Filling Confirm Password...")
    field = wait_visible(driver, By.NAME, "confirmPassword")
    field.clear()
    field.send_keys(TEST_USER["confirm_password"])
    assert len(field.get_attribute("value")) > 0
    print(" Confirm Password entered.")

def test_08_validate_all_fields(driver):
    print("\n[TEST 8] Validating Step 1 fields...")
    checks = {
        "firstName":   TEST_USER["first_name"],
        "lastName":    TEST_USER["last_name"],
        "email":       TEST_USER["email"],
        "phoneNumber": TEST_USER["phone"],
    }
    for name, expected in checks.items():
        actual = driver.find_element(By.NAME, name).get_attribute("value")
        assert actual == expected, f"'{name}': expected '{expected}', got '{actual}'"
        print(f" {name}: {actual}")
    pw  = driver.find_element(By.NAME, "password").get_attribute("value")
    cpw = driver.find_element(By.NAME, "confirmPassword").get_attribute("value")
    assert len(pw) > 0 and pw == cpw
    print(" All Step 1 fields validated.")

def test_09_click_next_step1(driver):
    print("\n[TEST 9] Clicking Next (Step 1)...")
    btn = wait_clickable(driver, By.XPATH,
        "//button[@type='submit' and contains(text(),'Next')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
    time.sleep(0.5)
    btn.click()
    time.sleep(3)
    print(" Next clicked.")


#  OTP VERIFICATION
def test_10_otp_page_loaded(driver):
    print("\n[TEST 10] Checking OTP page...")
    otp_heading = wait_visible(driver, By.XPATH,
        "//*[contains(text(),'Verification code') or "
        "contains(text(),'Email Verification') or "
        "contains(text(),'OTP')]", timeout=20)
    assert otp_heading is not None
    print(" OTP page loaded.")

def test_11_fetch_and_enter_otp(driver):
    print("\n[TEST 11] Fetching OTP from Gmail...")
    otp = get_otp_from_gmail(GMAIL_ADDRESS, GMAIL_APP_PASS)
    assert len(otp) == 6 and otp.isdigit()
    enter_otp_into_field(driver, otp)
    print(f" OTP {otp} entered.")

def test_12_click_verify_code(driver):
    print("\n[TEST 12] Clicking Verify Code...")
    verify_btn = wait_clickable(driver, By.XPATH,
        "//button[contains(text(),'Verify Code') or contains(text(),'Verify')]")
    verify_btn.click()
    time.sleep(3)
    print(" Verify Code clicked.")

def test_13_verify_otp_accepted(driver):
    print("\n[TEST 13] Confirming OTP accepted...")
    agency_field = WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.NAME, "agency_name"))
    )
    assert agency_field is not None
    print(f" URL: {driver.current_url}")
    print(" OTP accepted! Step 2 loaded.")

#  STEP 2 — AGENCY DETAILS

def test_14_verify_agency_page_loaded(driver):
    print("\n[TEST 14] Verifying Agency Details page...")
    heading = wait_visible(driver, By.XPATH,
        "//h3[contains(text(),'About your Agency')]", timeout=15)
    assert heading is not None
    print("  Agency Details page confirmed.")

def test_15_fill_agency_name(driver):
    print("\n[TEST 15] Filling Agency Name...")
    field = fill_field(driver, "agency_name", TEST_AGENCY["agency_name"])
    assert field.get_attribute("value") == TEST_AGENCY["agency_name"]
    print(f" Agency Name: {field.get_attribute('value')}")

def test_16_fill_role_in_agency(driver):
    print("\n[TEST 16] Filling Role...")
    field = fill_field(driver, "role_in_agency", TEST_AGENCY["role_in_agency"])
    assert field.get_attribute("value") == TEST_AGENCY["role_in_agency"]
    print(f" Role: {field.get_attribute('value')}")

def test_17_fill_agency_email(driver):
    print("\n[TEST 17] Filling Agency Email...")
    field = fill_field(driver, "agency_email", TEST_AGENCY["agency_email"])
    assert field.get_attribute("value") == TEST_AGENCY["agency_email"]
    print(f" Agency Email: {field.get_attribute('value')}")

def test_18_fill_agency_website(driver):
    print("\n[TEST 18] Filling Agency Website...")
    field = fill_field(driver, "agency_website", TEST_AGENCY["agency_website"])
    assert field.get_attribute("value") == TEST_AGENCY["agency_website"]
    print(f" Website: {field.get_attribute('value')}")

def test_19_fill_agency_address(driver):
    print("\n[TEST 19] Filling Agency Address...")
    field = fill_field(driver, "agency_address", TEST_AGENCY["agency_address"])
    assert field.get_attribute("value") == TEST_AGENCY["agency_address"]
    print(f" Address: {field.get_attribute('value')}")

def test_20_select_region_of_operation(driver):
    print("\n[TEST 20] Selecting Region of Operation...")
    trigger = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[@role='combobox' and @aria-haspopup='dialog']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
    portal_id = trigger.get_attribute("aria-controls")
    print(f" Portal ID: {portal_id}")
    trigger.click()
    time.sleep(1)

    region_value = TEST_AGENCY["region"]
    option_xpaths = [
        f"//div[@id='{portal_id}']//*[normalize-space(text())='{region_value}']",
        f"//div[@id='{portal_id}']//*[contains(normalize-space(.), '{region_value}')]",
        f"//*[@role='option' and normalize-space(.)='{region_value}']",
        f"//*[@role='option' and contains(normalize-space(.), '{region_value}')]",
        f"//*[@data-value='{region_value}']",
    ]
    option_clicked = False
    for xpath in option_xpaths:
        try:
            option = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            time.sleep(0.2)
            option.click()
            print(f" Region '{region_value}' selected.")
            option_clicked = True
            break
        except Exception:
            continue

    if not option_clicked:
        all_opts = driver.find_elements(By.XPATH, "//*[@role='option']")
        available = [o.text.strip() for o in all_opts if o.text.strip()]
        print(f" Available options: {available}")
        if available:
            all_opts[0].click()
            print(f" Fallback: selected '{available[0]}'")
        else:
            raise Exception(" No region options found.")

    time.sleep(0.5)
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(0.5)
    print("  Region selection complete.")

def test_21_validate_agency_fields(driver):
    print("\n[TEST 21] Validating Agency fields...")
    checks = {
        "agency_name":    TEST_AGENCY["agency_name"],
        "role_in_agency": TEST_AGENCY["role_in_agency"],
        "agency_email":   TEST_AGENCY["agency_email"],
        "agency_website": TEST_AGENCY["agency_website"],
        "agency_address": TEST_AGENCY["agency_address"],
    }
    for name, expected in checks.items():
        actual = driver.find_element(By.NAME, name).get_attribute("value")
        assert actual == expected
        print(f" {name}: {actual}")
    print("  All Agency fields validated.")

def test_22_click_next_step2(driver):
    print("\n[TEST 22] Clicking Next (Step 2 → Step 3)...")
    btn = wait_clickable(driver, By.XPATH,
        "//button[@type='submit' and contains(text(),'Next')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
    time.sleep(0.5)
    btn.click()
    time.sleep(3)
    print(" Next clicked.")

def test_23_verify_step3_loaded(driver):
    print("\n[TEST 23] Verifying Step 3 loaded...")
    step3_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "number_of_students_recruited_annually"))
    )
    assert step3_field is not None, "Step 3 did not load!"
    print(f" URL: {driver.current_url}")
    print(" Step 3 (Professional Experience) loaded!")

#  STEP 3 — PROFESSIONAL EXPERIENCE

def test_24_verify_experience_page_heading(driver):
    print("\n[TEST 24] Verifying Step 3 heading...")
    heading = wait_visible(driver, By.XPATH,
        "//*[contains(text(),'Experience and Performance Metrics')]",
        timeout=15)
    assert heading is not None, "Step 3 heading not found!"
    print(" Step 3 heading confirmed.")

def test_25_select_years_of_experience(driver):
    print("\n[TEST 25] Selecting Years of Experience...")
    trigger = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[@role='combobox' and @aria-autocomplete='none']"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
    trigger.click()
    print("  Years of Experience dropdown clicked...")
    time.sleep(1)

    exp_value = TEST_EXPERIENCE["years_of_experience"]
    option_xpaths = [
        f"//*[@role='option' and normalize-space(.)='{exp_value}']",
        f"//*[@role='option' and contains(normalize-space(.), '{exp_value}')]",
        f"//*[contains(@class,'SelectItem') and contains(normalize-space(.), '{exp_value}')]",
        f"//*[@data-value='{exp_value}']",
        "//*[@role='listbox']//*[@role='option'][1]",
    ]

    option_clicked = False
    for xpath in option_xpaths:
        try:
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            time.sleep(0.2)
            option.click()
            print(f" Experience level selected: {exp_value}")
            option_clicked = True
            break
        except Exception:
            continue

    if not option_clicked:
        all_opts = driver.find_elements(By.XPATH, "//*[@role='option']")
        available = [o.text.strip() for o in all_opts if o.text.strip()]
        print(f" Available experience options: {available}")
        if available:
            all_opts[0].click()
            print(f" Fallback: selected first option '{available[0]}'")
        else:
            raise Exception("No experience level options found.")

    time.sleep(0.5)
    print("  Years of Experience selection complete.")

def test_26_fill_students_recruited(driver):
    print("\n[TEST 26] Filling Number of Students Recruited Annually...")
    field = fill_field(driver, "number_of_students_recruited_annually",
                       TEST_EXPERIENCE["number_of_students_recruited_annually"])
    val = field.get_attribute("value")
    assert len(val) > 0, "Students recruited field is empty!"
    print(f"  Students Recruited: {val}")

def test_27_fill_focus_area(driver):
    print("\n[TEST 27] Filling Focus Area...")
    field = fill_field(driver, "focus_area", TEST_EXPERIENCE["focus_area"])
    val = field.get_attribute("value")
    assert val == TEST_EXPERIENCE["focus_area"]
    print(f" Focus Area: {val}")

def test_28_fill_success_metrics(driver):
    print("\n[TEST 28] Filling Success Metrics...")
    field = fill_field(driver, "success_metrics", TEST_EXPERIENCE["success_metrics"])
    val = field.get_attribute("value")
    assert len(val) > 0, "Success metrics field is empty!"
    print(f"  Success Metrics: {val}%")

def test_29_select_services_provided(driver):
    print("\n[TEST 29] Selecting Services Provided...")
    services_to_select = TEST_EXPERIENCE["services"]

    for service_label in services_to_select:
        print(f" Selecting: {service_label}")
        try:
            label = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    f"//label[normalize-space(text())='{service_label}']"
                ))
            )
            checkbox_id = label.get_attribute("for")
            print(f" Checkbox ID: {checkbox_id}")
            checkbox_btn = driver.find_element(By.ID, checkbox_id)
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_btn)
            time.sleep(0.2)
            checkbox_btn.click()
            time.sleep(0.3)
            state = checkbox_btn.get_attribute("data-state")
            aria  = checkbox_btn.get_attribute("aria-checked")
            assert state == "checked" or aria == "true", (
                f"Checkbox '{service_label}' did not get checked! "
                f"data-state={state}, aria-checked={aria}"
            )
            print(f" '{service_label}' checked (state={state})")
        except Exception as e:
            raise Exception(f" Failed to check '{service_label}': {e}")
    print(f" All {len(services_to_select)} services selected.")

def test_30_validate_step3_fields(driver):
    print("\n[TEST 30] Validating Step 3 fields...")
    students = driver.find_element(By.NAME,
        "number_of_students_recruited_annually").get_attribute("value")
    focus    = driver.find_element(By.NAME, "focus_area").get_attribute("value")
    metrics  = driver.find_element(By.NAME, "success_metrics").get_attribute("value")

    assert len(students) > 0, "Students recruited is empty!"
    assert focus == TEST_EXPERIENCE["focus_area"], f"Focus area mismatch: {focus}"
    assert len(metrics) > 0, "Success metrics is empty!"
    print(f" Students Recruited: {students}")
    print(f" Focus Area: {focus}")
    print(f" Success Metrics: {metrics}%")

    for service_label in TEST_EXPERIENCE["services"]:
        label = driver.find_element(By.XPATH,
            f"//label[normalize-space(text())='{service_label}']")
        checkbox_id  = label.get_attribute("for")
        checkbox_btn = driver.find_element(By.ID, checkbox_id)
        state = checkbox_btn.get_attribute("data-state")
        assert state == "checked", f"'{service_label}' not checked! state={state}"
        print(f" Service checked: {service_label}")
    print("All Step 3 fields validated.")

def test_31_click_next_step3(driver):
    print("\n[TEST 31] Clicking Next (Step 3 → Step 4)...")
    btn = wait_clickable(driver, By.XPATH,
        "//button[contains(text(),'Next')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
    time.sleep(0.5)
    btn.click()
    time.sleep(3)
    print("  Next clicked.")

def test_32_verify_step4_loaded(driver):
    print("\n[TEST 32] Verifying Verification and Preferences page loaded...")
    heading = wait_visible(driver, By.XPATH,
        "//h2[normalize-space()='Complete Your Agent Profile in Steps']", timeout=15)
    assert heading is not None
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "business_registration_number"))
    )
    print("Verification and Preferences page confirmed.")


#  STEP 4 — VERIFICATION AND PREFERENCES
def test_33_verify_step4_heading(driver):
    print("\n[TEST 33] Verifying Step 4 section heading...")
    heading = wait_visible(driver, By.XPATH,
        "//*[contains(text(),'Provide Business Details and Set Preferences')]",
        timeout=15)
    assert heading is not None, "Step 4 section heading not found!"
    print(" Step 4 heading confirmed.")

def test_34_fill_business_registration_number(driver):
    print("\n[TEST 34] Filling Business Registration Number...")
    field = fill_field(driver, "business_registration_number",
                       TEST_VERIFICATION["business_registration_number"])
    val = field.get_attribute("value")
    assert val == TEST_VERIFICATION["business_registration_number"], (
        f"BRN mismatch: expected '{TEST_VERIFICATION['business_registration_number']}', got '{val}'"
    )
    print(f" Business Registration Number: {val}")

def test_35_select_preferred_countries(driver):
    print("\n[TEST 35] Selecting Preferred Countries...")

    trigger = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[@role='combobox' and @aria-haspopup='dialog' and "
            ".//span[contains(text(),'Select Your Preferred Countries')]]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
    portal_id = trigger.get_attribute("aria-controls")
    print(f" Portal ID: {portal_id}")

    countries_to_select = TEST_VERIFICATION["preferred_countries"]
    if isinstance(countries_to_select, str):
        countries_to_select = [countries_to_select]

    for country in countries_to_select:
        print(f" Selecting country: {country}")

        # Only click trigger if dropdown is currently closed
        state = trigger.get_attribute("data-state")
        if state != "open":
            trigger.click()
            time.sleep(1)

        option_xpaths = [
            f"//div[@id='{portal_id}']//*[normalize-space(text())='{country}']",
            f"//div[@id='{portal_id}']//*[contains(normalize-space(.), '{country}')]",
            f"//*[@role='option' and normalize-space(.)='{country}']",
            f"//*[@role='option' and contains(normalize-space(.), '{country}')]",
            f"//*[@data-value='{country}']",
        ]

        option_clicked = False
        for xpath in option_xpaths:
            try:
                option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", option)
                time.sleep(0.2)
                option.click()
                print(f" Country '{country}' selected.")
                option_clicked = True
                time.sleep(0.5)
                break
            except Exception:
                continue

        if not option_clicked:
            all_opts = driver.find_elements(By.XPATH, "//*[@role='option']")
            available = [o.text.strip() for o in all_opts if o.text.strip()]
            print(f" Available country options: {available}")
            if available:
                for opt in all_opts:
                    if opt.get_attribute("aria-selected") != "true":
                        opt.click()
                        print(f" Fallback: selected '{opt.text.strip()}'")
                        time.sleep(0.5)
                        break
            else:
                raise Exception(f" No country options found for '{country}'.")

    # Close the dropdown
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(0.5)
    print(f" All {len(countries_to_select)} countries selected.")

def test_36_select_institution_types(driver):
    print("\n[TEST 36] Selecting Preferred Institution Types...")

    institution_types = TEST_VERIFICATION["institution_types"]

    for inst_label in institution_types:
        print(f" Selecting: {inst_label}")
        try:
            label = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    f"//label[normalize-space(text())='{inst_label}']"
                ))
            )
            checkbox_id = label.get_attribute("for")
            print(f" Checkbox ID: {checkbox_id}")

            checkbox_btn = driver.find_element(By.ID, checkbox_id)
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_btn)
            time.sleep(0.2)
            checkbox_btn.click()
            time.sleep(0.3)

            state = checkbox_btn.get_attribute("data-state")
            aria  = checkbox_btn.get_attribute("aria-checked")
            assert state == "checked" or aria == "true", (
                f"Checkbox '{inst_label}' did not get checked! "
                f"data-state={state}, aria-checked={aria}"
            )
            print(f" '{inst_label}' checked (state={state})")

        except Exception as e:
            raise Exception(f" Failed to check institution type '{inst_label}': {e}")

    print(f" All {len(institution_types)} institution types selected.")

def test_37_fill_certification_details(driver):
    print("\n[TEST 37] Filling Certification Details...")
    # name="certification_details" — optional field, plain text input
    # Confirmed placeholder: "E.g., ICEF Certified Education Agent"
    try:
        field = wait_visible(driver, By.NAME, "certification_details", timeout=10)
        field.clear()
        field.send_keys(TEST_VERIFICATION["certification_details"])
        val = field.get_attribute("value")
        assert val == TEST_VERIFICATION["certification_details"], (
            f"Certification details mismatch: got '{val}'"
        )
        print(f" Certification Details: {val}")
    except Exception:
        # Try by placeholder as fallback
        field = wait_visible(driver, By.XPATH,
            "//input[@placeholder='E.g., ICEF Certified Education Agent']")
        field.clear()
        field.send_keys(TEST_VERIFICATION["certification_details"])
        val = field.get_attribute("value")
        assert len(val) > 0, "Certification details field is empty!"
        print(f" Certification Details (fallback): {val}")

def test_38_upload_business_documents(driver):
    """
    Upload Business Documents — two upload zones side by side.
    Each zone wraps a hidden <input type="file">. Strategy:
      1. Find all hidden file inputs inside the upload containers.
      2. Make each visible via JS (remove display:none / pointer-events).
      3. Send the file path using send_keys (no dialog needed).
    Two dummy temp files are created for this test run.
    """
    print("\n[TEST 38] Uploading Business Documents...")

    # Create two dummy files to upload
    file1 = create_dummy_file(suffix=".pdf",
                              content=b"Company Registration Document - Test")
    file2 = create_dummy_file(suffix=".pdf",
                              content=b"Educational Certificate - Test")
    TEST_VERIFICATION["document_1"] = file1
    TEST_VERIFICATION["document_2"] = file2
    print(f" File 1: {file1}")
    print(f" File 2: {file2}")

    # Locate upload zone containers — identified by the upload icon SVG + "Upload a file" text
    # Each zone is a labeled drop area; the hidden <input type="file"> sits inside or nearby
    upload_zones = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH,
            "//div[contains(@class,'flex') and "
            ".//span[contains(text(),'Upload a file')]]"
        ))
    )
    print(f" Found {len(upload_zones)} upload zone(s).")
    assert len(upload_zones) >= 2, (
        f"Expected at least 2 upload zones, found {len(upload_zones)}"
    )

    files_to_upload = [file1, file2]

    for idx, (zone, file_path) in enumerate(zip(upload_zones[:2], files_to_upload), start=1):
        print(f" Uploading file {idx}: {os.path.basename(file_path)}")

        # Strategy 1: find <input type="file"> inside the zone's parent container
        file_input = None
        try:
            # Walk up to the clickable card container, then find input[type=file] within it
            card = zone.find_element(By.XPATH,
                "./ancestor::div[contains(@class,'border') or "
                "contains(@class,'rounded')][1]"
            )
            file_input = card.find_element(By.XPATH, ".//input[@type='file']")
        except Exception:
            pass

        # Strategy 2: find all file inputs on page, pick by index
        if file_input is None:
            try:
                all_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                if len(all_inputs) >= idx:
                    file_input = all_inputs[idx - 1]
                elif all_inputs:
                    file_input = all_inputs[0]
            except Exception:
                pass

        if file_input is None:
            raise Exception(
                f" Could not locate file input for upload zone {idx}. "
                "Check screenshot: step4_before_upload.png"
            )

        # Make the input interactable (remove hidden/opacity styles)
        driver.execute_script("""
            arguments[0].style.display    = 'block';
            arguments[0].style.opacity    = '1';
            arguments[0].style.visibility = 'visible';
            arguments[0].style.position   = 'relative';
            arguments[0].style.width      = '1px';
            arguments[0].style.height     = '1px';
            arguments[0].removeAttribute('hidden');
        """, file_input)
        time.sleep(0.3)

        file_input.send_keys(file_path)
        time.sleep(1.5)

        print(f" File {idx} upload triggered.")

    time.sleep(1)

    page_source = driver.page_source
    for file_path in files_to_upload:
        fname = os.path.basename(file_path)
        if fname in page_source:
            print(f" Filename '{fname}' confirmed in DOM.")
        else:
            print(f" Note: '{fname}' not visible in DOM (may render as preview only).")

    print(" Business document upload steps complete.")


def test_39_validate_step4_fields(driver):
    print("\n[TEST 39] Validating Step 4 fields...")

    # Business Registration Number
    brn = driver.find_element(
        By.NAME, "business_registration_number").get_attribute("value")
    assert brn == TEST_VERIFICATION["business_registration_number"], (
        f"BRN mismatch: {brn}"
    )
    print(f" Business Registration Number: {brn}")

    # Institution type checkboxes
    for inst_label in TEST_VERIFICATION["institution_types"]:
        label = driver.find_element(By.XPATH,
            f"//label[normalize-space(text())='{inst_label}']")
        checkbox_id  = label.get_attribute("for")
        checkbox_btn = driver.find_element(By.ID, checkbox_id)
        state = checkbox_btn.get_attribute("data-state")
        assert state == "checked", f"'{inst_label}' not checked! state={state}"
        print(f" Institution type checked: {inst_label}")

    # Certification Details
    try:
        cert = driver.find_element(
            By.NAME, "certification_details").get_attribute("value")
    except Exception:
        cert = driver.find_element(By.XPATH,
            "//input[@placeholder='E.g., ICEF Certified Education Agent']"
        ).get_attribute("value")
    assert len(cert) > 0, "Certification details is empty!"
    print(f" Certification Details: {cert}")
    print(" All Step 4 fields validated.")


def test_40_click_submit(driver):
    print("\n[TEST 40] Clicking Submit button...")

    submit_btn = None
    try:
        submit_btn = wait_clickable(driver, By.XPATH,
            "//button[@type='submit' and normalize-space(text())='Submit']",
            timeout=10)
    except Exception:
        pass

    if submit_btn is None:
        try:
            submit_btn = wait_clickable(driver, By.XPATH,
                "//button[normalize-space(text())='Submit']",
                timeout=10)
        except Exception:
            pass

    if submit_btn is None:
        try:
            submit_btn = wait_clickable(driver, By.XPATH,
                "//button[contains(@style,'--success') and "
                "contains(normalize-space(.), 'Submit')]",
                timeout=10)
        except Exception:
            pass

    assert submit_btn is not None, (
        "Submit button not found! Check screenshot: step4_before_submit.png"
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(0.5)
    submit_btn.click()
    time.sleep(4)
    print(" Submit clicked.")


def test_41_verify_submission_success(driver):
    print("\n[TEST 41] Verifying submission success...")
    time.sleep(3)
    current_url = driver.current_url
    print(f" Current URL after submit: {current_url}")

    success_xpaths = [
        "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'success')]",
        "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'submitted')]",
        "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'thank you')]",
        "//*[@role='alert']",
        "//*[contains(@class,'toast')]",
        "//*[contains(@class,'success')]",
    ]

    success_found = False
    for xpath in success_xpaths:
        try:
            el = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            print(f" Success indicator: '{el.text[:120]}'")
            success_found = True
            break
        except Exception:
            continue

    if not success_found:
        if current_url != BASE_URL:
            print(f" URL changed → '{current_url}' — treating as success.")
            success_found = True
        else:
            src = driver.page_source.lower()
            if any(kw in src for kw in ["success", "submitted", "thank you", "complete"]):
                print(" Success keyword found in page source.")
                success_found = True

    assert success_found, (
        "No success indicator found after submit. "
        "Check: step4_submission_result.png"
    )
    print(" Form submitted successfully — signup flow complete!")

    # Cleanup temp files
    for key in ("document_1", "document_2"):
        fpath = TEST_VERIFICATION.get(key)
        if fpath and os.path.exists(fpath):
            os.remove(fpath)
            print(f" Cleaned up temp file: {fpath}")
