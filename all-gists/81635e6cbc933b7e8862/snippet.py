import os
import sys
import time
import atomac
import subprocess

if len(sys.argv) < 2:
    print "Usage: bouncer.py <path_to_logic_project> (<path_to_logic_project>)"
    os.exit(1)

bundleId = 'com.apple.logic10'
for project in sys.argv[1:]:
    projectName = project.split('/')[-1].replace('.logicx', '')
    filename = projectName + ".wav"

    print "Opening %s..." % project

    #  Open a project file
    subprocess.call(['open', project])

    print "Activating Logic Pro X..."

    logic = atomac.getAppRefByBundleId(bundleId)
    logic.activate()

    print "Waiting for project '%s' to open..." % projectName

    while len(filter(lambda x: projectName in x.AXTitle, logic.windows())) == 0:
        time.sleep(0.1)

    # Wait for the window to load
    time.sleep(1)

    print "Triggering bounce operation..."

    logic.activate()
    logic.sendGlobalKeyWithModifiers('b', [atomac.AXKeyCodeConstants.COMMAND])

    print "Waiting for bounce window..."

    bounce_window = None
    while not bounce_window:
        bounce_window = filter(lambda x: ('Output 1-2' in x.AXTitle) or
                                         ('Bounce' in x.AXTitle),
                               logic.windows())
        time.sleep(0.1)
    bounce_window = bounce_window[0]

    print "Selecting output formats..."

    qualityScrollArea = bounce_window.findFirst(AXRole='AXScrollArea')
    qualityTable = qualityScrollArea.findFirst(AXRole='AXTable')
    for row in qualityTable.findAll(AXRole='AXRow'):
        rowName = row.findFirst(AXRole='AXTextField').AXValue
        checkbox = row.findFirst(AXRole='AXCheckBox')
        if rowName == 'PCM':
            if checkbox.AXValue is 0:
                print "Selected %s output format." % rowName
                checkbox.Press()
            else:
                print "%s output format selected." % rowName
        elif checkbox.AXValue is 1:
            print "Deselected %s output format." % rowName
            checkbox.Press()

    print "Pressing Bounce button..."

    bounce_button = bounce_window.findFirst(AXRole="AXButton",
                                            AXTitle="Bounce")
    if not bounce_button:
        bounce_button = bounce_window.findFirst(
            AXRole="AXButton",
            AXTitle="OK"
        )
    bounce_button.Press()
    bounce_window = None
    # bounce_window is now gone and we have a modal dialog about saving

    print "Waiting for save window..."

    save_window = None
    while not save_window:
        save_window = filter(lambda x: ('Output 1-2' in x.AXTitle) or
                                       ('Bounce' in x.AXTitle),
                             logic.windows())
        time.sleep(0.1)
    save_window = save_window[0]

    print "Entering filename..."

    filenameBox = save_window.findFirst(AXRole="AXTextField")
    filenameBox.AXValue = filename

    print "Pressing 'Bounce' on the save window..."

    bounce_button = save_window.findFirst(AXRole="AXButton", AXTitle="Bounce")
    bounce_button.Press()

    # Check to see if we got a "this file already exists" dialog
    if len(save_window.sheets()) > 0:
        print "Allowing overwriting of existing file..."
        overwrite_sheet = save_window.sheets()[0]
        overwrite_sheet.findFirst(AXRole="AXButton",
                                  AXTitle=u"Replace").Press()

    print "Bouncing '%s'..." % projectName

    # All UI calls will block now, because Logic blocks the UI thread while bouncing
    while len(logic.windows()) > 1:
        time.sleep(0.1)

    print "Waiting for Logic to regain its senses..."

    time.sleep(2)

    # Done - should be saved now.
    # Close the window with command-option-W
    logic.activate()

    time.sleep(1)

    print "Closing project '%s'..." % projectName

    logic.sendGlobalKeyWithModifiers('w', [
        atomac.AXKeyCodeConstants.COMMAND, atomac.AXKeyCodeConstants.OPTION
    ])

    print "Waiting for the 'do you want to save changes' window..."

    save_window = None
    attempts = 0
    while not save_window and attempts < 20:
        save_window = filter(lambda x: '' == x.AXTitle, logic.windows())
        time.sleep(0.1)
        attempts += 1

    if save_window:
        print "Saying 'No, I don't want to save changes'..."
        save_window = save_window[0]

        logic.activate()
        # Click the "Don't Save" button
        filter(lambda x: 'Don' in x.AXTitle, save_window.findAll(AXRole="AXButton"))[0].Press()

    print "Waiting for all Logic windows to close..."

    while len(logic.windows()) > 0:
        time.sleep(0.5)

print "Terminating Logic."
atomac.terminateAppByBundleId(bundleId)
