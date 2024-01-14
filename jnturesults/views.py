from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'index.html')

# views.py
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv
import time,os
def scrape_exam_data():
    # Get the absolute path to the chromedriver executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_driver_path = os.path.join(current_dir, 'chromedriver.exe')

    service = ChromeService(executable_path=chrome_driver_path)
    browser = webdriver.Chrome(service=service)

    try:
        browser.get('https://results.jntukucev.ac.in/')
        WebDriverWait(browser, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'resultBlockLink')))
        exam_data = []

        while True:
            link_elements = browser.find_elements(By.CLASS_NAME, 'resultBlockLink')
            for link_element in link_elements:
                exam_name = link_element.find_element(By.CLASS_NAME, 'examListHolderOne').text.strip()
                link = link_element.get_attribute('href')
                exam_data.append({'ExamName': exam_name, 'Link': link})

            browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)

            no_results_found = browser.find_elements(By.XPATH, '//div[@id="load-more"]//a[text()="No more results found"]')
            if no_results_found:
                break

    except Exception as e:
        print(f'Error: {str(e)}')
        exam_data = []

    finally:
        browser.quit()

    return exam_data

def home(request):
    exam_data = scrape_exam_data()
    exam_names = [exam['ExamName'] for exam in exam_data]
    context = {'exam_names': exam_names, 'exam_data': exam_data}
    return render(request, 'index.html', context)
# views.py
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv
import pandas as pd# Import necessary libraries and modules
from selenium.webdriver.chrome.options import Options 
def scrape_data(browser, roll_number, df):
    try:
        print(f'Scraping data for Roll Number {roll_number}')

        # Wait for the page to load
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.hallticket')))
        
        # Enter the roll number
        hall_ticket_input = browser.find_element('css selector', '.hallticket')
        hall_ticket_input.clear()
        hall_ticket_input.send_keys(roll_number)

        # Adding a delay after entering the roll number
        time.sleep(1)

        print('Waiting for the results to load...')
        # Wait for the results to load
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table .row.header .cell')))
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table:nth-child(2) .row.header .cell')))

        # Extract main data from the page
        main_data = {}
        main_header_cells = browser.find_elements('css selector', '.table .row.header .cell')
        main_data_cells = browser.find_elements('css selector', '.table .row:not(.header) .cell')

        main_header_values = [cell.text.strip() for cell in main_header_cells]
        main_data_values = [cell.text.strip() for cell in main_data_cells]

        for header, value in zip(main_header_values, main_data_values):
            main_data[header] = value

        # Extract additional subject-wise data
        subjects_data = []
        for _ in range(3):  # Retry up to 3 times in case of StaleElementReferenceException
            try:
                subject_rows = browser.find_elements('css selector', '.table:nth-child(2) .row:not(.header)')
                for subject_row in subject_rows:
                    subject_cells = subject_row.find_elements('css selector', '.cell')
                    subject_data = [cell.text.strip() for cell in subject_cells]
                    subjects_data.append(subject_data)
                break  # If successful, break out of the loop
            except StaleElementReferenceException:
                print('StaleElementReferenceException. Retrying...')
                time.sleep(1)  # Wait for 2 seconds before retrying
        row_data = [main_data['HallTicket'], main_data['Full Name'], main_data['Branch'],main_data['SGPA'], main_data['Credits'], main_data['Status']]
        for subject_data in subjects_data:
            row_data.extend(subject_data[1:])  # Skip the subject code

        # Concatenate the data to the DataFrame
        df = pd.concat([df, pd.DataFrame([row_data], columns=df.columns)], ignore_index=True)

    except TimeoutException:
        print(f'Timeout for roll number {roll_number}. Skipping.')

    return df
def findlen(browser, roll_number):
    try:
        print(f'Scraping data for Roll Number {roll_number}')

        # Wait for the page to load
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.hallticket')))
        
        # Enter the roll number
        hall_ticket_input = browser.find_element('css selector', '.hallticket')
        hall_ticket_input.clear()
        hall_ticket_input.send_keys(roll_number)

        # Adding a delay after entering the roll number
        time.sleep(1)

        print('Waiting for the results to load...')
        # Wait for the results to load
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table .row.header .cell')))
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table:nth-child(2) .row.header .cell')))

        # Extract main data from the page
        main_data = {}
        main_header_cells = browser.find_elements('css selector', '.table .row.header .cell')
        main_data_cells = browser.find_elements('css selector', '.table .row:not(.header) .cell')

        main_header_values = [cell.text.strip() for cell in main_header_cells]
        main_data_values = [cell.text.strip() for cell in main_data_cells]

        for header, value in zip(main_header_values, main_data_values):
            main_data[header] = value

        # Extract additional subject-wise data
        subjects_data = []
        for _ in range(3):  # Retry up to 3 times in case of StaleElementReferenceException
            try:
                subject_rows = browser.find_elements('css selector', '.table:nth-child(2) .row:not(.header)')
                for subject_row in subject_rows:
                    subject_cells = subject_row.find_elements('css selector', '.cell')
                    subject_data = [cell.text.strip() for cell in subject_cells]
                    subjects_data.append(subject_data)
                break  # If successful, break out of the loop
            except StaleElementReferenceException:
                print('StaleElementReferenceException. Retrying...')
                time.sleep(1)  # Wait for 2 seconds before retrying
        row_data = [main_data['HallTicket'], main_data['Full Name'], main_data['Branch'],main_data['SGPA'], main_data['Credits'], main_data['Status']]
        for subject_data in subjects_data:
            row_data.extend(subject_data[1:])
    except TimeoutException:
        print(f'Timeout for roll number {roll_number}. Skipping.')
    
    return len(subjects_data)
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
def results(request):
    #exam_link = request.GET.get('link', '')
    if request.method == 'POST':
        # Handle the form submissions and process the roll number inputs here
        normal_roll_prefix = request.POST.get('input1', '')
        normal_roll_start = int(request.POST.get('input2', 0))
        normal_roll_end = int(request.POST.get('input3', 0))
        lateral_roll_prefix = request.POST.get('input4', '')
        lateral_roll_start = int(request.POST.get('input5', 0))
        lateral_roll_end = int(request.POST.get('input6', 0))
        exam_link = request.POST.get('exam_link', '')

    # Generate roll numbers based on the inputs
    normals = [f'{normal_roll_prefix}{i:04d}' for i in range(normal_roll_start, normal_roll_end + 1)]
    laterals = [f'{lateral_roll_prefix}{i:04d}' for i in range(lateral_roll_start, lateral_roll_end + 1)]
    roll_numbers = normals + laterals


    current_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_driver_path = os.path.join(current_dir, 'chromedriver.exe')
    service = ChromeService(executable_path=chrome_driver_path)
    browser = webdriver.Chrome(service=service)

    try:
        browser.get(exam_link)
        columns = ['HallTicket', 'Full Name', 'Branch', 'Credits','SGPA', 'Status']
        length=findlen(browser,roll_numbers[0])
        print(length)
        subjects_data = [['Subject Code', 'Subject', 'C', 'GP', 'G'] for _ in range(length)]
        for subject_data in subjects_data:
            columns.extend(subject_data[1:])

        df = pd.DataFrame(columns=columns)
        for roll_number in roll_numbers:
            df = scrape_data(browser, roll_number, df)

        df.to_csv('results.csv', index=False)
        print('Data saved to results.csv')

    finally:
        browser.quit()

    html_table = df.to_html(classes='table table-bordered table-hover', index=False, escape=False)
    context = {'html_table': html_table}
    return render(request, 'results.html', context)