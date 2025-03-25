/**
 * This code is the draft for the javascript of the manager.
 */
let active_printout = -1;

const printout_parameters = {};

const btn_ids = [0, 1, 2, 3, 4, 5];
let all_printouts = [];

function create_websocket () {
    const protocol = window.location.protocol == "http:" ? "ws://" : "wss://";
    const hostname = window.location.host;
    const pathname = "/ws/printout/admin/"

    const websocket = `${protocol}${hostname}${pathname}`
    
    const ws = new WebSocket(websocket);
    ws.onmessage = (ev) => {
        const data = JSON.parse(ev.data)
        
        if (data.type == "update") update_component( data.printout, data.status );
        if (data.type == "new") new_component( data.printout, data.status )
        if (data.type == "load") {
            create_categories( data.user )
            build_all(categories, data.data);
        }
    }
    return ws;
}

const ws = create_websocket();

function set_printout_status (new_status) {
    if (active_printout == -1) return ;
    
    ws.send(JSON.stringify({ "printout": active_printout, "status": new_status }))
}

function update_active_printout () {
    if (active_printout == -1) {
        for (let btn_id of btn_ids) {
            const btn = document.querySelector(`#btn-status-${btn_id}`)
            btn.className = "btn btn-light"
            btn.disabled  = true;
            btn.onclick = () => undefined;
        }

        document.querySelector("#embed-pdf").src = "";
    } else {
        const [ printout, status ] = printout_parameters[active_printout];
        const status_uuid = get_status_uuid(status);

        for (let btn_id of btn_ids) {
            const btn = document.querySelector(`#btn-status-${btn_id}`)
            btn.onclick = () => undefined;
            if (btn_id <= status_uuid) btn.className = "btn btn-success";
            if (btn_id != 0 && btn_id == status_uuid) {
                btn.onclick = () => set_printout_status(get_status_from_uuid(status_uuid - 1));
            }
            if (btn_id == status_uuid + 1) {
                btn.className = "btn btn-primary";
                btn.onclick = () => set_printout_status(get_status_from_uuid(status_uuid + 1));
            }
            if (btn_id > status_uuid + 1) btn.className = "btn btn-light";
            btn.disabled = btn_id == 0 || !(status_uuid == btn_id || (btn_id - 1) == status_uuid);
        }
        
        const new_src = `/printout/pdf/${printout.id}/`;
        const element = document.querySelector("#embed-pdf")
        
        if (!element.src.endsWith(new_src))
            document.querySelector("#embed-pdf").src = new_src;
    }
}

function register_printout (printout, status) {
    const id = printout.id;
    printout_parameters[id] = [ printout, status ];

    if (id == active_printout)
        update_active_printout();
}

function set_visual_active_printout (printout_id) {
    if (active_printout != -1) {
        document.querySelector(`#list-printout-${active_printout}`)
            .classList.remove("active");
    }
    active_printout = printout_id;
    if (printout_id != -1) {
        document.querySelector(`#list-printout-${active_printout}`)
            .classList.add("active");
    }
}

function set_active_printout (printout_id) {
    set_visual_active_printout(printout_id)

    update_active_printout();
}
function get_status_uuid (status) {
    return {
        "RECEIVED"   : 0,
        "HAS_STAFF"  : 1,
        "DOWNLOAD"   : 2,
        "PRINTED"    : 3,
        "SENT_STAFF" : 4,
        "ARRIVED"    : 5
    }[status]
}
function get_status_from_uuid (uuid) {
    return [
        "RECEIVED",
        "HAS_STAFF",
        "DOWNLOAD",
        "PRINTED",
        "SENT_STAFF",
        "ARRIVED"
    ][uuid]
}
function get_status_parameters (status) {
    return {
        "RECEIVED"   : [ "text-bg-warning", "Received"   ],
        "HAS_STAFF"  : [ "text-bg-info",    "Has Staff"  ],
        "DOWNLOAD"   : [ "text-bg-info",    "Downloaded" ],
        "PRINTED"    : [ "text-bg-primary", "Printed"    ],
        "SENT_STAFF" : [ "text-bg-primary", "Sent Staff" ],
        "ARRIVED"    : [ "text-bg-success", "Arrived"    ]
    }[status]
}

