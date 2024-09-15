import molmass
from molmass import Formula
import os
import re
import fitz
import time
from fpdf import FPDF

# Source folder
folder_path = r"C:\Users\match\Downloads"  # Specify path of folder to be scanned
# Destination folder #filename for report
output_file = r"C:\Users\match\Desktop\Report.pdf"  # Specify name and path of output file

start_time = time.time() # Start counter to later determine the program's running time

# Define some colors for the console output
CCYAN = '\033[96m'
CGREEN = '\33[32m'
CVIOLET = '\33[35m'
CEND = '\033[0m'
def calculate_molecular_weight(formula):

    atomic_weights = {
        "H": 1.008, "D": 2.0141, "He": 4.002602, "Li": 6.94, "Be": 9.0121831, "B": 10.81, "C": 12.011,
        "N": 14.007, "O": 15.999, "F": 18.9984, "Ne": 20.1797, "Na": 22.98977,
        "Mg": 24.305, "Al": 26.98154, "Si": 28.085, "P": 30.97376, "S": 32.06,
        "Cl": 35.45, "Ar": 39.948, "K": 39.0983, "Ca": 40.078, "Sc": 44.955908, "Ti": 47.867,
        "V": 50.9415, "Cr": 51.9961, "Mn": 54.938044, "Fe": 55.845, "Co": 58.933194,
        "Ni": 58.6934, "Cu": 63.546, "Zn": 65.38, "Ga": 69.723, "Ge": 72.630, "As": 74.921595,
        "Se": 78.971, "Br": 79.904, "Kr": 83.798, "Rb": 85.4678, "Sr": 87.62, "Y": 88.90584,
        "Zr": 91.224, "Nb": 92.90637, "Mo": 95.95, "Tc": 98, "Ru": 101.07, "Rh": 102.90550,
        "Pd": 106.42, "Ag": 107.8682, "Cd": 112.414, "In": 114.818, "Sn": 118.710, "Sb": 121.760,
        "Te": 127.60, "I": 126.90447, "Xe": 131.293, "Cs": 132.90545196, "Ba": 137.327,
        "Au": 196.96657 # Added Gold
        # ... (add the rest of the elements)
    }

    # Extract elements and their counts using regular expressions
    elements = re.findall(r"([A-Z][a-z]?)(\d*)", formula)

    mol_weight = 0.0
    for element, count in elements:
        element_weight = atomic_weights.get(element, 0.0)
        mol_weight += element_weight * (int(count) if count else 1)
    return mol_weight

class PDF(FPDF):
    def header(self):
        # Set font for the header
        self.set_font('Arial', 'B', 12)
        # Title
        pdf.set_text_color(0, 0, 0)  # Black
        self.cell(0, 10, 'HRMS Report', 0, 1, 'C')

def normalize_word(word, string):
    pattern = re.compile(r'(?i)' + re.escape(word))
    return pattern.sub(word.lower(), string)


def is_molecular_formula(s):
    # Remove parentheses and square brackets from the string
    s = re.sub(r'[\(\)\[\]]', '', s)
    # Define a regular expression pattern for a valid molecular formula
    # The pattern ensures that if a digit follows an element, it must not start with '0'
    pattern = re.compile(
        r'^((Ac|Ag|Al|Am|Ar|As|At|Au|B|Ba|Be|Bh|Bi|Bk|Br|C|Ca|Cd|Ce|Cf|Cl|Cm|Co|Cr|Cs|Cu|Ds|D|Db|Dy|Er|Es|Eu|F|Fe|Fm|Fr|Ga|Gd|Ge|H|He|Hf|Hg|Ho|Hs|I|In|Ir|K|Kr|La|Li|Lr|Lu|Md|Mg|Mn|Mo|Mt|N|Na|Nb|Nd|Ne|Ni|No|Np|O|Os|P|Pa|Pb|Pd|Pm|Po|Pr|Pt|Pu|Ra|Rb|Re|Rf|Rg|Rh|Rn|Ru|S|Sb|Sc|Se|Sg|Si|Sm|Sn|Sr|Ta|Tb|Tc|Te|Th|Ti|Tl|Tm|U|V|W|Xe|Y|Yb|Zn|Zr)([1-9]\d*)?)*$'
    )

    # Search the string for a match against the pattern
    return bool(pattern.fullmatch(s))

def is_convertible_to_float(value):
    return value is not None and isinstance(value, (float, int)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit())

def convert_pattern_hrms(input_string):
    return re.sub(r"HRMS.{1,10} for (\S+) .{1,10} calcd ", lambda m: f"calculated for {m.group(1)}", input_string)

def extract_float_number(input_string):
    match = re.search(r'\b\d+\.\d{4}\b', input_string)
    return match.group() if match else None

def extract_number(input_string):
    match = re.search(r'\b(\d+(\.\d+)?)\b', input_string)
    if match:
        return match.group(1)
    else:
        return None

def delete_between_strings(text, start_string, end_string, max_length=42):
    pattern = re.compile(f'{re.escape(start_string)}(.*?){re.escape(end_string)}', re.DOTALL)
    matches = pattern.finditer(text)
    for match in matches:
        passage = match.group(1)
        if len(passage) <= max_length:
            text = text.replace(match.group(0), "")

    return text

def have_swapped_adjacent_digits(float1, float2):
    # Convert floats to strings, ensuring consistent decimal representation
    str1, str2 = str(float1), str(float2)
    # Ensure both strings are of the same length
    if len(str1) != len(str2):
        return False
    # Remove the last two characters for comparison
    str1 = str1[:-2]
    str2 = str2[:-2]
    if len(str1) != len(str2) or len(str1) < 2:
        return False
    swapped_digits = False
    i = 0
    while i < len(str1) - 1:
        if str1[i] == str2[i] and str1[i + 1] == str2[i + 1]:
            i += 1  # Skip identical digits
        elif str1[i] == str2[i + 1] and str1[i + 1] == str2[i]:
            if swapped_digits:  # If we already found a swapped pair, return False
                return False
            swapped_digits = True  # Mark that we found a swapped pair
            i += 2  # Skip the next digit since we know it's part of the swap
        elif str1[i] != str2[i]:
            return False  # If digits don't match and it's not a swap, return False
        else:
            i += 1
    return swapped_digits  # Return True if exactly one swapped pair is found

def differ_in_single_digit_except_last_two(float1, float2):
    str1, str2 = str(float1), str(float2)
    # Handle potential decimal points and trailing zeros
    str1 = str1.rstrip('0').rstrip('.')
    str2 = str2.rstrip('0').rstrip('.')
    if len(str1) != len(str2):
        return False
    differing_digits = 0
    for i in range(len(str1) - 2):  # Check up to the second-to-last digit
        if str1[i] != str2[i]:
            differing_digits += 1
            if differing_digits > 1:
                return False
    # Check if the last two digits match
    return differing_digits == 1 and str1[-2:] == str2[-2:]

def add_sentence(pdf, sentence):
    # Set font and text color
    pdf.set_font("Arial", size=10)
    # Set position to the top left and align text to the left
    pdf.set_xy(10, pdf.get_y())
    # Write the sentence with colors
    pdf.cell(0, 5, txt=sentence, ln=True, align='L')

