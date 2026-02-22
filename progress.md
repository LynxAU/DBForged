Original prompt: also most of Hair style: Enter a hair style (e.g. spiky, short, ponytail): [current: spiky] @event {...} this belongs in the player panel.. all we really need is health and Ki and Powerlevel for our hud

2026-02-22: Patched webclient event handling to parse embedded @event payloads, suppress them from the text stream, and preserve any prompt text before the payload.
2026-02-22: Added a left-side player panel (identity/appearance/room/sprite) fed by entity_delta/player_frame packets.
2026-02-22: Kept scouter HUD stats-only (HP, Ki, PL) while allowing updates from both player_frame and entity_delta packets.
TODO: Verify in browser against live server that mixed prompt+@event lines render prompt text without raw JSON leakage.
TODO: Confirm player panel placement does not overlap existing overlays on small screens.
2026-02-22: Fixed OOC/IC command boundary by removing DB menu commands from CharacterCmdSet and locking them with cmd:is_ooc() so 1/2/3/4/menu/exit do not trigger while puppeted.
2026-02-22: Disabled automatic in-character chargen on puppet; IC chargen command interception now requires explicit db.chargen_active, preventing normal gameplay commands from being consumed as hair/eye/aura prompts.
2026-02-22: Reworked Account post-login menu to spec-oriented numeric flow with race-aware skin palettes, create wizard back/cancel-confirm/review handling, exact zero-char enter/delete messages, and delete exact-name confirmation retry behavior. Added tests and README notes.
