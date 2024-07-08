/** @odoo-module */

import { registry } from "@web/core/registry";
import { memoize } from "@web/core/utils/functions";

const statisticsService = {
    dependencies: ["rpc"],
    async: ["loadStatistics"],
    start(env, { rpc }) {
        return {
            loadStatistics: memoize(() => rpc("/oba/statistics")),
        };
    },
};

registry.category("services").add("oba.statistics", statisticsService);