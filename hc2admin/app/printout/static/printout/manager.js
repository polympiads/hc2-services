
function clear_node (node) {
    const childs = []
    for (let child of node.childNodes)
        childs.push(child);
    for (let child of childs)
        node.removeChild(child);
}

class PrintoutWebSocket extends ProtocolWebsocket {
    constructor () {
        super("ws/printout/admin/");
    }

    on_load (payload) {
        maintainer.on_load(payload.user, payload.data)
    }
    on_update (payload) {
        maintainer.on_update( payload.printout, payload.status );
    }
    on_new (payload) {
        maintainer.on_new( payload.printout, payload.status );
    }
}

class PrintoutStatus {
    static get_uuid (status) {
        return {
            "RECEIVED"   : 0,
            "HAS_STAFF"  : 1,
            "DOWNLOAD"   : 2,
            "PRINTED"    : 3,
            "SENT_STAFF" : 4,
            "ARRIVED"    : 5
        }[status]
    }
    static from_uuid (uuid) {
        return [
            "RECEIVED",
            "HAS_STAFF",
            "DOWNLOAD",
            "PRINTED",
            "SENT_STAFF",
            "ARRIVED"
        ][uuid]
    }
    static get_parameters (status) {
        return {
            "RECEIVED"   : [ "text-bg-warning", "Received"   ],
            "HAS_STAFF"  : [ "text-bg-info",    "Has Staff"  ],
            "DOWNLOAD"   : [ "text-bg-info",    "Downloaded" ],
            "PRINTED"    : [ "text-bg-primary", "Printed"    ],
            "SENT_STAFF" : [ "text-bg-primary", "Sent Staff" ],
            "ARRIVED"    : [ "text-bg-success", "Arrived"    ]
        }[status]
    }
}

class ListComponent {
    constructor () {
        this.element = this.render();

        this.parent = undefined;
    }

    set_active (active) {}
    onclick () {
        if (this.parent)
            this.parent.onclick(this);
    }
    should_render () {
        return true;
    }
    render () {
        return undefined;
    }
};

class Category extends ListComponent {
    constructor (title, subtitle, filter) {
        super();

        this.title = title
        this.subtitle = subtitle
        this.filter = filter
        this.element = this.render();
    }

    build_category (infos) {
        const inside_infos = infos.filter( info => info.matches_filter(this.filter) );

        if (inside_infos.length == 0) return [];

        const array = [ this ];
        for (let info of inside_infos) array.push(info);
        
        return array;
    }
    should_render () {
        return true;
    }

    render () {
        const div = document.createElement("div");
        div.innerHTML = `
            <a class="list-group-item no-active py-3 pt-4 mt-5 lh-sm" aria-current="true">
                <div class="w-100">
                    <strong class="mb-1">${this.title}</strong>
                    <span class="px-1 text-secondary">${this.subtitle}</span>
                </div>
            </a>
        `
        const result = div.querySelector("a.list-group-item");
        div.removeChild(result)
        return result;
    }
};

class Printout extends ListComponent {
    constructor (printout, status) {
        super();

        this.update(printout, status);
        this.active = false;

        this.element = this.render();
    }

    matches_filter (filter) {
        return filter(this.printout, this.status)
    }

    update (printout, status) {
        this.printout = printout;
        this.status   = status;
        
        this._should_render = true;
    }

    set_remote_status (status) {
        websocket.send({ "printout": this.printout.id, "status": status })
    }

    update_main () {
        const [ printout, status ] = [ this.printout, this.status ];
        const status_uuid = PrintoutStatus.get_uuid(status);

        for (let btn_id = 0; btn_id <= 5; btn_id ++) {
            const btn = document.querySelector(`#btn-status-${btn_id}`)
            btn.onclick = () => undefined;
            if (btn_id <= status_uuid) btn.className = "btn btn-success";
            if (btn_id != 0 && btn_id == status_uuid) {
                btn.onclick = () => this.set_remote_status(PrintoutStatus.from_uuid(status_uuid - 1));
            }
            if (btn_id == status_uuid + 1) {
                btn.className = "btn btn-primary";
                btn.onclick = () => this.set_remote_status(PrintoutStatus.from_uuid(status_uuid + 1));
            }
            if (btn_id > status_uuid + 1) btn.className = "btn btn-light";
            btn.disabled = btn_id == 0 || !(status_uuid == btn_id || (btn_id - 1) == status_uuid);
        }
        
        const new_src = `/printout/pdf/${printout.id}/`;
        const element = document.querySelector("#embed-pdf")
        
        if (!element.src.endsWith(new_src))
            document.querySelector("#embed-pdf").src = new_src;
    }