def list_filepaths_in_folder(folder_path):
    try:
        # Check if the provided path is a directory
        if os.path.isdir(folder_path):
            # Use os.listdir to get a list of filenames in the directory
            filenames = os.listdir(folder_path)
            # Create a list of full file paths by joining the folder path and each filename
            filepaths = [os.path.join(folder_path, filename) for filename in filenames]
            return filepaths
        else:
            return "The provided path is not a valid directory."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def extract_text_from_pdf(file_path):
    # Initialize the PyMuPDF document object
    if os.path.basename(file_path).lower() == 'desktop.ini':
        return ""
    pdf_document = fitz.open(file_path)
    # Initialize an empty string to store the text content
    text_content = ""
    # Iterate through each page of the PDF
    for page_num in range(pdf_document.page_count):
        # Get the current page
        page = pdf_document.load_page(page_num)
        # Extract text from the page and add it to the content string
        text_content += page.get_text()
    return text_content


def exchange_if_float_list(list1, list2):
    if all(is_float(value) for value in list1):
        return list2, list1
    else:
        return list1, list2

def is_float(value):
    if value is None:
        return False
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def remove_lines_with_pattern(text):
    return '\n'.join([line for line in text.split('\n') if not (line.startswith('S') and line[1:].isdigit())])

def extract_text_after_string(text, search_string, num_characters):
    result = []
    index = 0
    while index < len(text):
        start_index = text.find(search_string, index)
        if start_index == -1:
            break
        start_index += len(search_string)
        end_index = start_index + num_characters
        if end_index > len(text):
            break
        result.append(text[start_index:end_index])
        index = end_index
    return result

def extract_text_before_string(text, search_string, num_characters):
    result = []
    index = 0
    while index < len(text):
        start_index = text.find(search_string, index)
        if start_index == -1:
            break
        end_index = start_index - num_characters
        if end_index < 0:
            end_index = 0
        result.append(text[end_index:start_index])
        index = start_index + len(search_string)
    return result

def remove_chars(string, chars_to_remove):
    for char in chars_to_remove:
        string = string.replace(char, "")
    return string

def concatenate_formulas(match):
    formula1, formula2 = match.group().split()
    return formula1 + formula2

def replace_comma_with_decimal(text):
    # Define a regular expression pattern to match floating-point numbers with commas
    pattern = r'\b(\d+,\d+)\b'
    # Use re.sub() to find and replace commas with decimal points
    def replace(match):
        return match.group(0).replace(',', '.')
    # Replace all occurrences of floating-point numbers with commas,
    result = re.sub(pattern, replace, text)
    return result


def adjust_space_around_decimal(text):
    text = re.sub(r'(\d{3,4})\. (\d{4})', r'\1.\2', text)  # Remove space after decimal
    return re.sub(r'(\d+\.\d+)([A-Za-z])', r'\1 \2', text)  # Add space after decimal

def increase_element_count(molecular_formula, element_to_increase):
    # Define a regular expression pattern to match the specified element
    pattern = r'({})(?![a-z])\d*'.format(element_to_increase)
    def replace_element(match):
        element_count = match.group()
        element = re.match(r'([A-Z][a-z]*)', element_count).group()
        count = re.search(r'\d+', element_count)
        if count:
            new_count = int(count.group()) + 1
        else:
            new_count = 2
        return element + str(new_count)
        modified_formula = re.sub(pattern, replace_element, molecular_formula)
        return modified_formula

    # Use the re.sub() function to replace the specified element according to the pattern
    new_formula = re.sub(pattern, replace_element, molecular_formula)
    return new_formula

def decrease_element_count(molecular_formula, element_to_decrease):
    # Define a regular expression pattern to match the specified element
    pattern = r'({})(?![a-z])\d*'.format(element_to_decrease)

    def replace_element(match):
        element_count = match.group()
        element = re.match(r'([A-Z][a-z]*)', element_count).group()
        count = re.search(r'\d+', element_count)

        if count:
            current_count = int(count.group())
            if current_count > 2:
                new_count = current_count - 1
                return element + str(new_count)
            else:
                return element  # Remove the count when it's 2
        else:
            return element

    modified_formula = re.sub(pattern, replace_element, molecular_formula)
    return modified_formula
def is_element_in_formula(molecular_formula, element_to_check):
    # Extract elements and their counts from the formula using regex
    pattern = r'([A-Z][a-z]*)(\d*)'
    elements_and_counts = re.findall(pattern, molecular_formula)

    # Check if the element is present in the extracted elements
    for element, count in elements_and_counts:
        if element == element_to_check:
            return True
    return False

def remove_short_lines(text):
    # Split the text into lines
    lines = text.split('\n')
    # Filter out lines shorter than 6 characters
    filtered_lines = [line for line in lines if len(line) >= 6]
    # Join the filtered lines back into a string
    modified_text = '\n'.join(filtered_lines)
    return modified_text

def check_molecular_formula(molecular_formula):
    # Define a regular expression pattern to match an element and its count
    pattern = r'([A-Z][a-z]*)(\d*)'
    def replace_element(match):
        element = match.group(1)
        count = match.group(2)
        if count == '1':
            return element  # Remove the '1'
        else:
            return match.group(0)  # Keep the original element and count
    corrected_formula = re.sub(pattern, replace_element, molecular_formula)
    return corrected_formula
def delete_element_from_formula(molecular_formula, element_to_delete):
    # Define a regular expression pattern to match an element and its count
    pattern = r'([A-Z][a-z]*)(\d*)'

    # Function to replace an element and its count
    def replace_element(match):
        element = match.group(1)
        count = match.group(2)
        if element == element_to_delete:
            return ''  # Remove the specified element and its count
        else:
            if count == '1':
                return element  # Remove the '1'
            else:
                return match.group(0)  # Keep the original element and count
    corrected_formula = re.sub(pattern, replace_element, molecular_formula)
    return corrected_formula

def add_space_after_pattern(input_string):
    # Define the pattern to match "XXX.XXXXYYY" where X is a digit and Y can be anything
    pattern = r'(\d{3}\.\d{4})(\w{3})'
    # Use re.sub() to add a space after the pattern
    result = re.sub(pattern, r'\1 \2', input_string)
    return result

