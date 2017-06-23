# Priority skills

priority skills are skills that need to be loaded first, these are read from config file and loaded by that order

this partially solves skills being dependencies of each other problem, but the aim of this change is for skills that need to listen for messages

objectives skill needs this to catch register objectives messages
control center skill needs this to enforce run level
help skill needs this to catch all register stuff messages