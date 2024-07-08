/**@odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart } from "@odoo/owl";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "@odoo-basic-accounting/js/dashboard_item";
import { BarChart } from "@odoo-basic-accounting/js/bar_chart";

class ObaDashboard extends Component {
    static template = "odoo-basic-accounting.ObaDashboard";
    static components = { Layout, DashboardItem, BarChart };

    setup() {
        this.action = useService("action");
        this.statistics = useService("oba.statistics");
        this.display = {
            controlPanel: {},
        };

    onWillStart(async () => {
        this.statistics = await this.statistics.loadStatistics();
        });
    }
}

registry.category("actions").add("oba_dashboard_tag", ObaDashboard);
