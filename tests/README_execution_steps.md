# Authorized Partner Signup Automation

## Overview

This project automates the complete signup flow of the Authorized Partner Portal using Selenium WebDriver, Python, and Pytest.

Application URL:
https://authorized-partner.vercel.app/

The automation covers:

* Step 1: Account Setup
* Email OTP Verification
* Step 2: Agency Details
* Step 3: Professional Experience
* Step 4: Verification & Preferences
* Document Upload
* Final Form Submission

No manual intervention is required during execution.


# Project Structure

Virt_Task/tests/
│
├── signup_automation_script.py
├── README_execution_steps.md
├── test_report.pdf
├── demo_video.mp4

```


# Technology Stack

| Component      | Version                                    |
| -------------- | ------------------------------------------ |
| Python         | 3.10+                                      |
| Selenium       | Latest                                     |
| Pytest         | Latest                                     |
| Chrome Browser | Latest                                     |
| ChromeDriver   | Managed automatically by webdriver-manager |


# Prerequisites

Install:

* Python 3.10 or above
* Google Chrome Browser
* Gmail Account with App Password enabled


# Installation

Clone repository:

```bash
git clone https://github.com/sushanv10/Virt_QA_Task.git
cd Virt_QA_Task
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

# Required Python Packages

```bash
pip install selenium
pip install pytest
pip install webdriver-manager
```

# Test Data

The script automatically generates a unique email address using Gmail aliasing.

```
Static Test Data:

```text
First Name: Test
Last Name: User
Phone Number: 9848769773
Password: TestPass@123
Agency Name: Test Agency Nepal
Role: QA Engineer
```

# Gmail OTP Configuration

Update the following variables before execution:

```python
GMAIL_ADDRESS = "yourgmail@gmail.com"
GMAIL_APP_PASS = "your-app-password"
```

Generate App Password:

1. Enable Two-Factor Authentication.
2. Open Google Account Settings.
3. Navigate to Security → App Passwords.
4. Create a Mail App Password.
5. Replace GMAIL_APP_PASS with generated password.


# Running the Test

Execute all tests:

```bash
pytest -v signup_automation_script.py
```

Run with detailed logs:

```bash
pytest -v -s signup_automation_script.py
```

Generate HTML report (optional):

```bash
pip install pytest-html
pytest --html=report.html
```


# Expected Result

The automation should:

✓ Open signup page

✓ Fill account details

✓ Retrieve OTP automatically from Gmail

✓ Verify OTP

✓ Complete Agency Details form

✓ Complete Professional Experience form

✓ Upload documents

✓ Submit final registration

✓ Verify successful submission

---

# Deliverables

Included in repository:

* signup_automation_script.py
* README_execution_steps.md
* test_report.pdf
* demo_video.mp4


# Test Summary

| Metric           | Result |
| ---------------- | ------ |
| Total Test Cases | 41     |
| Passed           | 41     |
| Failed           | 0      |
| Success Rate     | 100%   |


# Author

Submitted as QA Automation Task for Vrit Technologies.
