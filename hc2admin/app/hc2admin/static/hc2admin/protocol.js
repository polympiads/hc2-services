
const DEFAULT_RETRY_TIME = 5000;
const INCREMENT_RETRY_TIME = 5000;
const MAX_RETRY_TIME = 30000;

class ProtocolWebsocket {
    /**
     * Create a Protocol Based Websocket.
     * 
     * @param {String} path 
     */
    constructor (path) {
        this.path = path;

        this.retry_time = DEFAULT_RETRY_TIME;
        this.can_create = true;

        this.create();
    }

    target_url () {
        const protocol = window.location.protocol == "http:" ? "ws://" : "wss://";
        const hostname = window.location.host;
        const pathname = this.path;
        const pathpref = pathname.length == 0 || pathname[0] != '/' ? '/' : '';
    
        return `${protocol}${hostname}${pathpref}${pathname}`
    }
    create () {
        if (this.websocket)
            this.websocket.close();

        this.websocket = new WebSocket( this.target_url() );
        this.websocket.onopen    = (ev) => this.onopen(ev);
        this.websocket.onclose   = (ev) => this.onclose(ev);
        this.websocket.onmessage = (ev) => this.onmessage(ev);
        this.websocket.onerror   = (ev) => this.onerror(ev);
    }

    /**
     * On open handler
     * @param {Event} ev 
     */
    onopen (ev) {
        this.retry_time = DEFAULT_RETRY_TIME;
    }
    /**
     * On close handler
     * @param {Event} ev
     */
    onclose (ev) {
        if (!this.can_create) return ;
        setTimeout(() => {
            this.can_create = true;
            this.create()
        }, this.retry_time);

        this.retry_time = Math.min(this.retry_time + INCREMENT_RETRY_TIME, MAX_RETRY_TIME);
        this.can_create = false;
    }
    /**
     * On error handler
     * @param {Event} ev
     */
    onerror (ev) {
        this.onclose(ev);
    }
    /**
     * On message handler
     * @param {MessageEvent} ev
     */
    onmessage (ev) {
        const payload = JSON.parse(ev.data);
        
        const target = `on_${payload['type']}`
        if (this[target])
            return this[target](payload);

        return this.on_404(payload);
    }

    on_404 (payload) {
        console.log("Could not find appropriate route for payload: ", payload);
    }

    send (payload) {
        this.websocket.send( JSON.stringify(payload) )
    }
};
