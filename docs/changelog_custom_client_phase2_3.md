# DBForged Custom Web Client - Phase 2 & 3 Completed

## Summary of Changes
Implemented a fully autonomous visual game client using HTML5 Canvas and CSS Glassmorphism logic tied directly to Evennia's native Out-Of-Band (OOB) JSON WebSocket payloads. This replaces the old text-based "webclient" view.

## Scope Included
- **UI Shell:** Designed a new viewport container `custom_client/index.html` built around a React/MMO-style component scheme (Action bar, Event log, Floating HUDs).
- **Evennia Connection:** Upgraded connection bridge to hook into `evennia.js` (Evennia's core web library), establishing a raw `/webclientdata` JSON websocket connection on load.
- **Player HUD:** Dynamically tracks Player PL, HP, Ki, and Stamina using data piped from Evennia's `emit_entity_delta`.
- **Scouter HUD:** Triggers dynamically when clicking on targetable NPCs. Shows Target PL, HP, and KI.
- **Action Bar:** Bound HTML inputs and Global Keyboard Hotkeys (`1`-`5`) to issue attack forms (`cmd_attack`, `cmd_charge`) natively bridging the client state -> server command state.
- **Canvas Rendering:** Upgraded `dbforged_canvas_demo.js` into a robust `canvas_manager.js` class that intercepts Evennia `map_data` to render entities correctly, including bounding box click-to-target calculations.

## Scope Not Included
- Phase 4 complex Animations/VFX tied to combat hits (still basic log output).

## Exact Files Touched
- [NEW] `live/web/custom_client/*` (Includes `index.html`, `css/styles.css`, `js/core/app.js`, `js/core/canvas_manager.js`, `js/core/ui_manager.js`, `js/core/evennia_bridge.js`)
- [NEW] `live/web/custom_client/urls.py` & `views.py`
- [MODIFIED] `live/web/urls.py`
- [MODIFIED] `live/commands/commandset.py`
- [MODIFIED] `live/commands/db_commands.py`
- [MODIFIED] `live/world/events.py`

## Testing Performed
- **Manual Launch Test:** Verified Evennia booted correctly over dynamic port `8244/8245`.
- **WebSocket Verification:** Verified the Dev login properly negotiated the `evennia.js` connection without failing back to AJAX Comet polling.
- **UI Render Verification:** Verified Player HUD updates live with player session information.
- **Hitbox Testing:** Verified clicking an NPC model correctly identifies the entity ID and updates Evennia's `caller.db.combat_target`.

## Known Issues / Follow Up Items
- Need to expand the Action Bar mapping beyond just basic numbers (1-5).
- Need to hook in the Event Log filter tabs (System / Combat).
