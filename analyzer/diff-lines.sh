# Get only all modified lines of code from a git diff with
# their line numbers.
#
# Outputs: 
# {file_path}:CASDELIMITER:{line number}:CASDELIMITER:{Code modified}
#
# example:
#   mysqltuner.pl:CASDELIMITER:828:CASDELIMITER:-     print "General recommendations:n";
#
# We only really care about the file path and line of code, but we keep the modified itself
# only for it helps debugging.
#
# Much inspiration for this solution come from John at StackOverflow, thank you!
# http://stackoverflow.com/questions/8i-get-added-and-modified-lines-numbers

path=
line=
while read; do
    esc=$'\033'
    if [[ $REPLY =~ ---\ (a/)?.* ]]; then
        continue
    elif [[ $REPLY =~ \+\+\+\ (b/)?([^[:blank:]$esc]+).* ]]; then
        path=${BASH_REMATCH[2]}
    elif [[ $REPLY =~ @@\ -[0-9]+(,[0-9]+)?\ \+([0-9]+)(,[0-9]+)?\ @@.* ]]; then
        line=${BASH_REMATCH[2]}
    elif [[ $REPLY =~ ^($esc\[[0-9;]+m)*([\ +-]) ]]; then
        echo "$path:$line:$REPLY"
        if [[ ${BASH_REMATCH[2]} != - ]]; then
            ((line++))
        fi
    fi
done