def check_formula(text,entity):
    global flag
    global pdf
    new_formula_anion = new_formula.replace("+", "-")
    new_formula_neutral = new_formula.replace("+", "")
    formatted_modified_mass = f"{Formula(new_formula).monoisotopic_mass:.4f}"
    formatted_modified_mass_anion = f"{Formula(new_formula_anion).monoisotopic_mass:.4f}"
    formatted_modified_mass_neutral = f"{Formula(new_formula_neutral).monoisotopic_mass:.4f}"
    if formatted_calculated_mass == formatted_modified_mass and new_formula_anion != mol_formula_anion:
        a=f'{text} {i + 1} {element_to_test}{entity}, the following molecular formula fits the mass reported in the SI: {new_formula} ({formatted_modified_mass})'
        pdf.set_text_color(24, 116, 205)
        add_sentence(pdf,a)
        pdf.set_text_color(0, 0, 0)
        print(
            CVIOLET + f'{text} {i + 1} {element_to_test}{entity}, the following molecular formula fits the mass reported in the SI: {new_formula} ({formatted_modified_mass})' + CEND)
        flag=1
    elif formatted_calculated_mass == formatted_modified_mass_anion and new_formula_anion != mol_formula_anion:
        a=f'{text} {i + 1} {element_to_test}{entity}, the following molecular formula fits the mass reported in the SI: {new_formula_anion} ({formatted_modified_mass_anion})'
        pdf.set_text_color(24, 116, 205)
        add_sentence(pdf, a)
        pdf.set_text_color(0, 0, 0)
        print(
            CVIOLET + f'{text} {i + 1} {element_to_test}{entity}, the following molecular formula fits the mass reported in the SI: {new_formula_anion} ({formatted_modified_mass_anion})' + CEND)
        flag=1
    elif formatted_calculated_mass == formatted_modified_mass_neutral and new_formula_neutral != mol_formula_neutral:
        a=f'{text} {i + 1} {element_to_test}{entity}, the following molecular formula fits the mass reported in the SI: {new_formula_neutral} ({formatted_modified_mass_neutral})'
        b=f'However, the reported mass was probably measured for the cation: {new_formula} ({formatted_modified_mass})'
        pdf.set_text_color(24, 116, 205)
        add_sentence(pdf, a)
        add_sentence(pdf, b)
        pdf.set_text_color(0, 0, 0)
        print(
            CVIOLET + f'{text} {i + 1} {element_to_test}{entity}, the following molecular formula fits the mass reported in the SI: {new_formula_neutral} ({formatted_modified_mass_neutral})' + CEND)
        print(
            CVIOLET + f'However, the reported mass was probably measured for the cation: {new_formula} ({formatted_modified_mass})' + CEND)
        flag=1

#Initialize PDF Output
pdf = PDF()
pdf.add_page()

# Get the names of the PDF files in the source folder
filepaths = list_filepaths_in_folder(folder_path)

