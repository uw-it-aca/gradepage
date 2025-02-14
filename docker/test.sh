trap 'exit 1' ERR

#
# PRECONDITION: inherited env vars MUST include:
#      DJANGO_APP: django application directory name

# start virtualenv
source bin/activate

function run_test {
    echo "##########################"
    echo "TEST: $1"
    eval $1
}

run_test "pycodestyle ${DJANGO_APP}/ --exclude=migrations,static"

run_test "python -Wd -m coverage run --source=${DJANGO_APP} manage.py test ${DJANGO_APP}"

# put generated coverage result where it will get processed
cp .coverage.* /coverage

exit 0
