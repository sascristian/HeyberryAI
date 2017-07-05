# Priority skills

priority skills are skills that need to be loaded first, these are read from config file and loaded by that order

this partially solves skills being dependencies of each other problem, but the aim of this change is for skills that need to listen for messages

        - objectives skill needs this to catch register objectives messages
        - control center skill needs this to enforce run level
        - help skill needs this to catch all register stuff messages
        - browser service needs to be loaded first or skills that use it in initialize may not work properly (skills that need login)

# troubles

control center enforces run-level at start up, so it should be 1st priority skill

second priority skill will start loading before run level is finished, this means if 2nd priority skill isnt part of run level it will start but then shutdown