# Aufgaben
- Konvertierung von strukturiert vorliegenden Metadaten in Dataverse-konforme JSON-Datei
  - Input: Metadaten in strukturiertem Format
  - Output: Dataverse-konforme JSON-Datei, die Metadaten anhand der aktuell vorliegenden Metadatenkonfiguration (tsv-files) der Dataverse-Installation beinhaltet

- Strukturierte Metadatenformate registrieren und Mapping definieren
- Inkonsistenzen von Mappings zu aktueller Dataverse-Metadaten-Konfiguration testen

# Endpoints
## Metadatenkonvertierung

### POST /metadata/<string:scheme>
- Path-Parameter scheme (string, default='update'): Identifizierung das Schemas, in dem die gepostete Metadatendatei vorliegt
- Query-Parameter method: Gibt das Output-Format an. 
  - edit:kompatibel zum Edit-Metadata-Endpoint, 
  - update:kompatibel zum Update-Metadata-Endpoint (Standard), 
  - create:kompatibel zum Anlegen eines neuen Datensatzes auf Dataverse 
- Query-Parameter verbose (boolean, default=False): Gibt an, ob zusätzliche Informationen zum Erfolg gegeben werden sollen
- Body: Metadatendatei, die zu konvertieren ist mit Content-Type: text/plain, application/xml oder application/json
- Output: Dataverse-kompatibles JSON (verbose=False) oder 
  ```
  {
   'success': <True|False>,
   'messages': [
      {'level': <error|warning|message>,
       'message': <textual message>
       },
    'result': <Dataverse-compatible JSON-Structure to be used for Edit, Update or Create-Endpoints>
   ]
  ```
