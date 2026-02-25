// Wrapper for Evennia's native websocket client
// We rely on evennia_websocket_webclient.js being loaded in index.html

let evenniaLink = null;
let evEmitter = null;
let isConnected = false;

export function connectToEvennia(callbacks) {
    if (isConnected) return;

    // The Evennia client attaches itself to window.Evennia
    // It automatically reads `window.ev_opts` we defined in index.html

    // We need to wait for Evennia to initialize
    const checkInterval = setInterval(() => {
        if (window.Evennia && window.Evennia.emitter) {
            clearInterval(checkInterval);
            evEmitter = window.Evennia.emitter;
            bindEvents(callbacks);

            // Initialize the connection (Evennia ignores this if already init)
            window.Evennia.init();

            // If the native script already established the socket before we bound the callback,
            // we should manually trigger it now.
            if (window.Evennia.isConnected && window.Evennia.isConnected()) {
                isConnected = true;
                if (callbacks.onOpen) callbacks.onOpen();
            }
        }
    }, 100);
}

function bindEvents(callbacks) {
    // Standard connection events
    evEmitter.on('connection_open', () => {
        isConnected = true;
        if (callbacks.onOpen) callbacks.onOpen();
    });

    evEmitter.on('connection_close', () => {
        isConnected = false;
        if (callbacks.onClose) callbacks.onClose();
    });

    evEmitter.on('connection_error', (error) => {
        if (callbacks.onError) callbacks.onError(error);
    });

    // Message routing
    evEmitter.on('text', (args, kwargs) => {
        if (callbacks.onMessage) callbacks.onMessage('text', args);
    });

    // Our custom JSON payloads.
    // Evennia sends OOB data in kwargs (args is always []).
    // We must use kwargs when args is empty, because [] is truthy in JS.
    evEmitter.on('dbforged_event', (args, kwargs) => {
        const data = (args && args.length > 0) ? args : kwargs;
        if (callbacks.onMessage) callbacks.onMessage('dbforged_event', data);
    });
}

// Send standard MUD text commands upstream
// Evennia parses these like they came from Telnet
export function sendInteractiveCommand(cmdString) {
    if (!isConnected || !window.Evennia) {
        console.warn("Attempted to send command while disconnected:", cmdString);
        return;
    }

    // "text" is the default protocol input type
    // args: [command_string], kwargs: {}
    window.Evennia.msg('text', [cmdString], {});
}

// Example: Send a structured JSON command upstream (Phase 3)
export function sendJsonCommand(cmdObj) {
    if (!isConnected || !window.Evennia) return;
    window.Evennia.msg('dbforged_cmd', [cmdObj], {});
}