    onclick () {
        super.onclick();

        this.update_main();
    }
    set_active (active) {
        if (this.element === undefined) return ;

        this.active = active;

        if (active)
            this.element.classList.add("active");
        else
            this.element.classList.remove("active");
    }

    should_render () {
        return this._should_render;
    }
    render () {
        if (this.printout === undefined) return undefined;

        if (this.active)
            this.update_main();

        this._should_render = false;

        const [status_cls, status_text] = PrintoutStatus.get_parameters(this.status);
        const { id, team, user } = this.printout;
        const { team_id, team_name, team_location } = team;

        const div = document.createElement("div");
        const act_cls = this.active ? " active" : "";

        div.innerHTML = `
            <a class="list-group-item list-group-item-action py-3 lh-sm${act_cls}" aria-current="true">
                <div class="d-flex w-100 align-items-center justify-content-between">
                    <span><strong class="mb-1">Printout #${id}</strong><span class="px-1 text-secondary">${user ? "(" + user + ")" : ""}</span></span>
                    <span class="badge ${status_cls}">${status_text}</span>
                </div>
                <div class="d-flex w-100 align-items-center justify-content-between">
                    <small>${team_name} (Team ${team_id})</small>
                    <small>${team_location}</small>
                </div>
            </a>
        `
        const result = div.querySelector("a.list-group-item");
        div.removeChild(result)
        result.onclick = () => this.onclick();
        return result;
    }
};

class PrintoutMaintainer {
    constructor () {
        this.printouts_dict = {  }
        this.printouts = [];
    }

    onclick (object) {
        for (let printout of this.printouts)
            printout.set_active(printout == object)
    }

    on_load (user, printouts) {
        const my_printouts       = new Category("My Printouts", `(${user})`, (printout, status) => printout.user == user && status != "ARRIVED")
        const pending_printouts  = new Category("Pending Printouts", "", (printout, status) => printout.user == "" && status == "RECEIVED")
        const other_printouts    = new Category("Taken Printouts", "",   (printout, status) => printout.user != "" && printout.user != user && status != "ARRIVED")
        const finished_printouts = new Category("Finished Printouts", "", (printout, status) => status == "ARRIVED" )
    
        this.categories = [
            my_printouts,
            pending_printouts,
            other_printouts,
            finished_printouts
        ]
        for (let category of this.categories)
            category.parent = this;

        this.printouts = []

        for (let [printout, status] of printouts) {
            const { id } = printout

            const object = new Printout(printout, status);
            object.parent = this;

            this.printouts_dict[id] = object
            this.printouts.push(object);
        }

        this.render()
    }

    on_new (printout, status) {
        const { id } = printout;
        
        const object = new Printout(printout, status);
        object.parent = this;
    
        this.printouts_dict[id] = object

        const new_printouts = [ object ];
        for (let printout of this.printouts)
            new_printouts.push(printout);

        this.printouts = new_printouts;
        this.render();
    }
    on_update (printout, status) {
        const { id } = printout;

        const object = this.printouts_dict[id];
        object.update(printout, status);
        
        this.render();
    }
    
    render () {
        const container = document.querySelector("#list-container")
        clear_node(container);

        if (this.categories === undefined) return ;
    
        this.objects = [];
        for (let category of this.categories) {
            const infos = category.build_category(this.printouts)

            for (let info of infos)
                this.objects.push(info);
        }

        let is_first = true;
        for (let object of this.objects) {
            if (object.should_render())
                object.element = object.render();
            
            const el = object.element;
            if (is_first) {
                el.classList.remove("pt-4");
                el.classList.remove("mt-5");

                is_first = false;
            }

            container.appendChild(el);
        }
    }
};

const websocket  = new PrintoutWebSocket();
const maintainer = new PrintoutMaintainer();
