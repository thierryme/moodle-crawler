#!/bin/env python2

from selenium import webdriver
import getpass
import requests
from path import path


def download_file(url, filename="", filepath=".", cookies=None):
    if filename == "":
        filename = url.split('/')[-1]

    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, cookies=cookies)

    if filepath.isdir() == False:
        filepath.makedirs()

    with open(filepath/filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian



folder_path = path("./result_files")
user = raw_input("user: ")
passwd = getpass.getpass()



driver = webdriver.Firefox()
# Service selection
# Here I had to select my school among others 
driver.get("https://cyberlearn.hes-so.ch/auth/shibboleth/index.php")
driver.find_element_by_id('userIdPSelection_iddtext').click()
driver.find_element_by_id('userIdPSelection_iddtext').send_keys('HES-SO : UAS Western Switzerland')
driver.find_element_by_name('Select').click()

# Login page (https://cas.ensicaen.fr/cas/login?service=https%3A%2F%2Fshibboleth.ensicaen.fr%2Fidp%2FAuthn%2FRemoteUser)
# Fill the login form and submit it
driver.find_element_by_id('username').send_keys(user)
driver.find_element_by_id('password').send_keys(passwd)
driver.find_element_by_id('j_loginform').submit()

## Now connected to the home page

print(driver.get_cookies())

# get the session cookies for using them to download files
all_cookies = driver.get_cookies()

cookies = {}  
for s_cookie in all_cookies:
    cookies[s_cookie["name"]]=s_cookie["value"]


# retreive every html elements wich contains a link to a course
courses_elems = driver.find_elements_by_xpath("//div[@class='course_title']/h2[@class='title']/a")

courses = []
for course in courses_elems:
    print(course.text)
    # save course title and link to it
    courses.append((course.text, course.get_attribute('href')))

# for every courses
for name,link in courses:

    #go to course link
    driver.get(link)

    # retrieve elements wich contains link to course's document
    docs_elems = driver.find_elements_by_xpath("//section[@id='region-main']//a")

    docs = []

    # for every document of the course
    for doc in docs_elems:
        link = doc.get_attribute('href')
        # verify that the link points to a downloadable ressource
        if "cyberlearn.hes-so.ch/mod/resource" in link:
            # save document name and link to it
            redirection = True
            docs.append((doc.text,link, redirection))

        elif "cyberlearn.hes-so.ch" in link and "mod_folder/content" in link:
            redirection = False
            docs.append((doc.text,link, redirection))

    # for every document link
    for doc_name, doc_link, redirection in docs:
        print(doc_name)
        print(": {}\n".format(doc_link))

        if redirection:
            # when getting the url a redirection append to a page with another document url
            driver.get(doc_link)
            # get the document url
            file_to_dl = driver.find_element_by_xpath("//section[@id='region-main']//a")

            print(file_to_dl.get_attribute('href'))
            download_file(file_to_dl.get_attribute('href'), path(file_to_dl.text), folder_path/name, cookies)

        else:
            download_file(doc_link, path(doc_name), folder_path/name, cookies)

