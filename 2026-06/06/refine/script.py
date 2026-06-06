from bs4 import BeautifulSoup

def replace_hrefs(input_file, output_file):
    # Read the HTML file as bytes
    with open(input_file, 'rb') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Replace all href attributes with '#'
    for a in soup.find_all('a'):
        a['href'] = '#'

    # Write the modified HTML to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == "__main__":
    replace_hrefs('input.html', 'output.html')
    print("All href attributes have been replaced with '#' and saved to output.html")