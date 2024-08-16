""" 
MODS XML Validator 
- Intentionally focuses on MODS to allow for mods-specific enhancements.
- First TODO: allow an additional argument to a schematron file.
"""

import argparse
from lxml import etree

def validate_mods_xml(xml_file_path):
    ## Parse the XML file
    try:
        with open(xml_file_path, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file)
    except (etree.XMLSyntaxError, IOError) as e:
        print(f"Error reading XML file: {e}")
        return False

    ## Extract the schema location from the XML
    schema_location = xml_doc.getroot().attrib.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation')
    if not schema_location:
        print("No schema location found in XML.")
        return False

    ## The schema location typically contains pairs of namespace and schema URL
    ## For MODS, we're interested in the second part (the URL to the XSD file)
    schema_url = schema_location.split()[1]

    ## Load the schema
    try:
        with open(schema_url, 'rb') as schema_file:
            schema_doc = etree.parse(schema_file)
        xml_schema = etree.XMLSchema(schema_doc)
    except (etree.XMLSyntaxError, IOError) as e:
        print(f"Error loading schema: {e}")
        return False

    ## Validate the XML document against the schema
    if xml_schema.validate(xml_doc):
        print("The XML is valid according to the schema.")
        return True
    else:
        print("The XML is invalid according to the schema.")
        for error in xml_schema.error_log:
            print(error.message)
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate a MODS XML file against its embedded schema.')
    parser.add_argument('--mods_path', required=True, help='Path to the MODS XML file to validate.')
    
    args = parser.parse_args()
    
    validate_mods_xml(args.mods_path)


## dundermain
if __name__ == '__main__':
    main()
