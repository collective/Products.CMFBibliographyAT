## Python Script "getLastImportReport"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

report=[]
try:
    import_report = context.import_report
except AttributeError:
    # context must be an ATBiblioList
    import_report = context.getAssociatedBibFolder().import_report
old_report = import_report.split('\n')
for line in old_report:
    if line != '':
        if line != '='*30:
           report.append(line)
        else:
           return tuple(report)
return tuple(report)
