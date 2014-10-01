import fileinput
for line in fileinput.input('src/app.yaml', inplace=1):
    if line.startswith('application:'):
        print 'application: spudmart1'
    else:
        print line,