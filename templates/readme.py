def read_html_static_page(filename):
    with open(filename, 'r') as f:
        content =f.read()
        data = {
                "content": content
                }
        return (data)

print (read_html_static_page("humidity.html"))
