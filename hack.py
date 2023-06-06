def hack(file_path, before, after):
    with open(file_path, 'r') as f:
        text = f.read()
    text = text.replace(before, after)
    with open(file_path, 'w') as f:
        f.write(text)

before = "'pw_docgen.sphinx.module_metadata',"
after = f"{before} 'pw_docgen.sphinx.embeddings',"
hack('pigweed/docs/conf.py', before, after)

before = "html_static_path = ['docs/_static']"
after = f"{before}\nhtml_js_files = ['pigweedai.js']"
hack('pigweed/docs/conf.py', before, after)

before = '"_static/css/pigweed.css",'
after = f'{before} "_static/pigweedai.js",'
hack('pigweed/docs/BUILD.gn', before, after)

before = '"pw_docgen/sphinx/module_metadata.py",'
after = f'{before} "pw_docgen/sphinx/embeddings.py",'
hack('pigweed/pw_docgen/py/BUILD.gn', before, after)

before = '"code_of_conduct.rst",'
after = f'"ask_pigweed_ai.rst", {before}'
hack('pigweed/docs/BUILD.gn', before, after)

before = 'Home <self>'
after = f'docs/ask_pigweed_ai\n  Home <self>'
hack('pigweed/docs/index.rst', before, after)
