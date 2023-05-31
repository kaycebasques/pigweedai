function bootstrap_docs_repo() {
    git clone --depth 1 https://pigweed.googlesource.com/pigweed/pigweed
    cd pigweed
    source bootstrap.sh
    deactivate
    cd ..
}

# This function just updates a couple lines in the configuration files
# of //pigweed. If you run this function and then `cd pigweed && git diff`
# you can see the changes. There are probably more readable ways to do this
# but this approach is good enough for now.
function hack_palmweed_into_docs_repo() {
    BEFORE="\'pw_docgen\.sphinx\.module_metadata\',"
    AFTER="$BEFORE\n    \'pw_docgen\.sphinx\.palmweed\',"
    sed -i "s/$BEFORE/$AFTER/" pigweed/docs/conf.py
    cp src/sphinx/palmweed.py pigweed/pw_docgen/py/pw_docgen/sphinx/palmweed.py
 
    BEFORE="\"pw_docgen\/sphinx\/module\_metadata\.py\","
    AFTER="$BEFORE\n    \"pw_docgen\/sphinx\/palmweed\.py\","
    sed -i "s/$BEFORE/$AFTER/" pigweed/pw_docgen/py/BUILD.gn
 
    BEFORE="html_static_path = \[\'docs\/_static\'\]"
    AFTER="$BEFORE\nhtml_js_files = \[\'palmweed\.js\'\]"
    sed -i "s/$BEFORE/$AFTER/" pigweed/pw_docgen/py/BUILD.gn

    BEFORE="\"\_static\/css\/pigweed\.css\","
    AFTER="$BEFORE\n    \"\_static\/palmweed\.js\","
    sed -i "s/$BEFORE/$AFTER/" pigweed/docs/BUILD.gn
    cp src/sphinx/palmweed.js pigweed/docs/_static/palmweed.js
}

function build_docs() {
    cd pigweed
    source activate.sh
    [ -d out ] && rm -rf out
    gn gen out
    ninja -C out docs
    deactivate
    cd ..
    mv pigweed/out/docs/gen/docs/html/embeddings src/embeddings/data
}

bootstrap_docs_repo
hack_palmweed_into_docs_repo
# build_docs
