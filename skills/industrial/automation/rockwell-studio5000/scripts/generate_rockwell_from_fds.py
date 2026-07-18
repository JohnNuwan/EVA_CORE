import os
import sys
import json
import re
import argparse
import asyncio

# Setup dynamic path connection to Helios root directory for agent imports
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Helper function to dynamically import and install dependency if missing
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        return __import__(import_name)
    except ImportError:
        print(f"[INFO] Dependance '{package_name}' non trouvee. Installation via pip...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return __import__(import_name)
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'installation de {package_name}: {e}")
            sys.exit(1)

# Dynamically import dependencies
pypdf = install_and_import("pypdf")
docx = install_and_import("python-docx", "docx")

from agent.auxiliary_client import async_call_llm

def extract_text_from_pdf(pdf_path: str) -> str:
    text_parts = []
    with open(pdf_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- PAGE {i+1} ---\n{page_text}")
    return "\n".join(text_parts)

def extract_text_from_docx(docx_path: str) -> str:
    doc = docx.Document(docx_path)
    text_parts = []
    # Extract from paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text.strip())
    # Extract from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                text_parts.append(" | ".join(row_text))
    return "\n".join(text_parts)

def escape_xml_attr(val: str) -> str:
    if not val:
        return ""
    val = str(val)
    val = val.replace("&", "&amp;")
    val = val.replace("<", "&lt;")
    val = val.replace(">", "&gt;")
    val = val.replace('"', "&quot;")
    val = val.replace("'", "&apos;")
    return val

def generate_aoi_xml(name: str, description: str, parameters: list, local_tags: list, st_code: str) -> str:
    # Ensure EnableIn and EnableOut are present in parameters
    has_enable_in = any(p.get("name", "").lower() == "enablein" for p in parameters)
    has_enable_out = any(p.get("name", "").lower() == "enableout" for p in parameters)
    
    param_xml_lines = []
    if not has_enable_in:
        param_xml_lines.append('        <Parameter Name="EnableIn" Usage="Input" DataType="BOOL" Required="false" Visible="false" Description="Enable Input"/>')
    if not has_enable_out:
        param_xml_lines.append('        <Parameter Name="EnableOut" Usage="Output" DataType="BOOL" Required="false" Visible="false" Description="Enable Output"/>')
        
    for p in parameters:
        p_name = escape_xml_attr(p.get("name", ""))
        p_usage = escape_xml_attr(p.get("usage", "Input"))
        p_data_type = escape_xml_attr(p.get("data_type", "BOOL"))
        p_desc = escape_xml_attr(p.get("description", ""))
        
        # Rockwell AOI Usage values: Input, Output, InOut
        if p_usage.lower() == "input":
            p_usage = "Input"
        elif p_usage.lower() == "output":
            p_usage = "Output"
        else:
            p_usage = "InOut"
            
        param_xml_lines.append(f'        <Parameter Name="{p_name}" Usage="{p_usage}" DataType="{p_data_type}" Required="false" Visible="true" Description="{p_desc}"/>')
        
    local_tag_xml_lines = []
    for t in local_tags:
        t_name = escape_xml_attr(t.get("name", ""))
        t_data_type = escape_xml_attr(t.get("data_type", "BOOL"))
        t_desc = escape_xml_attr(t.get("description", ""))
        
        local_tag_xml_lines.append(f'        <LocalTag Name="{t_name}" DataType="{t_data_type}" Description="{t_desc}"/>')
        
    parameters_xml = "\n".join(param_xml_lines)
    local_tags_xml = "\n".join(local_tag_xml_lines)
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.00" TargetName="{escape_xml_attr(name)}" TargetType="AddOnInstructionDefinition">
  <AddOnInstructionDefinitions>
    <AddOnInstructionDefinition Name="{escape_xml_attr(name)}" Revision="1.0" ExecutionOrder="0">
      <Parameters>
{parameters_xml}
      </Parameters>
      <LocalTags>
{local_tags_xml}
      </LocalTags>
      <Routines>
        <Routine Name="Logic" Type="StructuredText">
          <Content>
            <![CDATA[{st_code}]]>
          </Content>
        </Routine>
      </Routines>
    </AddOnInstructionDefinition>
  </AddOnInstructionDefinitions>
</RSLogix5000Content>
"""
    return xml_content

def generate_routine_xml(name: str, st_code: str) -> str:
    xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.00" TargetName="{escape_xml_attr(name)}" TargetType="Routine">
  <Routines>
    <Routine Name="{escape_xml_attr(name)}" Type="StructuredText">
      <Content>
        <![CDATA[{st_code}]]>
      </Content>
    </Routine>
  </Routines>
</RSLogix5000Content>
"""
    return xml_content

SYSTEM_PROMPT = """You are an expert Control Systems Engineer specialized in Rockwell Automation (Allen-Bradley Logix Designer / Studio 5000).
Your task is to analyze the Functional Design Specification (FDS) of an industrial sequence and generate:
1. Syntax-compliant Rockwell Structured Text (ST) logic implementing the sequence, states, timers, interlocks, hand valve checks, and control modules described.
2. A structured declaration of all required parameters (Inputs, Outputs, InOuts) and local tags.

--- RULES FOR ROCKWELL STRUCTURED TEXT (ST) ---
- Always use ':=' for assignments (never '=' for assignment).
- Semicolons ';' are required at the end of each statement (including inside IF-THEN and CASE statements).
- Do NOT use Siemens, Codesys, or Beckhoff specific features (such as S5T#, #variable, TON.Q, or direct variable declarations inside ST).
- Implement timers using the Rockwell 'TIMER' type and 'TON' instruction:
  * To run/execute a timer: TON(TimerName);
  * Preset time is set in milliseconds (.PRE): TimerName.PRE := 5000; (for 5 seconds)
  * Enable bit: TimerName.TimerEnable := boolean_condition;
  * Done bit is checked using: TimerName.DN (e.g. IF TimerName.DN THEN ...)
- Implement sequences using a clear state machine (CASE State OF 0: ... 10: ... END_CASE;).
- All variables used in Structured Text must be declared in either 'parameters' or 'local_tags'.

--- OUTPUT FORMAT ---
You must output a single valid JSON block containing the generated program details.
JSON Schema:
{
  "name": "Alphanumeric name for the routine / AOI, starting with a letter, using underscores, e.g. 'Calibration_Liquid'",
  "description": "Short description of the logic based on the FDS",
  "st_code": "The full Structured Text code block with CDATA-safe content",
  "parameters": [
    {
      "name": "ParameterName",
      "usage": "Input" | "Output" | "InOut",
      "data_type": "BOOL" | "REAL" | "INT" | "DINT" | "TIMER" | etc.,
      "description": "Short description of the parameter"
    }
  ],
  "local_tags": [
    {
      "name": "TagName",
      "data_type": "BOOL" | "REAL" | "INT" | "DINT" | "TIMER" | etc.,
      "description": "Short description of the local tag"
    }
  ]
}

Ensure your response is valid JSON and contains no extra text outside the JSON block. Do not include markdown code block syntax inside the json values themselves.
"""

USER_PROMPT_TEMPLATE = """Here is the extracted text of the Functional Design Specification (FDS) document:

{fds_text}

Analyze the document, identify the main state machine / sequence (Steps, transitions, timers, actions, permissive/interlock conditions, hand valve positioning requirements), and generate the JSON block with the Rockwell ST code, parameters, and local tags.
"""

async def main():
    parser = argparse.ArgumentParser(description="Genere du code Rockwell ST et L5X a partir d'un fichier FDS (PDF ou DOCX).")
    parser.add_argument("fds_file", help="Chemin vers le fichier FDS (PDF ou DOCX)")
    parser.add_argument("--skid", help="Numero de skid pour remplacer 'SKXX' par 'SK' suivi du numero (ex: 01, 02)")
    parser.add_argument("--verbose", action="store_true", help="Affiche plus de logs")
    args = parser.parse_args()

    # 1. Verification du fichier d'entree
    if not os.path.exists(args.fds_file):
        print(f"[ERROR] Le fichier specifie n'existe pas : {args.fds_file}")
        sys.exit(1)

    spec_name = os.path.splitext(os.path.basename(args.fds_file))[0]
    file_ext = os.path.splitext(args.fds_file)[1].lower()

    print(f"[INFO] Lecture de la specification fonctionnelle '{spec_name}' ({file_ext})...")

    # 2. Extraction du texte
    try:
        if file_ext == ".pdf":
            fds_text = extract_text_from_pdf(args.fds_file)
        elif file_ext in [".docx", ".doc"]:
            fds_text = extract_text_from_docx(args.fds_file)
        else:
            print(f"[ERROR] Format de fichier non supporte : {file_ext}. Veuillez fournir un fichier PDF ou DOCX.")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Impossible d'extraire le texte du document FDS : {e}")
        sys.exit(1)

    print(f"[SUCCESS] Texte extrait avec succes. Nombre de caracteres : {len(fds_text)}")

    # Remplacement du pattern SKXX si le numero de skid est specifie
    if args.skid:
        print(f"[INFO] Remplacement de 'SKXX' par 'SK{args.skid}'...")
        fds_text = re.sub(r'SKXX', f'SK{args.skid}', fds_text, flags=re.IGNORECASE)
        # Remplacement optionnel dans le nom du projet
        spec_name = re.sub(r'SKXX', f'SK{args.skid}', spec_name, flags=re.IGNORECASE)

    # Troncature raisonnable si le document est anormalement grand (> 300 000 caracteres)
    if len(fds_text) > 300000:
        print("[WARNING] Le document est tres volumineux. Troncature du texte a 300 000 caracteres...")
        fds_text = fds_text[:300000]

    # 3. Appel au modele de langage
    print("[LLM] Analyse par l'IA et generation du code Structured Text et des configurations L5X...")
    
    user_prompt = USER_PROMPT_TEMPLATE.format(fds_text=fds_text)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        resp = await async_call_llm(
            messages=messages,
            timeout=240.0
        )
        
        # Extraction du contenu textuel de la reponse
        content = ""
        if hasattr(resp, "choices") and resp.choices:
            content = resp.choices[0].message.content
        elif hasattr(resp, "message"):
            content = resp.message.content
        else:
            content = str(resp)

        if args.verbose:
            print("\n--- REPONSE DU LLM ---")
            print(content)
            print("----------------------\n")

        # 4. Parsing de la reponse JSON
        # Nettoyage si emballe dans des backticks markdown
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            first_bracket = content.find("{")
            last_bracket = content.rfind("}")
            if first_bracket != -1 and last_bracket != -1:
                json_str = content[first_bracket:last_bracket+1]
            else:
                json_str = content

        result = json.loads(json_str)

    except json.JSONDecodeError as je:
        print(f"[ERROR] Erreur lors du decodage du JSON renvoye par l'IA : {je}")
        print("Reponse brute de l'IA :")
        print(content)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Erreur lors de la generation ou de la communication avec l'IA: {e}")
        sys.exit(1)

    # 5. Extraction des champs du JSON
    name = result.get("name", spec_name).replace(" ", "_").replace("-", "_")
    description = result.get("description", f"Logic based on {spec_name}")
    st_code = result.get("st_code", "")
    parameters = result.get("parameters", [])
    local_tags = result.get("local_tags", [])

    print(f"[GEN] Generation pour l'instruction/routine : '{name}'")
    print(f"   - Parametres identifies : {len(parameters)}")
    print(f"   - Variables locales identifies : {len(local_tags)}")

    # 6. Generation des formats de sortie
    aoi_xml = generate_aoi_xml(name, description, parameters, local_tags, st_code)
    routine_xml = generate_routine_xml(name, st_code)

    # 7. Sauvegarde des fichiers
    output_folder_name = spec_name
    if args.skid:
        if "SKXX" in spec_name.upper():
            output_folder_name = re.sub(r'SKXX', f'SK{args.skid}', spec_name, flags=re.IGNORECASE)
        else:
            output_folder_name = f"{spec_name}_SK{args.skid}"

    output_dir = os.path.join(root_dir, "output", "rockwell_gen", output_folder_name)
    os.makedirs(output_dir, exist_ok=True)

    st_file_path = os.path.join(output_dir, f"{name}.st")
    aoi_file_path = os.path.join(output_dir, f"{name}_AOI.L5X")
    routine_file_path = os.path.join(output_dir, f"{name}_Routine.L5X")

    with open(st_file_path, "w", encoding="utf-8") as f:
        f.write(st_code)
    
    with open(aoi_file_path, "w", encoding="utf-8") as f:
        f.write(aoi_xml)

    with open(routine_file_path, "w", encoding="utf-8") as f:
        f.write(routine_xml)

    print("\n[SUCCESS] GENERATION TERMINEE AVEC SUCCES !")
    print(f"Dossier de sortie : {output_dir}")
    print(f"  - Code Structured Text brut : {st_file_path}")
    print(f"  - Fichier import Add-On Instruction (AOI) : {aoi_file_path}")
    print(f"  - Fichier import Routine standard : {routine_file_path}")

if __name__ == "__main__":
    asyncio.run(main())
