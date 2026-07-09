/** @odoo-module **/

import { SearchPanel } from "@web/search/search_panel/search_panel";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";

const PANEL_SELECTOR = ".o_search_panel";
const PERIOD_CLASS = "ar_caisse_period_filter";
const MODEL_NAME = "ar.sortie.caisse.mouvement";
const FILTER_PREFIX = "Période caisse";

function getSearchModel(component) {
    return component.env.searchModel || component.props.searchModel;
}

function getSearchItems(searchModel) {
    const items = searchModel.searchItems;
    if (!items) {
        return [];
    }
    if (items instanceof Map) {
        return [...items.values()];
    }
    return Object.values(items);
}

function removePreviousPeriodFilter(searchModel) {
    if (!searchModel.deleteSearchItems) {
        return;
    }
    const filterIds = getSearchItems(searchModel)
        .filter((item) => item.description && item.description.startsWith(FILTER_PREFIX))
        .map((item) => item.id)
        .filter(Boolean);
    if (filterIds.length) {
        searchModel.deleteSearchItems(filterIds);
    }
}

function buildPeriodDomain(dateFrom, dateTo) {
    const domain = [];
    if (dateFrom) {
        domain.push(["date_mouvement", ">=", `${dateFrom} 00:00:00`]);
    }
    if (dateTo) {
        domain.push(["date_mouvement", "<=", `${dateTo} 23:59:59`]);
    }
    return domain;
}

function buildPeriodDescription(dateFrom, dateTo) {
    if (dateFrom && dateTo) {
        return `${FILTER_PREFIX}: ${dateFrom} -> ${dateTo}`;
    }
    if (dateFrom) {
        return `${FILTER_PREFIX}: depuis ${dateFrom}`;
    }
    return `${FILTER_PREFIX}: jusqu'au ${dateTo}`;
}

function applyPeriodFilter(searchModel, dateFrom, dateTo) {
    removePreviousPeriodFilter(searchModel);
    if (!dateFrom && !dateTo) {
        return;
    }
    if (!searchModel.createNewFilters) {
        return;
    }
    searchModel.createNewFilters([{
        description: buildPeriodDescription(dateFrom, dateTo),
        domain: buildPeriodDomain(dateFrom, dateTo),
        type: "filter",
    }]);
}

function renderPeriodPanel(component) {
    const searchModel = getSearchModel(component);
    const isCaisseHistory = searchModel && (
        searchModel.resModel === MODEL_NAME
        || searchModel.context?.ar_caisse_period_panel
    );
    if (!isCaisseHistory) {
        return;
    }

    const panel = document.querySelector(PANEL_SELECTOR);
    if (!panel || panel.querySelector(`.${PERIOD_CLASS}`)) {
        return;
    }

    const section = document.createElement("section");
    section.className = `o_search_panel_section ${PERIOD_CLASS}`;
    section.innerHTML = `
        <header class="o_search_panel_section_header ar_caisse_period_header">
            <i class="fa fa-calendar-o" aria-hidden="true"></i>
            <span>Période</span>
        </header>
        <div class="ar_caisse_period_body">
            <label>
                <span>De</span>
                <input class="ar_caisse_period_from" type="date"/>
            </label>
            <label>
                <span>A</span>
                <input class="ar_caisse_period_to" type="date"/>
            </label>
            <div class="ar_caisse_period_actions">
                <button class="btn btn-primary btn-sm ar_caisse_period_apply" type="button">Appliquer</button>
                <button class="btn btn-secondary btn-sm ar_caisse_period_clear" type="button">Effacer</button>
            </div>
        </div>
    `;

    const inputFrom = section.querySelector(".ar_caisse_period_from");
    const inputTo = section.querySelector(".ar_caisse_period_to");
    section.querySelector(".ar_caisse_period_apply").addEventListener("click", () => {
        applyPeriodFilter(searchModel, inputFrom.value, inputTo.value);
    });
    section.querySelector(".ar_caisse_period_clear").addEventListener("click", () => {
        inputFrom.value = "";
        inputTo.value = "";
        removePreviousPeriodFilter(searchModel);
    });
    section.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            applyPeriodFilter(searchModel, inputFrom.value, inputTo.value);
        }
    });

    panel.prepend(section);
}

patch(SearchPanel.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => renderPeriodPanel(this));
        onPatched(() => renderPeriodPanel(this));
    },
});
