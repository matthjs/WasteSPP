import pickle
from typing import Set, Tuple, List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from componentannotator.componentannotator import ComponentAnnotator
from loguru import logger

def waste_service_links():
    """
    This function visits the wasteservice webpage and extracts all the GitHub projects from it
    as (name, url) pairs.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    # Navigate to the webpage
    driver.get('https://wasteservice.github.io/')

    driver.implicitly_wait(2)

    multi_select = driver.find_element(by=By.CSS_SELECTOR, value="select")

    select = Select(multi_select)
    select.select_by_value("-1")            # This is to get the webpage to display ALL projects.

    table = driver.find_element(By.CSS_SELECTOR, 'table')

    # Find the header row of the table
    header_row = table.find_element(By.TAG_NAME, 'thead').find_element(By.TAG_NAME, 'tr')

    # Find the index of the "Project" column
    columns = header_row.find_elements(By.TAG_NAME, 'th')

    project_column_index = None
    for index, column in enumerate(columns):
        if column.text == 'Project':
            project_column_index = index
            break

    projects = set()

    # Get project name and project url pairs.
    if project_column_index is not None:
        # Find all rows in the table body
        rows = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')

        # Extract and print information from the "Project" column
        for row in rows:
            # Find all cells in the row
            cells = row.find_elements(By.TAG_NAME, 'td')
            link = row.find_elements(By.TAG_NAME, "a")
            # Check if the index is within the range of the cells
            if project_column_index < len(cells):
                if cells[1].text != "tohu-generator" and cells[1].text != "Usherb-IFT585-TP1-Link-layer":
                    projects.add( (cells[1].text, link[1].get_attribute("href")) )

    projects_list = list(projects)
    # Extract and print column names
    with open('projects.pkl', 'wb') as file:
        pickle.dump(projects_list, file)
    # Close the browser
    driver.quit()

def load_projects():
    # Load the projects dictionary from the pickle file
    with open('./src/projects.pkl', 'rb') as pickle_file:
        loaded_projects = pickle.load(pickle_file)

    # Print or use the loaded projects dictionary
    return loaded_projects

def process(tuples_param: Set[Tuple], batch_size=50):
    annot = ComponentAnnotator("java")
    #print(len(tuples_param))
    tuples = list(tuples_param)
    for i in range(0, len(tuples), batch_size):
        logger.debug(i)
        batch = tuples[i:i + batch_size]
        frames = annot.annotate_project_list(batch)
        if len(frames) > 0:
            pd.concat(frames).to_csv(f'output{i}.csv', index=False)
            #print(batch)

if __name__ == "__main__":
    #ComponentAnnotator("java").annotate_project("tohu-generator", "https://github.com/rah/tohu-generator")
    #waste_service_links()
    #projects = load_projects()

    #process(projects)
    #ComponentAnnotator("java").annotate_project_list()

    #logger.debug("Passed A-1 (assuming this is run through docker)")
    #logger.debug("Passed A-4 (logging is active)")
    #logger.debug("Passed A-6 (pipeline and auto-fl run in separate containers)")
    #logger.debug("Passed A-17 (databases are running in separate containers)")
    #frames = ComponentAnnotator("java").annotate_projects(5)
    #df = pd.concat(frames)
    #print(df)
    #df.to_csv('output.csv', index=False)
    df = ComponentAnnotator("java").annotate_project("OOP_final_project", "https://github.com/matthjs/OOP_final_project.git")
    df.to_csv("oop.csv", index=False)