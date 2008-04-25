## Python Script "getImportReports"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
reports=[]
report=[]
try:
    import_report = context.import_report
except AttributeError:
    # context must be an ATBiblioList
    import_report = context.getAssociatedBibFolder().import_report
report_lines = import_report.split('\n')
for line in report_lines:
    if line != '':
        if line != '='*30:
           report.append(line)
        else:
           reports.append(tuple(report))
           report = []
return tuple(reports)