# Extract the text from source PDF and store it in the variable file_contents
for pdf_file_path in filepaths:
    error=0
    correct=0
    try:

        file_contents = extract_text_from_pdf(pdf_file_path) # load the text content into a string

        #print(file_contents)

        replacements = [("HRMS", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa HRMS "), (" calc ", " calcd "),
                        (" cald.", " calcd "), ("calcd.", "calcd"), ("calcd:", "calcd"), ("Calcd.", "calcd"),
                        ("calcd for", "calcd"), ("Calcd for", "calcd"), ("m/z:", "m/z"), ("):", ")"),
                        ("for [M+H]", ""), ("for [M-H]", ""), ("[M+H]+", ""), ("(М+H)+", ""), ("(М+H)", ""),
                        (" ESI ", " calcd"), ("ESI+)", " calcd"), ("ESI-)", " calcd"), ("ESI)", " calcd"),
                        ("TOF) m/z", "calcd"), ("(m/z)", "")]

        for old, new in replacements:
            file_contents = file_contents.replace(old, new)

        file_contents = ' '.join(file_contents.split()).strip()

        file_contents = file_contents + "lore ipsum lore ipsum lore ipsum lore ipsum"

        file_contents=convert_pattern_hrms(file_contents)
        replacements = {
            "=": " ",
            "C  ": "C", "  H  ": "H", "H  ": "H", "  N  ": "N", "N  ": "N",
            "  O  ": "O", "O  ": "O", "  S  ": "S", "S  ": "S", "  P  ": "P", "P  ": "P",
            "  Na  ": "Na", "Na  ": "Na",
            " C ": " C", " H ": "H", " N ": "N", " O ": "O", " S ": "S",
            " Br ": "Br", " F ": "F", " P ": "P", " I ": "I", " Cl ": "Cl",
            " Na ": "Na", " SNa ": "SNa", " NO ": "NO"
        }

        for old, new in replacements.items():
            file_contents = file_contents.replace(old, new)

        file_contents = remove_short_lines(file_contents)

        # The following commands are aimed at cleaning up the data

        file_contents = adjust_space_around_decimal(file_contents)  # 278. 2334 -> 278.2334
        file_contents = replace_comma_with_decimal(file_contents) # 278,2334 -> 278.2334

        # Normalize the writing of the following words to all lowercase, e.g. CalC -> calc

        list_of_strings_to_be_all_lowercase=['calc','anal','elem','mass','obs','for','page','found','exact','mono','meas']
        for string in list_of_strings_to_be_all_lowercase:
            file_contents = normalize_word(string, file_contents)

        # Define a regular expression pattern to match the specified sequences in single lines
        pattern = re.compile(r"\bS\d+\b\s*\n")  # Matches standalone S{number} followed by a line break

        # Use the sub() function to replace matched patterns with an empty string
        file_contents = re.sub(pattern, "", file_contents)

        # remove page numbers
        file_contents = file_contents.replace("&", " ")

        for number in range(179, 0, -1):
            file_contents = file_contents.replace(f" S{number}", " ")
        for number in range(179, 0, -1):
            file_contents = file_contents.replace(f" s{number}", " ")
        for number in range(179,0, -1):
            file_contents = file_contents.replace(f" {number} ", " ")
        file_contents = remove_lines_with_pattern(file_contents)

        replacements = {
            "The":" ", "FAB":" ","page": " ", "of": " ", " is ": " ", "Figure": " ", " N ": " ", " O ": " ", " NO ": " ",
            "calculated": "calcd", "calc'd": "calcd","cal'd":"calcd","calc.'d": "calcd","calc'ed": "calcd", "calc’d": "calcd","calc.’d": "calcd","calc’ed": "calcd", "calc`d": "calcd",
            "calc`ed": "calcd","calc´d": "calcd", "calc′d.":"calcd","calc´ed": "calcd","cal´d": "calcd","calced":"calcd","calc:":"calcd","calc for":"calcd","for": "", "C ": "C:", "C,": "C:", "C.": "C:", "C'": "C:",
            "%C": "C:", "C%": "C:", "C[%": "C:", "C(%": "C:", "found,":"found","berechnet für":"calcd", "berechnet":"calcd", "gefunden":"found"
        }

        for original, replacement in replacements.items():
            file_contents = file_contents.replace(original, replacement)

        file_contents = ' '.join(file_contents.split()).strip()

        start_delimiter = "calc"
        end_delimiter = "C:"
        file_contents = delete_between_strings(file_contents, start_delimiter, end_delimiter)
        file_contents = ' '.join(file_contents.split()).strip()
        replacements = {
            "was": "", "for": "", "mass": "", "and found": " ", "found": " ", "and": " ", "exact": " ",
            "rel": " ", ",": " ", ":.": " ", "[  ": "[", "[ ": "[", "(  ": "(", "( ": "(", ";": " ",
            "(": " ", ")": " ", "monoisotopic": " "
        }

        for original, replacement in replacements.items():
            file_contents = file_contents.replace(original, replacement)

        file_contents = re.sub(r'\[M[^\]]*\]|\[M[^\,]]*?\n[^\]]*\]', '', file_contents)
        file_contents = re.sub(r'\(M[^\)]*\)', '', file_contents)
        file_contents = re.sub(r'\{M[^\}]*\}', '', file_contents)

        replacements = {
            "2M+Na": " ", "2M - H": "", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
            "₆": "6", "₇": "7", "₈": "8", "₉": "9", "₀": "0", "¹": "1", "²": "2", "³": "3",
            "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁰": "0", "[": "",
            "]": "", "measured": " ", "mono": " "
        }

        for original, replacement in replacements.items():
            file_contents = file_contents.replace(original, replacement)

        file_contents = re.sub(r'M(?![gno])', '', file_contents)
        file_contents = re.sub(r"page \d+ of \d+", "", file_contents, flags=re.DOTALL)
        file_contents = re.sub(r"Chemical Science", "", file_contents)

        file_contents = ' '.join(file_contents.split()).strip()

        replacements = {
            "+": " ", "ꞏ": " ","-":"", "=": " ", "nalysis calc": "", "nalysis: calc": "", "(%) calc": "",
            "EA: calc": "", "av.": "", "nal.calc": "", "..": ".", "was calcd for": "calcd ",
            "exact mass for": "calcd ", "requires": "calcd ", "ass required for": "calcd ",
            "and found": "", "found as": "", "found.:": "","found:":"", "found,":"","Foumd": "", "OO": " ", "F ound": "",
            "we calcd": "","found":""
        }

        for original, replacement in replacements.items():
            file_contents = file_contents.replace(original, replacement)

        #print(file_contents)

        #chars_to_remove = ['DFT calculated', 'alculated tot', 'alculated en', 'alculated IR', 'alculated di',
        chars_to_remove = ['ber.', 'gef.',"measured",'measd','ass found',"found", "Found",'expected','Expected',"required",
                             'expect',"requires","Requires",'dcalc',  ' OCl', ' Br ', 'O Cl ','fFor', 'alcd for C:', 'nal. Cal',
                           'nal. cal', 'nal Calc', 'nal calc', 'ensity (calc', 'to calc','most','abundant','isotope','peak',
                          'Observed', 'observed', 'Anal. Calcd', '3. Calc', 'bcalc','calcd C:','monoisotopic','was',
                           'ρca,lcd', 'Anal. calc', 'anal. calc', 'Exp.','Error', "(",'fo ','und','not','OO',' S',
                           ")","for", "For", "m/z",'m/','z:','exact mass', "Dcalc"," is", 'meas']

        file_contents=remove_chars(file_contents,chars_to_remove)

        replacements = {
            "page": " ", "of": " ", "TOF": " ", "𝑀": " ", "EI": " ", " . ": " ", ":": " ", "Δ": " ",
            "𝛼": " ", " a ": " ", " M ": " ", " H ": " ", "ESI": " ", " Na ": " ", " K ": " ",
            " NH4 ": " ", "Obs.": " ", "obs": " ", "78.9183": "", " 48Ti": "[48Ti]",
            " 46Ti": "[46Ti]", " 47Ti": "[47Ti]", " 80Se": "[80Se]", " 2H": "D", " [3H]": "[3H]",
            " 10B": "[10B]",  "127I": "[127I]", "120Sn":"[120Sn]", "119Sn":"[119Sn]", "118Sn":"[118Sn]","N23Na": "*N23*Na","F23Na": "*F23*Na","H23Na": "*H23*Na","H28Si": "*H28*Si","H11B": "*H11*B", "H13Co": "*H13*Co",
            "H13Cl": "*H13*Cl", "H18O": "*H18*O", "H218O": "*H218*O", "N18O": "*N18*O",
            "H35Cl": "*H35*Cl", "H37Cl": "*H37*Cl", "H10B":"*H10*B","H19F": "*H19*F", "Br79": "[79Br]",
            " 79Br": "[79Br]", " 81Br": "[81Br]", "18O": "[18O]", "74Ge": "[74Ge]","65Cu":"[65Cu]","63Cu":"[63Cu]",
            "Br81": "[81Br]", " 35Cl": "[35Cl]", " 37Cl": "[37Cl]", " 11B": "[11B]",
            " 32S": "S", " 31P": "P","35Cl":"[35Cl]","80Se":"[80Se]","37Cl":"[37Cl]","28Si":"[28Si]","13C":"[13C]","[13C]l":"13Cl","79Br":"[79Br]","81Br":"[81Br]","11B":"[11B]","10B":"[10B]","[10B]r":"10Br","[[":"[","]]":"]","*H13*Cl": "H13Cl", "*H18*O": "H18O", "*H218*O": "H218O",
            "*N18*O": "N18O", "*H13*Co": "H13Co", "*H37*Cl": "H37Cl", "*H35*Cl": "H35Cl",
            "*H28*Si": "H28Si","*H10*B":"H10B","*H23*Na": "H23Na","*F23*Na": "F23Na","*N23*Na": "N23Na","*H11*B":"H11B", "*H19*F": "H19F", "cacld": "", "calcd.": "calcd ", "calc’d": "calcd ",
            "calc.": "calcd ", "calclulated": "calcd ", "calcluated": "calcd ", "caculated": "calcd ",
            "calcd gcm": " ", " is ": " ", "calcd": "calcd ", "calcd  ": "calcd "
        }

        for original, replacement in replacements.items():
            file_contents = file_contents.replace(original, replacement)

        file_contents = re.sub(r'[^\w\s.\[\]]', '', file_contents)
        file_contents = ' '.join(file_contents.split()).strip()
        file_contents = ' '.join(file_contents.split()).strip()

        replacements = {}
        for i in range(1, 10):
            old_str = f"calcd C{i}"
            new_str = f"HeHeXe{i}"
            replacements[old_str] = new_str
        for old_str, new_str in replacements.items():
            file_contents = file_contents.replace(old_str, new_str)
        file_contents = file_contents.replace("calcd", "")
        for old_str, new_str in replacements.items():
            file_contents = file_contents.replace(new_str, old_str)

        # Use re.sub() to find and concatenate formulas in the text
        formula_pattern = r'[A-Z][a-z]?\d*'
        file_contents = re.sub(f'({formula_pattern} {formula_pattern})', concatenate_formulas, file_contents)

        # e.g. 1232.344.dsds and convert the full stop into a space the text becomes 1232.344 dsds
        file_contents = re.sub(r'(\d+\.\d+)\.', r'\1 ', file_contents)

        # remove everything that is two characters/digits or shorter
        file_contents = re.sub(r' (?<![a-zA-Z0-9]) [a-zA-Z0-9] (?![a-zA-Z0-9]) ', ' ', file_contents)
        file_contents = re.sub(r' (?<![a-zA-Z0-9]) [a-zA-Z0-9]{2} (?![a-zA-Z0-9]) ', ' ', file_contents)
        file_contents = ' '.join(file_contents.split()).strip()
        file_contents = add_space_after_pattern(file_contents)

        search_string = "calcd "
        num_characters = 45
        result = extract_text_after_string(file_contents, search_string, num_characters)
        result = [s.lstrip() for s in result]
        # Assuming 'result' is a list of strings
        # Filter elements to only those that can be split into 3 or more parts

        filtered_elements = [element for element in result if len(element.split()) > 2]

        # Now, you can safely assume each element in 'filtered_elements' has at least three parts
        # and proceed to extract them without worrying about an 'index out of range' error

        mol_formula = [element.split()[0] for element in filtered_elements]
        raw_calc_mass_from_SI = [element.split()[1] for element in filtered_elements]
        raw_found_mass_from_SI = [element.split()[2] for element in filtered_elements]

        # get the float BEFORE calc in case the order is different

        num_characters = 25
        result2 = extract_text_before_string(file_contents, search_string, num_characters)
        result2 = [extract_float_number(xxx) for xxx in result2]

        result2, raw_found_mass_from_SI = exchange_if_float_list(result2, raw_found_mass_from_SI)

        #replace N0 (N zero) by NO
        mol_formula = [element.replace('N0', "NO") for element in mol_formula]
        mol_formula = [element.replace('oH', "0H") for element in mol_formula]
        # change C12h13 into C12H13
        converted_formulas = [re.sub(r'C(\d+)h(\d+)', lambda m: f"C{m.group(1)}H{m.group(2)}", formula) for formula in
                              mol_formula]
        mol_formula = converted_formulas

        for i in range(len(mol_formula)):
            x = len(raw_calc_mass_from_SI[i])
            d = mol_formula[i][-x:]
            try:
                calc_mass = float(raw_calc_mass_from_SI[i])

                if abs(calc_mass - float(d)) <= 0.01 * calc_mass:
                    raw_found_mass_from_SI[i], raw_calc_mass_from_SI[i] = raw_calc_mass_from_SI[i], d
                    # Remove the floating-point portion from the mol_formula
                    mol_formula[i] = mol_formula[i][:-x]
            except ValueError:
                pass

        # remove colons in formulas, e.g. ["H2O.", "C6H12O6.", "NaCl."] -> ["H2O", "C6H12O6", "NaCl"]
        mol_formula = [element.replace('.', "") for element in mol_formula]

        #list incorrect formulas
        incorrect_formulas = [element for element in mol_formula if not is_molecular_formula(element)]

        # filters results where raw_calc_mass... and raw_found_m.. are convertible to float AND mol_formula is valid
        if len(mol_formula)>0 and len(raw_found_mass_from_SI)==len(raw_calc_mass_from_SI)==len(mol_formula):

            # Assuming mol_formula, raw_calc_mass_from_SI, and raw_found_mass_from_SI are defined
            # and is_convertible_to_float and is_molecular_formula functions are defined

            # Perform the filtering
            filtered_tuples = [(xn, yn, zn) for xn, yn, zn in
                               zip(mol_formula, raw_calc_mass_from_SI, raw_found_mass_from_SI) if
                               is_convertible_to_float(yn) and is_convertible_to_float(zn) and is_molecular_formula(xn)]

            # Check if filtered_tuples is empty
            if filtered_tuples:
                filtered_x, filtered_y, filtered_z = zip(*filtered_tuples)
                # Convert zipped tuples back to lists if necessary
                filtered_x = list(filtered_x)
                filtered_y = list(filtered_y)
                filtered_z = list(filtered_z)
            else:

                # Initialize empty lists or handle the case as needed
                filtered_x = []
                filtered_y = []
                filtered_z = []

            mol_formula = list(filtered_x)
            raw_calc_mass_from_SI = list(filtered_y)
            raw_found_mass_from_SI = list(filtered_z)

        # put the molecular formula in a [ ]+ bracket
        mol_formula = ["[" + element + "]+" for element in mol_formula]
        # conditionally Remove a full stop before and after raw mass strings (raw_calc.. and raw_found..)
        raw_calc_mass_from_SI = [element.rstrip('.') for element in raw_calc_mass_from_SI]
        raw_found_mass_from_SI = [element.rstrip('.') for element in raw_found_mass_from_SI]
        raw_calc_mass_from_SI = [element.lstrip('.') for element in raw_calc_mass_from_SI]
        raw_found_mass_from_SI = [element.lstrip('.') for element in raw_found_mass_from_SI]

        raw_found_mass_from_SI = [extract_number(xxx) for xxx in raw_found_mass_from_SI]
        raw_calc_mass_from_SI = [extract_number(xxx) for xxx in raw_calc_mass_from_SI]

        # convert masses from strings into floating numbers

        mass_calculated_from_SI = [float(element) if element is not None and is_convertible_to_float(element) else 0.01
                                   for element in raw_calc_mass_from_SI]
        mass_reported_from_SI = [float(element) if element is not None and is_convertible_to_float(element) else 0.01
                                   for element in raw_found_mass_from_SI]

        if os.path.basename(pdf_file_path).lower() != 'desktop.ini':
            a=f"Analysis for: {pdf_file_path}"
            print(f"\nAnalysis for: {pdf_file_path}")
            add_sentence(pdf,a)
            if len(mol_formula)==0:
                print("No HRMS data found")
                a=f"No HRMS data found."
                add_sentence(pdf,a)
            if incorrect_formulas:
                print(f"Incorrect Formulas: {incorrect_formulas}")
                a=f"One or more incorrect formulas"
                add_sentence(pdf,a)

        # Calculate monisotopic mass from molecular formula, calculate mass error
        for element1, element2, element3 in zip(mol_formula, mass_calculated_from_SI, mass_reported_from_SI):
            # Calculate the monoisotopic mass for the original formula
            element1 = check_molecular_formula(element1)
            mol_formula_anion = element1.replace("+", "-")
            mol_formula_neutral = element1.replace("+", "")
            calculated_mass_from_formula = Formula(element1).monoisotopic_mass
            calculated_mass_anion = Formula(mol_formula_anion).monoisotopic_mass
            calculated_mass_neutral = Formula(mol_formula_neutral).monoisotopic_mass
            #fun test, delete later - maybe not
            fun1=decrease_element_count(mol_formula_neutral,'H')
            fun1b=mol_formula_neutral.replace("Na","")
            f=Formula(mol_formula_neutral)
            fun_mw=calculate_molecular_weight(mol_formula_neutral)
            fun_mw_minus1=calculate_molecular_weight(fun1)
            fun_mw_minus_Na=calculate_molecular_weight(fun1b)
            fun_mw2=fun_mw_minus1+1
            fun_mw3=fun_mw+1
            fun_mw4=fun_mw+23
            fun_mw5=fun_mw_minus_Na+23
            fun_mw_rounded=f"{fun_mw:.4f}"
            fun_mw2_rounded = f"{fun_mw2:.4f}"
            fun_mw3_rounded = f"{fun_mw3:.4f}"
            fun_mw4_rounded = f"{fun_mw4:.4f}"
            fun_mw5_rounded = f"{fun_mw5:.4f}"
            fun2=Formula(fun1).monoisotopic_mass
            fun2b=f"{fun2:.4f}"
            fun3=fun2+1
            fun4=f"{fun3:.4f}"
            fun5=calculated_mass_neutral+1
            fun6=f"{fun5:.4f}"

            # Format the calculated masses with 4 decimal places
            formatted_calculated_mass = f"{element2:.4f}"
            formatted_reported_mass = f"{element3:.4f}"
            formatted_calculated_mass_from_formula = f"{calculated_mass_from_formula :.4f}"
            formatted_calculated_mass_from_formula_anion = f"{calculated_mass_anion:.4f}"
            formatted_calculated_mass_from_formula_neutral = f"{calculated_mass_neutral:.4f}"
            fm1 = float(formatted_calculated_mass)
            fm2 = float(formatted_reported_mass)
            fm3 = float(formatted_calculated_mass_from_formula)
            fm4 = float(formatted_calculated_mass_from_formula_anion)
            fm5 = float(formatted_calculated_mass_from_formula_neutral)

            # Calculate mass errors
            if fm2 == 0:
                break
            mass_error1 = abs(round((fm1 / fm2 - 1) * 10 ** 6, 1))
            mass_error2 = abs(round((fm3 / fm2 - 1) * 10 ** 6, 1))
            mass_error_anion = abs(round((fm4 / fm2 - 1) * 10 ** 6, 1))
            mass_error_neutral = abs(round((fm5 / fm2 - 1) * 10 ** 6, 1))

            flag=0

            # Cation Mode !!! Print calculated, recalculated, and reported masses with respective errors
            if formatted_calculated_mass == formatted_calculated_mass_from_formula:
                flag=1
                if mass_error2 > 10.0 or mass_error1 > 10.0:
                    a = f"Calculated for {element1} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error2} ppm)"
                    pdf.set_text_color(255, 0, 0)  # Black color
                    add_sentence(pdf,a)
                    pdf.set_text_color(0, 0, 0)  # Black color
                    print(
                        f"Calculated for {element1} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} "
                        f"\033[91mMass Error:  {mass_error1} ppm ({mass_error2} ppm)\033[0m"
                        )
                    error=1
                else:
                    a=f"Calculated for {element1} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error2} ppm)"
                    print(
                        f"Calculated for {element1} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} "
                        f"Mass Error: {mass_error1} ppm ({mass_error2} ppm)"
                        )
                    add_sentence(pdf,a)
                    flag=1,
                    correct=1

            # Check anion mode
            elif formatted_calculated_mass == formatted_calculated_mass_from_formula_anion:
                flag=1
                fm3=fm1
                if mass_error_anion > 10.0 or mass_error1 > 10.0:
                    a = f"Calculated for {mol_formula_anion} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula_anion}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error_anion} ppm)"
                    pdf.set_text_color(255, 0, 0)  # Black color
                    add_sentence(pdf, a)
                    pdf.set_text_color(0, 0, 0)  # Black color
                    print(
                        f"Calculated for {mol_formula_anion} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula_anion}) found {formatted_reported_mass} "
                        f"\033[91mMass Error:  {mass_error1} ppm ({mass_error_anion} ppm)\033[0m"
                    )
                    error = 1
                else:
                    a = f"Calculated for {mol_formula_anion} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula_anion}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error_anion} ppm)"
                    add_sentence(pdf, a)
                    print(
                        f"Calculated for {mol_formula_anion} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula_anion}) found {formatted_reported_mass} "
                        f"Mass Error: {mass_error1} ppm ({mass_error_anion} ppm)"
                        )
                    flag=1
                    correct=1
            # Check neutral

            elif formatted_calculated_mass == formatted_calculated_mass_from_formula_neutral:
                if mass_error_neutral > 10.0:
                    pdf.set_text_color(255, 0, 0)  # Red color
                    a =  f"Calculated for {mol_formula_neutral} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula_neutral}) found {formatted_reported_mass} Mass Error: {mass_error_neutral} ppm ({mass_error_neutral} ppm)"
                    add_sentence(pdf, a)
                    pdf.set_text_color(0, 0, 0)  # Black color
                    print(
                        f"Calculated for {mol_formula_neutral} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula_neutral}) found {formatted_reported_mass} "
                        f"\033[91mMass Error:  {mass_error_neutral} ppm ({mass_error_neutral} ppm)\033[0m"
                    )

                    if mass_error2 > 10.0:
                        pdf.set_text_color(0, 255, 0)  # Green color
                        a=f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} Mass Error: {mass_error2} ppm'
                        add_sentence(pdf, a)
                        pdf.set_text_color(0, 0, 0)  # Black color
                        print(CGREEN + f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} \033[91mMass Error: {mass_error2} ppm\033[0m'+ CEND)
                        error=1
                    else:
                        pdf.set_text_color(0, 255, 0)  # Green color
                        a = f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} Mass Error: {mass_error2} ppm'
                        add_sentence(pdf, a)
                        pdf.set_text_color(0, 0, 0)  # Black color
                        print(
                            CGREEN + f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} Mass Error: {mass_error2} ppm' + CEND)
                        error=1
                else:
                    a = f"Calculated for {mol_formula_neutral} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula_neutral}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error_neutral} ppm)"
                    add_sentence(pdf, a)
                    print(
                        f"Calculated for {mol_formula_neutral} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula_neutral}) found {formatted_reported_mass} "
                        f"Mass Error: {mass_error1} ppm ({mass_error_neutral} ppm)"
                    )
                    correct=1
                    if mass_error2 > 10.0:
                        pdf.set_text_color(0, 255, 0)  # Green color
                        a = f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} Mass Error: {mass_error2} ppm'
                        add_sentence(pdf, a)
                        pdf.set_text_color(0, 0, 0)  # Black color
                        print(CGREEN + f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} \033[91mMass Error: {mass_error2} ppm\033[0m' + CEND)
                        error = 1

                    else:
                        pdf.set_text_color(0, 255, 0)  # Green color
                        a = f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} Mass Error: {mass_error2} ppm'
                        add_sentence(pdf, a)
                        pdf.set_text_color(0, 0, 0)  # Black color
                        print(
                            CGREEN + f'The reported mass was probably measured for the cation: {element1} {formatted_calculated_mass_from_formula} Mass Error: {mass_error2} ppm' + CEND)
                        flag=1
                        error=1

          # Everything else
            else:
                if mass_error2 > 10.0 or mass_error1 > 10.0:
                    pdf.set_text_color(255, 0, 0)  # Red color
                    a = f"Calculated for {element1} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error2} ppm)"
                    add_sentence(pdf, a)
                    pdf.set_text_color(0, 0, 0)  # Black color
                    print(
                        f"Calculated for {element1} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} "
                        f"\033[91mMass Error:  {mass_error1} ppm ({mass_error2} ppm)\033[0m"
                    )
                    error=1
                else:
                    a = f"Calculated for {element1} {formatted_calculated_mass} ({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} Mass Error: {mass_error1} ppm ({mass_error2} ppm)"
                    add_sentence(pdf, a)
                    print(
                        f"Calculated for {element1} {formatted_calculated_mass} "
                        f"({formatted_calculated_mass_from_formula}) found {formatted_reported_mass} "
                        f"Mass Error: {mass_error1} ppm ({mass_error2} ppm)"
                    )
                    flag=1

            if formatted_calculated_mass == fun4:
                print(CCYAN + 'It appears that the high resolution mass was generated by calculating the exact mass for')
                print(f'for the neutral molecule {fun1} ({fun2b}) and adding 1H and +1.0000 => {mol_formula_neutral} ({fun4})'+CEND)
                a='It appears that the high resolution mass was generated by calculating the exact mass for'
                b=f'for the neutral molecule {fun1} ({fun2b}) and adding 1H and +1.0000 => {mol_formula_neutral} ({fun4})'
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                add_sentence(pdf, b)
                pdf.set_text_color(0, 0, 0)  # Orange color

            if formatted_calculated_mass == fun6:
                a='It appears that the high resolution mass was generated by calculating the exact mass for'
                b=f'for the neutral molecule {mol_formula_neutral} ({formatted_calculated_mass_from_formula_neutral}) and adding +1.0000 => ({fun6})'
                print(CCYAN + 'It appears that the high resolution mass was generated by calculating the exact mass for')
                print( f'for the neutral molecule {mol_formula_neutral} ({formatted_calculated_mass_from_formula_neutral}) and adding +1.0000 => ({fun6})')
                new_formula=increase_element_count(element1,'H')
                new_mass=Formula(new_formula).monoisotopic_mass
                formatted_new_mass=f"{new_mass:.4f}"
                fm6 = float(formatted_new_mass)
                mass_error6 = abs(round((fm6 / fm2 - 1) * 10 ** 6, 1))
                print(f'The molecular formula for [M+H]+ is {new_formula}, the correct mass is: {formatted_new_mass} Mass error: {mass_error6} ppm'+CEND)
                c=f'The molecular formula for [M+H]+ is {new_formula}, the correct mass is: {formatted_new_mass} Mass error: {mass_error6} ppm'
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                add_sentence(pdf, b)
                add_sentence(pdf, c)
                pdf.set_text_color(0, 0, 0)

            if formatted_calculated_mass == fun_mw_rounded:
                a=f'ALERT! The molecular weight ({fun_mw_rounded}) was calculated, not the exact mass ({formatted_calculated_mass_from_formula})'
                print(CCYAN + f'ALERT! The molecular weight ({fun_mw_rounded}) was calculated, not the exact mass ({formatted_calculated_mass_from_formula})' + CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                pdf.set_text_color(0, 0, 0)
            if formatted_calculated_mass == fun_mw2_rounded:
                a=f'ALERT! Calculated mass was calculating MW for {fun1} and adding 1.0000 ({fun_mw2_rounded}) [M+H]'
                print(CCYAN + f'ALERT! Calculated mass was calculating MW for {fun1} and adding 1.0000 ({fun_mw2_rounded}) [M+H]' + CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                pdf.set_text_color(0, 0, 0)
            if formatted_calculated_mass == fun_mw3_rounded:
                a=f'ALERT! Calculated mass was calculating MW for {mol_formula_neutral} and adding 1.0000 ({fun_mw3_rounded}) [M+H]'
                print(CCYAN + f'ALERT! Calculated mass was calculating MW for {mol_formula_neutral} and adding 1.0000 ({fun_mw3_rounded}) [M+H]' + CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                pdf.set_text_color(0, 0, 0)

            if formatted_calculated_mass == fun_mw4_rounded:
                a="Alert! The molecular weight + 23.0000 has been used instead of the exact mass"
                print(CCYAN + f'Alert! The molecular weight + 23.0000 has been used instead of the exact mass'+ CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                pdf.set_text_color(0, 0, 0)


            if formatted_calculated_mass == fun_mw5_rounded:
                a="Alert! The molecular weight + 23.0000 has been used instead of the exact mass"
                print(CCYAN + f'Alert! The molecular weight + 23.0000 has been used instead of the exact mass'+ CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, a)
                pdf.set_text_color(0, 0, 0)

            if differ_in_single_digit_except_last_two(fm1,fm3):
                print(CCYAN + 'The calculated mass might contain a typo' + CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, 'The calculated mass might contain a typo')
                pdf.set_text_color(0, 0, 0)  # Black color

            if have_swapped_adjacent_digits(fm1,fm3):
                print(CCYAN + 'The calculated and the recalculated mass appear to be transposed by two digits.' + CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, 'The calculated and the recalculated mass appear to be transposed by two digits.')
                pdf.set_text_color(0, 0, 0)  # Black color

            if have_swapped_adjacent_digits(fm1,fm2):
                print(CCYAN + 'The calculated mass and the measured mass appear to be transposed by two digits.' + CEND)
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, 'The calculated f and the measured mass appear to be transposed by two digits.')
                pdf.set_text_color(0, 0, 0)  # Black color
            elif int(fm2) != int(fm1) and mass_error1 > 10.0:
                pdf.set_text_color(255, 165, 0)  # Orange color
                add_sentence(pdf, 'The reported calculated and measured HR masses differ in their integers.')
                pdf.set_text_color(0, 0, 0)  # Orange color
                print(CCYAN + 'The reported calculated and measured HR masses differ in their integers.' + CEND)

            # Check whether one or more of the following atoms is missing in the reported molecular formula
            elements_to_test = ['C', 'H', 'O']  # Add more elements as needed
            for i in range(10):
                for element_to_test in elements_to_test:
                    new_formula = element1
                    for j in range(i+1):
                        if is_element_in_formula(new_formula, element_to_test):
                            new_formula = increase_element_count(new_formula, element_to_test)
                        else:
                            new_formula = new_formula.replace("]+", f"{element_to_test}]+")
                    check_formula('Adding','-atoms(s)')

            # Check whether one or more of the following atoms is missing in the reported molecular formula
            elements_to_test = [ 'D','S', 'Na', 'N',  'P', 'Si', 'Se', 'Li', 'B','Br','F','Cl','K','I','Ag','Ru']  # Add more elements as needed
            for i in range(4):
                for element_to_test in elements_to_test:
                    new_formula = element1
                    for j in range(i+1):
                        if is_element_in_formula(new_formula, element_to_test):
                            new_formula = increase_element_count(new_formula, element_to_test)
                        else:
                            new_formula = new_formula.replace("]+", f"{element_to_test}]+")
                    check_formula('Adding','-atoms(s)')

            #flag = 0
            if flag==0:
                elements_to_test = ['C', 'H',  'O']  # Add more elements as needed
                for i in range(10):
                    for element_to_test in elements_to_test:
                        new_formula = element1
                        for j in range(i + 1):
                            new_formula = decrease_element_count(new_formula, element_to_test)
                            if flag==0:
                                check_formula('Removing','-atoms(s)')

            if flag==0:
                elements_to_test = ['D', 'S', 'Na', 'N',  'P', 'Si', 'Se', 'Li', 'B', 'Br', 'F', 'Cl', 'K',
                                    'I', 'Ag','Ru']  # Add more elements as needed
                for i in range(4):
                    for element_to_test in elements_to_test:
                        new_formula = element1
                        for j in range(i + 1):
                            new_formula = decrease_element_count(new_formula, element_to_test)
                            if flag==0:
                                check_formula('Removing','-atoms(s)')

            elements_to_test = ['S', 'Na', 'N', 'O', 'P', 'Si', 'Se', 'Li', 'K', 'B', 'Br', 'F',
                                'Cl', 'D']  # Add more elements as needed
            if flag == 0:
                elements_to_replace = ["[18]", "[35]", "[10]", "[37]", "[79]", "[81]", "[11]", "[28]", "[23]", "[80]",
                                       "[]"]
                for element_to_test in elements_to_test:
                    new_formula = delete_element_from_formula(element1, element_to_test)
                    for elem in elements_to_replace:
                        new_formula = new_formula.replace(elem, "")
                    i=0
                    check_formula('Removing','-atoms(s)')

            new_formula = element1
            i=0
            if flag == 0:
                new_formula = increase_element_count(new_formula, 'C')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'CH'
                check_formula('Adding a ', 'group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'CH2'
                if flag == 0:
                    check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'CH3'
                if flag == 0:
                    check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'CH4'
                if flag == 0:
                    check_formula('Adding', '-group')

            new_formula = element1
            i=0
            if flag == 0:
                new_formula = increase_element_count(new_formula, 'O')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'OH'
                check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'H2O'
                if flag == 0:
                    check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'H3O+'
                if flag == 0:
                    check_formula('Adding', '-group')

            new_formula = element1
            i=0
            if flag == 0:
                new_formula = increase_element_count(new_formula, 'N')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'NH'
                check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'NH2'
                if flag == 0:
                    check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'NH3'
                if flag == 0:
                    check_formula('Adding', '-group')
                new_formula = increase_element_count(new_formula, 'H')
                element_to_test = 'NH4+'
                if flag == 0:
                    check_formula('Adding', '-group')

            new_formula = element1
            i=0
            if flag == 0:
                new_formula = decrease_element_count(new_formula, 'C')
                new_formula = decrease_element_count(new_formula, 'H')
                element_to_test = 'CH'
                check_formula('Removing a ', 'group')
                new_formula = decrease_element_count(new_formula, 'H')
                element_to_test = 'CH2'
                if flag == 0:
                    check_formula('Removing', '-group')
                new_formula = decrease_element_count(new_formula, 'H')
                element_to_test = 'CH3'
                if flag == 0:
                    check_formula('Removing', '-group')
                new_formula = decrease_element_count(new_formula, 'H')
                element_to_test = 'CH4'
                if flag == 0:
                    check_formula('Removing', '-group')

            new_formula = element1
            i = 0
            if flag == 0:
                if is_element_in_formula(new_formula, 'O'):
                    new_formula = decrease_element_count(new_formula, 'O')
                    if new_formula==element1:
                        delete_element_from_formula(new_formula, 'O')
                    new_formula = decrease_element_count(new_formula, 'H')
                    element_to_test = 'OH'
                    check_formula('Removing', '-group')
                    if flag == 0:
                        new_formula = decrease_element_count(new_formula, 'H')
                        element_to_test = 'H2O'
                        check_formula('Removing', '-group')
                    if flag == 0:
                        new_formula = decrease_element_count(new_formula, 'H')
                        element_to_test = 'H3O'
                        check_formula('Removing', '-group')

            new_formula = element1
            i = 0
            if flag == 0:
                if is_element_in_formula(new_formula, 'N'):
                    new_formula = decrease_element_count(new_formula, 'N')
                    if new_formula == element1:
                        delete_element_from_formula(new_formula, 'N')
                    new_formula = decrease_element_count(new_formula, 'H')
                    element_to_test = 'NH'
                    check_formula('Removing', '-group')
                    if flag == 0:
                        new_formula = decrease_element_count(new_formula, 'H')
                        element_to_test = 'NH2'
                        check_formula('Removing', '-group')
                    if flag == 0:
                        new_formula = decrease_element_count(new_formula, 'H')
                        element_to_test = 'NH3'
                        check_formula('Removing', '-group')
                    if flag == 0:
                        new_formula = decrease_element_count(new_formula, 'H')
                        element_to_test = 'NH4'
                        check_formula('Removing', '-group')

            new_formula = element1
            i = 0
            if flag == 0:
                if is_element_in_formula(new_formula, 'Na'):
                    new_formula = decrease_element_count(new_formula, 'Na')
                    if new_formula == element1:
                        delete_element_from_formula(new_formula, 'Na')
                    new_formula = increase_element_count(new_formula, 'H')
                    element_to_test = 'Na'
                    check_formula('Replacing', '+ by H+')

            new_formula = element1
            i = 0
            if flag == 0:
                if is_element_in_formula(new_formula, 'H'):
                    new_formula = decrease_element_count(new_formula, 'H')
                    if new_formula == element1:
                        delete_element_from_formula(new_formula, 'H')
                    new_formula = new_formula.replace("]+","Na]+")
                    element_to_test = 'H'
                    check_formula('Replacing', '+ by Na+')

            new_formula = element1
            i = 0
            if flag == 0:
                if is_element_in_formula(new_formula, 'Na'):
                    delete_element_from_formula(new_formula, 'Na')
                    new_formula = new_formula.replace("]+","K]+")
                    element_to_test = 'Na'
                    check_formula('Replacing', '+ by K+')

            i = 0
            if flag == 0:
                new_formula=element1
                if is_element_in_formula(new_formula, 'Na'):
                    new_formula=new_formula.replace('Na','')
                    new_formula_neutral = new_formula.replace("+", "")
                    x=Formula(new_formula_neutral).monoisotopic_mass
                    y=x+1
                    mass=f"{x:.4f}"
                    formatted_modified_mass_neutral = f"{y:.4f}"
                    if formatted_modified_mass_neutral == formatted_calculated_mass:
                        print(
                            CCYAN + 'It appears that the high resolution mass was generated by calculating the exact mass for')
                        print(
                            f'for the neutral molecule {new_formula_neutral} ({mass}) and adding +1.0000 => {formatted_calculated_mass}')

                        a='It appears that the high resolution mass was generated by calculating the exact mass for'
                        b=f'for the neutral molecule {new_formula_neutral} ({mass}) and adding +1.0000 => {formatted_calculated_mass}'
                        pdf.set_text_color(255, 165, 0)  # Orange color
                        add_sentence(pdf, a)
                        add_sentence(pdf, b)
                        new_formula=increase_element_count(new_formula,'H')
                        new_mass=Formula(new_formula).monoisotopic_mass
                        z=f"{new_mass:.4f}"
                        new_mass=float(z)
                        mass_error7 = abs(round((new_mass / fm2 - 1) * 10 ** 6, 1))
                        print(
                            f'Thee molecular formula for [M+H]+ is {new_formula}, the correct mass is: {z} Mass error: {mass_error7} ppm' + CEND)
                        c= f'The molecular formula for [M+H]+ is {new_formula}, the correct mass is: {z} Mass error: {mass_error7} ppm'
                        add_sentence(pdf, c)
                        pdf.set_text_color(0, 0, 0)  # Black color

            if flag == 0:
                new_formula=element1
                if is_element_in_formula(new_formula, 'Na'):
                    new_formula=new_formula.replace('Na','')
                    new_formula_neutral = new_formula.replace("+", "")
                    x=Formula(new_formula_neutral).monoisotopic_mass
                    y=x+23
                    mass=f"{x:.4f}"
                    formatted_modified_mass_neutral = f"{y:.4f}"
                    if formatted_modified_mass_neutral == formatted_calculated_mass:
                        print(
                            CCYAN + 'It appears that the high resolution mass was generated by calculating the exact mass for')
                        print(
                            f'for the neutral molecule {new_formula_neutral} ({mass}) and adding +23.0000 => {formatted_calculated_mass}')
                        print('The correct mass and mass error are shown above in parenthesis'+CEND)
                        a='It appears that the high resolution mass was generated by calculating the exact mass for'
                        b=f'for the neutral molecule {new_formula_neutral} ({mass}) and adding +23.0000 => {formatted_calculated_mass}'
                        c='The correct mass and mass error are shown above in parenthesis'
                        pdf.set_text_color(255, 165, 0)  # Orange color
                        add_sentence(pdf, a)
                        add_sentence(pdf, b)
                        add_sentence(pdf, c)
                        pdf.set_text_color(0, 0, 0)  # Black color

        if error == 0 and correct==1:
            add_sentence(pdf,'Very nice, no mistakes!')
            print('Very nice, no mistakes!')
        add_sentence(pdf, "")

    except Exception as e:
        # Handle the error, or simply print a message
        print('')
        print(pdf_file_path)
        print('an error occurred:')
        print(e)
        continue  # Continue to the next iteration of the loop

end_time = time.time()
elapsed_time = end_time - start_time
minutes, seconds = divmod(elapsed_time, 60)
print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")
pdf.output(output_file)