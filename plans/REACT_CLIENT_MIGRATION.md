# DBForged React Client Migration Plan

## Overview
Migrate from vanilla JS to React for a modern, maintainable UI.

## Current State
- Vanilla JS with canvas rendering
- WebSocket connection to Evennia
- Glassmorphism CSS design
- 3-column grid layout

## Target Architecture
```
web/
├── client/                    # New React app (Vite)
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── GameCanvas/   # Canvas rendering
│   │   │   ├── Hud/          # Player/target HUD
│   │   │   ├── Chat/         # Chat window
│   │   │   ├── ActionBar/    # Quick actions
│   │   │   ├── Menu/         # Character menu
│   │   │   └── Login/        # Login screen
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useWebSocket.js
│   │   │   └── useGameState.js
│   │   ├── services/         # Evennia API
│   │   │   └── evennia.js
│   │   ├── styles/           # CSS modules
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
```

## Migration Phases

### Phase 1: Foundation
1. Set up Vite + React project
2. Create WebSocket hook
3. Basic connection flow

### Phase 2: Core UI
1. Login screen
2. Chat panel
3. Canvas integration

### Phase 3: Game UI
1. Player HUD
2. Target HUD
3. Action bar

### Phase 4: Features
1. Character menu
2. Inventory
3. Techniques
4. Quests

## Benefits
- Component-based architecture
- State management
- Hot reload during development
- Better dev tools
- Easier testing
