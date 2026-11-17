*** Settings ***
Documentation  Plone 4.3 keywords (from collective.eeafaceted.collectionwidget, + Add the portlet). Same keyword names and arguments as ui_plone6.robot.
...            Robot Framework 3.0 syntax (Python 2 environment).
...            The status message contains: skips the hidden #kssPortalMessage placeholder (Plone 4.3).
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ***
${MODAL}  css=div.overlay-ajax
${ERROR_PAGE_TEXT}  there seems to be an error
${NOT_FOUND_TEXT}  This page does not seem to exist
${HEADING}  css=#content h1.documentFirstHeading


*** Keywords ***
Log in with the login form
    [Documentation]  Real login (creates the user folder), unlike autologin
    [Arguments]  ${username}  ${password}
    Disable autologin
    Go to  ${PLONE_URL}/login_form
    Input text  css=#__ac_name  ${username}
    Input password  css=#__ac_password  ${password}
    Click button  css=input[name="submit"]
    Wait until page contains element  css=#portal-personaltools

Click the content action
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}
    Click element  css=#plone-contentmenu-actions dt.actionMenuHeader a
    Wait until element is visible  css=#plone-contentmenu-actions-${action_id}
    Click element  css=#plone-contentmenu-actions-${action_id}

The content action is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Click element  css=#plone-contentmenu-actions dt.actionMenuHeader a
    Wait until element is visible  css=#plone-contentmenu-actions dd.actionMenuContent
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-actions-${action_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-actions-${action_id}

Open the add menu
    Click element  css=#plone-contentmenu-factories dt.actionMenuHeader a
    Wait until element is visible  css=#plone-contentmenu-factories dd.actionMenuContent

The personal action links to
    [Documentation]  Item of the user menu (user actions), by action id
    [Arguments]  ${action_id}  ${url}
    Element attribute value should be  css=#personaltools-${action_id} a  href  ${url}

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
    Click button  ${MODAL} #form-buttons-save

Cancel the modal
    Click button  ${MODAL} #form-buttons-cancel

The modal is closed
    Wait until element is not visible  ${MODAL}

The status message contains
    [Documentation]  Skips the hidden, empty #kssPortalMessage placeholder
    [Arguments]  ${text}
    Wait until element contains  css=.portalMessage:not(#kssPortalMessage)  ${text}

The page is not an error
    Page should not contain  ${ERROR_PAGE_TEXT}

The page is not found
    Page should contain  ${NOT_FOUND_TEXT}

The edit link is not available
    Page should not contain element  css=#contentview-edit

Click the add menu item
    [Documentation]  Item of the Add new... menu (factories), by its id: the normalized portal type
    [Arguments]  ${item_id}
    Click element  css=#plone-contentmenu-factories a#${item_id}

Input the title
    [Documentation]  Title field of a Dexterity add or edit form (IDublinCore behavior)
    [Arguments]  ${title}
    Wait until element is visible  css=#form-widgets-IDublinCore-title
    Input text  css=#form-widgets-IDublinCore-title  ${title}

Save the add form
    Click button  css=#form-buttons-save

Add the query criterion
    [Documentation]  Collection query widget (plone.formwidget.querystring): "Add criterion" select, by title
    ...              (from collective.compoundcriterion)
    [Arguments]  ${criterion}
    # the widget is ready when its javascript has loaded the configuration and hidden the "Add" button
    Wait until element is not visible  css=input.addIndexButton
    Select from list by label  css=select.addIndex  ${criterion}

Select the query value
    [Documentation]  Value of the last added MultipleSelectionWidget criterion (checkbox pulldown), by title
    ...              (from collective.compoundcriterion)
    [Arguments]  ${value}
    ${widget}=  Set variable  xpath=(//dl[contains(@class, "multipleSelectionWidget")])[last()]
    ${checkbox}=  Set variable  ${widget}//label[normalize-space(span)="${value}"]/input
    Wait until page contains element  ${checkbox}
    ${visible}=  Run keyword and return status  Element should be visible  ${checkbox}
    Run keyword unless  ${visible}  Click element  ${widget}/dt
    Select checkbox  ${checkbox}

Add the portlet
    [Documentation]  Portlet added to the left column of the content at ${path} (@@manage-portlets), by its title.
    ...              Its add form (formlib) is saved as it is.
    [Arguments]  ${path}  ${title}
    Go to  ${PLONE_URL}/${path}/@@manage-portlets
    Select from list by label  css=#portletmanager-plone-leftcolumn select[name=":action"]  ${title}
    Wait until page contains element  css=input[name="form.actions.save"]
    Click button  css=input[name="form.actions.save"]
    Wait until page contains element  css=#portletmanager-plone-leftcolumn .managedPortlet
