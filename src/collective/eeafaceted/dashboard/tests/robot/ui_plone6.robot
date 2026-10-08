*** Settings ***
Documentation  Plone 6 Classic UI keywords. Same keyword names and arguments as ui_plone4.robot.
...            Robot Framework 3.0 syntax: shared with the Plone 4.3 (Python 2) environment.
...            Selectors checked on Plone 6.1 (collective.contact.contactlist).
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ***
${MODAL}  css=.modal-dialog
${ERROR_PAGE_TEXT}  there seems to be an error
${NOT_FOUND_TEXT}  This page does not seem to exist
${HEADING}  css=#content > header > h1


*** Keywords ***
Log in with the login form
    [Documentation]  Real login (creates the user folder), unlike autologin
    [Arguments]  ${username}  ${password}
    Disable autologin
    Go to  ${PLONE_URL}/login
    Input text  css=#__ac_name  ${username}
    Input password  css=#__ac_password  ${password}
    Click button  css=#buttons-login
    Wait until page contains element  css=#personaltools-menulink

Click the content action
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions-${action_id}
    Click element  css=#plone-contentmenu-actions-${action_id}

The content action is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions ul
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-actions-${action_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-actions-${action_id}

Open the add menu
    Click element  css=#plone-contentmenu-factories > a
    Wait until element is visible  css=#plone-contentmenu-factories ul

The personal action links to
    [Documentation]  Item of the user menu (user actions), by action id
    [Arguments]  ${action_id}  ${url}
    Element attribute value should be  css=#personaltools-${action_id}  href  ${url}

The personal action is not available
    [Arguments]  ${action_id}
    Page should not contain element  css=#personaltools-${action_id}

The modal is open
    [Documentation]  Overlay (Plone 4) or modal (Plone 6) showing a form
    Wait until element is visible  ${MODAL} form

Modal element
    [Documentation]  Locator of the element with this id inside the modal
    ...              (an argument starting with # would be a robot comment)
    [Arguments]  ${id}
    [Return]  ${MODAL} [id="${id}"]

Save the modal
    Click button  css=.modal-footer #form-buttons-save

Cancel the modal
    Click button  css=.modal-footer #form-buttons-cancel

The modal is closed
    Wait until page does not contain element  ${MODAL}

The status message contains
    [Arguments]  ${text}
    Wait until element contains  css=.portalMessage  ${text}

The page is not an error
    Page should not contain  ${ERROR_PAGE_TEXT}

The page is not found
    Page should contain  ${NOT_FOUND_TEXT}

The edit link is not available
    Page should not contain element  css=#contentview-edit

Click the add menu item
    [Documentation]  Item of the Add new... menu (factories), by its id: the normalized portal type
    ...              NOT CHECKED YET on Plone 6 (id from plone.app.contentmenu 3 contentmenu.pt)
    [Arguments]  ${item_id}
    Click element  css=#plone-contentmenu-factories a#${item_id}

Input the title
    [Documentation]  Title field of a Dexterity add or edit form (IDublinCore behavior). NOT CHECKED YET on Plone 6
    [Arguments]  ${title}
    Wait until element is visible  css=#form-widgets-IDublinCore-title
    Input text  css=#form-widgets-IDublinCore-title  ${title}

Save the add form
    Click button  css=#form-buttons-save

Add the query criterion
    [Documentation]  Collection query widget (pat-querystring): criterion of the empty last row, by title
    ...              (from collective.compoundcriterion, checked on Plone 6)
    [Arguments]  ${criterion}
    # a click scrolls the element to the bottom of the window, under the sticky form buttons
    Set window size  1280  2000
    ${index}=  Set variable  xpath=(//div[contains(@class, "querystring-criteria-wrapper")])[last()]//div[contains(@class, "querystring-criteria-index")]//a[contains(@class, "select2-choice")]
    Wait until element is visible  ${index}
    Click element  ${index}
    Wait until element is visible  css=#select2-drop input.select2-input
    Input text  css=#select2-drop input.select2-input  ${criterion}
    Wait until element is visible  css=#select2-drop .select2-match
    Click element  css=#select2-drop .select2-match

Select the query value
    [Documentation]  Value of the last added MultipleSelectionWidget criterion (select2 tags), by title
    ...              (from collective.compoundcriterion, checked on Plone 6)
    [Arguments]  ${value}
    ${values}=  Set variable  xpath=(//div[contains(@class, "querystring-criteria-value")]//ul[contains(@class, "select2-choices")])[last()]
    Wait until element is visible  ${values}
    Click element  ${values}
    Wait until element is visible  css=.select2-input.select2-focused
    Input text  css=.select2-input.select2-focused  ${value}
    Wait until element is visible  xpath=//*[@id="select2-drop"]//*[@class="select2-match"][normalize-space()="${value}"]
    Click element  xpath=//*[@id="select2-drop"]//*[@class="select2-match"][normalize-space()="${value}"]

Add the portlet
    [Documentation]  Portlet added to the left column of the content at ${path} (@@manage-portlets), by its title.
    ...              Its add form (z3c.form) is saved as it is. NOT CHECKED YET on Plone 6
    [Arguments]  ${path}  ${title}
    Go to  ${PLONE_URL}/${path}/@@manage-portlets
    Select from list by label  css=#portletmanager-plone-leftcolumn select[name=":action"]  ${title}
    Wait until page contains element  css=#form-buttons-add
    Click button  css=#form-buttons-add
    Wait until page contains element  css=#portletmanager-plone-leftcolumn .managedPortlet