function build_category_header (title, subtitle) {
    const div = document.createElement("div");
    div.innerHTML = `
        <a class="list-group-item no-active py-3 pt-4 mt-5 lh-sm" aria-current="true">
            <div class="w-100">
                <strong class="mb-1">${title}</strong>
                <span class="px-1 text-secondary">${subtitle}</span>
            </div>
        </a>
    `
    const result = div.querySelector("a.list-group-item");
    div.removeChild(result)
    return result;
}
function _build_component (printout, status) {
    register_printout(printout, status);
    const [status_cls, status_text] = get_status_parameters(status);
    const { id, team, user } = printout;
    const { team_id, team_name, team_location } = team;
    console.log(printout, status)
    const obj_id = `list-printout-${id}`;

    const div = document.createElement("div");
    div.innerHTML = `
        <a id="${obj_id}" href="#" class="list-group-item list-group-item-action py-3 lh-sm" aria-current="true">
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
    result.onclick = () => set_active_printout(id);
    return result;
}
function build_component (printout, status) {
    const { id, team, user } = printout;
    const obj_id = `list-printout-${id}`;
    const cached = document.querySelector(`#${obj_id}`)
    if (cached)
        return cached;

    return _build_component(printout, status);
}
function update_component (printout, status) {
    register_printout(printout, status);
    for (let idx = 0; idx < all_printouts.length; idx ++) {
        if (all_printouts[idx][0].id == printout.id) {
            all_printouts[idx] = [ printout, status ];
        }
    }

    const { id, team, user } = printout;
    const obj_id = `list-printout-${id}`;
    const cached = document.querySelector(`#${obj_id}`)
    if (cached) {
        const new_c = _build_component(printout, status)
        cached.parentNode.replaceChild(
            new_c,
            cached
        );
    }

    build_all(categories, all_printouts);

    set_visual_active_printout(active_printout)
    if (printout.id == active_printout)
        update_active_printout();
}
function new_component (printout, status) {
    let new_printouts = [ [printout, status] ];
    for (let printout of all_printouts)
        new_printouts.push(printout);
    all_printouts = new_printouts;
    build_all(categories, new_printouts);
}

function clear_node (node) {
    const childs = []
    for (let child of node.childNodes)
        childs.push(child);
    for (let child of childs)
        node.removeChild(child);
}
function put_components (components) {
    const build_component = document.querySelector("#list-container")
    clear_node(build_component);

    for (let component of components)
        build_component.appendChild(component)
}

function build_category (category, parameters) {
    const header = build_category_header(category.title, category.subtitle);

    const array = [ header ]
    for (let [ printout, status ] of parameters)
        array.push( build_component( printout, status ) );
    
    return array;
}

class Category {
    constructor (title, subtitle, filter) {
        this.title = title
        this.subtitle = subtitle
        this.filter = filter
    }

    build (components) {
        const comp = components.filter((value, index) => {
            const [ printout, status ] = value;

            return this.filter( printout, status );
        })
        if (comp.length == 0) return [];

        return build_category( this, comp )
    }
};

function build_all (categories, infos) {
    console.log(infos)
    all_printouts = infos;
    for (let info of infos)
        register_printout(info[0], info[1]);

    const result = [];
    for (let category of categories) {
        for (let value of category.build(infos)) {
            result.push(value);
        }
    }
    if (result.length != 0) {
        result[0].classList.remove("pt-4");
        result[0].classList.remove("mt-5");
    }

    put_components(result);
}
function create_categories (user) {
    const my_printouts       = new Category("My Printouts", `(${user})`, (printout, status) => printout.user == user && status != "ARRIVED")
    const pending_printouts  = new Category("Pending Printouts", "", (printout, status) => printout.user == "" && status == "RECEIVED")
    const other_printouts    = new Category("Taken Printouts", "",   (printout, status) => printout.user != "" && printout.user != user && status != "ARRIVED")
    const finished_printouts = new Category("Finished Printouts", "", (printout, status) => status == "ARRIVED" )

    categories.push(    
        my_printouts,
        pending_printouts,
        other_printouts,
        finished_printouts
    )
}

const categories = [];
build_all(categories, []);
