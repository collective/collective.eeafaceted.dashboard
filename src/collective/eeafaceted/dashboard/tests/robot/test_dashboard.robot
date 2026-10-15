*** Settings ***
Documentation  The faceted dashboard (demo profile): collection widget, results table and collection counts.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  dashboard.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
The dashboard shows its collections and the results table
    Open the dashboard
    The collection is selected  Every elements
    The table columns are  Title  Creator  Created on  Modified on  State
    The results list  Dashboard  Folder  My elements

Selecting a collection updates the results and the table columns
    Create a page  folder  Alpha page
    Create a collection  dashboard  Pages  ['pretty_link', 'CreationDate']
    Open the dashboard
    The results list  Dashboard
    Select the collection  Pages
    The collection is selected  Pages
    The table columns are  Title  Created on
    The results list  Alpha page
    The results do not list  Dashboard

The collection counts are refreshed after a faceted query
    Open the dashboard
    The collection shows its number of items  Expired elements  0
    Create an expired page  folder  Old page
    Select the collection  My elements
    The collection shows its number of items  Expired elements  1
    The collection shows its number of items  Elements to review  0
