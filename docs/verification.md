# Content Verification Checklist

## Content Completeness Counts

- [x] Techniques: `50`
- [x] Racials: `33` total (`11 races x 3`)
- [x] Transformations: `31`
- [x] Iconic NPC definitions: `14`
- [x] Questline scaffolds: `41`
- [x] Unlock mapping coverage (techniques / transformations / racials): complete

## Registry File Paths

- Techniques registry: `live/world/techniques.py`
- Transformations registry: `live/world/forms.py`
- LSSJ system: `live/world/lssj.py`
- Racial registry: `live/world/racials.py`
- Unlock coverage map: `live/world/content_unlocks.py`
- NPC definitions: `live/world/npc_content.py`
- Quest scaffolding: `live/world/quests.py`
- Content validation helpers: `live/world/content_validation.py`

## UI / Route File Paths

- Technique UI route: `live/web/website/urls.py`
- Technique UI view: `live/web/website/views/technique_ui.py`
- Technique UI template: `live/web/templates/website/db_techniques.html`
- In-game UI helper command: `live/commands/db_commands.py`

## Command / Typeclass Integration Paths

- Command implementations: `live/commands/db_commands.py`
- Command registration: `live/commands/commandset.py`
- Character defaults / content state init: `live/typeclasses/characters.py`
- Trainer NPC hooks: `live/typeclasses/npcs.py`
- PL form integration: `live/world/power.py`

## Validation Commands Run (Local)

### 1) Python compile pass

Command:

```powershell
python -m compileall live\world live\commands live\typeclasses live\web\website\views
```

Result:

- Passed (`Exit code 0`)

### 2) Content counts + registry validation

Command (inline script):

```powershell
@'
import sys, json
sys.path.insert(0, 'live')
from world.content_validation import validate_all_content
print(json.dumps(validate_all_content(), indent=2))
'@ | python -
```

Key output (summarized):

- `techniques: 50`
- `transformations: 31`
- `racials_total: 33`
- `npcs: 14`
- `questlines: 41`
- `errors.techniques: []`
- `errors.transformations: []`
- `errors.racials: []`
- `errors.unlocks: []`

### 3) Technique UI serialization payload smoke test

Command (inline script):

```powershell
@'
import sys
sys.path.insert(0, 'live')
from world.content_validation import validate_all_content
from web.website.views.technique_ui import _serialize_techniques, _serialize_racials, _serialize_forms
result = validate_all_content()
assert not any(result['errors'].values())
assert result['counts']['techniques'] == 50
print('technique_ui_payload_counts', len(_serialize_techniques()), len(_serialize_racials()), len(_serialize_forms()))
'@ | python -
```

Observed output:

- `technique_ui_payload_counts 50 33 31`

### 4) Django route reverse check for Technique UI

Command (inline script):

```powershell
$env:DJANGO_SETTINGS_MODULE='server.conf.settings'
@'
import sys
sys.path.insert(0, 'live')
import django
django.setup()
from django.urls import reverse
print(reverse('db_technique_ui'))
'@ | python -
```

Observed output:

- `/db/techniques/`

### 5) Live instance launch test (Codex copy)

Commands:

```powershell
cd Agents\Codex\live
evennia stop
evennia start
evennia status
```

Observed:

- Portal and Server both running on the randomized Codex port block (`5143-5149`)

HTTP checks:

```powershell
python - <<EOF
import urllib.request
for url in ["http://127.0.0.1:5144", "http://127.0.0.1:5144/db/techniques/"]:
    with urllib.request.urlopen(url, timeout=8) as r:
        print(url, r.status)
EOF
```

Observed:

- Web root -> `200`
- Technique UI -> `200`

### 6) Live command smoke test (running Codex DB objects / command classes)

Method:

- Executed the command classes against the real `admin` character object in the running Codex database and captured `msg()` output.
- This validates command logic and runtime integrations even though telnet transcript capture was unreliable due telnet negotiation/compression.

Commands validated:

- `forms`
- `lssj status`
- `listtech`
- `spawntrainer master_roshi`
- `talk master roshi`
- `techui`

Observed results (summarized):

- `forms` returned transformation list with unlock source labels
- `lssj status` returned LSSJ state block (`unlocked=False`, `PLx=1.00`)
- `listtech` returned categorized technique list with costs/cooldowns/unlock sources
- `spawntrainer master_roshi` succeeded and created NPC in room
- `talk master roshi` returned bio/dialogue/questline/reward scaffold text
- `techui` returned `/db/techniques/` route and current loadout summary

Runtime fix discovered during this test:

- `spawntrainer` initially failed because `create_object` was imported from `evennia` top-level (resolved to `None`)
- Fixed in `live/commands/db_commands.py` by importing:
  - `from evennia.utils.create import create_object`

## Not Run (Documented)

- Full interactive telnet/webclient transcript with readable command output
- Web page rendering screenshot capture

Reason:

- Telnet automation output was obscured by protocol negotiation/compression in the ad-hoc socket harness. Core runtime behavior was instead validated via live server boot, HTTP endpoint checks, and command-class execution against real game objects in the running Codex DB.

## Manual QA Checklist (Next Pass)

- [ ] Start Evennia services
- [ ] Capture a readable telnet/webclient transcript for the validated commands
- [ ] Open `/db/techniques/` manually and visually verify search/filter/loadout interactions
