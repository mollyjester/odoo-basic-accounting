/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from  "@odoo/owl";
import { Layout } from "@web/search/layout";

class ObaDashboard extends Component {
    static template = "odoo-basic-accounting.ObaDashboard";
    static components = { Layout };

    setup() {
        this.display = {
            controlPanel: {},
        };
    }
}

registry.category("actions").add("oba_dashboard_tag", ObaDashboard);
