"""Update BTS software version in all templates."""
import os, io, zipfile, re, shutil

NEW_VERSION = "BTS3900_5900 V100R019C10SPC290"
BTS_PATTERN = re.compile(r'BTS\d+\s*V100R\d{3}C\d{2}SPC\d{3}')

templates_dir = r'C:\Users\MDYakovleva\Documents\Lazy Integration\templates'
updated = 0
errors = 0

for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if not (f.endswith('.xlsx') or f.endswith('.xlsm')):
            continue
        path = os.path.join(root, f)
        
        try:
            # Read the file
            with open(path, 'rb') as fh:
                data = fh.read()
            
            z = zipfile.ZipFile(io.BytesIO(data), 'r')
            new_data = io.BytesIO()
            found = False
            
            with zipfile.ZipFile(new_data, 'w', zipfile.ZIP_DEFLATED) as out:
                for item in z.infolist():
                    content = z.read(item.filename)
                    
                    if item.filename.endswith('.xml'):
                        text = content.decode('utf-8', errors='replace')
                        matches = BTS_PATTERN.findall(text)
                        if matches:
                            new_text = BTS_PATTERN.sub(NEW_VERSION, text)
                            if new_text != text:
                                content = new_text.encode('utf-8')
                                found = True
                    
                    out.writestr(item, content)
            
            z.close()
            
            if found:
                # Write back
                with open(path, 'wb') as fh:
                    fh.write(new_data.getvalue())
                updated += 1
                print(f'Updated: {f}')
        
        except Exception as e:
            errors += 1
            print(f'Error: {f}: {e}')

print(f'\nDone: {updated} templates updated, {errors} errors')
