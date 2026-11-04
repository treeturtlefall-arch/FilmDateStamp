import { app } from "../../../scripts/app.js";

const DEBUG = false;
const log = (...args) => {
    if (DEBUG) console.log("[FilmDateStamp]", ...args);
};

/**
 * FilmDateStamp スタイルプリセット定義
 * film_config.py と同期
 */
const STYLE_PRESETS = {
    "Japanese Tokyo 90s": {
        "date_mode": "custom",
        "date_string": "'98 12 24",
        "date_format": "'YY MM DD",
        "show_time": false,
        "font_type": "FDS7_Strict_Compact (80s -7°)",
        "preset_color": "Amber Classic",
        "exposure_intensity": 1.00,
        "core_glow": 1.00,
        "halation": 1.00,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "Japanese Snap (Disposable)": {
        "date_mode": "custom",
        "date_string": "'98 12 24 18:30",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
        "preset_color": "Fuji Orange",
        "exposure_intensity": 1.00,
        "core_glow": 0.50,
        "halation": 1.00,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.20,
        "margin_x": 1.50,
        "margin_y": 1.50,
    },
    "American West Coast": {
        "date_mode": "custom",
        "date_string": "12 24 '98",
        "date_format": "MM DD 'YY",
        "show_time": false,
        "font_type": "FDS7_Strict_Compact (80s -7°)",
        "preset_color": "Golden Yellow",
        "exposure_intensity": 1.00,
        "core_glow": 0.85,
        "halation": 1.00,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "American 80s (Red Quartz)": {
        "date_mode": "custom",
        "date_string": "12 24 '88",
        "date_format": "MM DD 'YY",
        "show_time": false,
        "font_type": "FDS7_Strict_SLR (80s 0°)",
        "preset_color": "Quartz Red",
        "exposure_intensity": 1.10,
        "core_glow": 1.00,
        "halation": 1.30,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "European Classic (Paris/Berlin)": {
        "date_mode": "custom",
        "date_string": "24.12.98",
        "date_format": "DD.MM.YY",
        "show_time": false,
        "font_type": "FDS7_Strict_SLR (80s 0°)",
        "preset_color": "Amber Classic",
        "exposure_intensity": 0.90,
        "core_glow": 0.70,
        "halation": 0.80,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 0.95,
        "margin_x": 1.10,
        "margin_y": 1.10,
    },
    "Hong Kong Neon (90s Cinema)": {
        "date_mode": "custom",
        "date_string": "'94 05 01",
        "date_format": "'YY MM DD",
        "show_time": false,
        "font_type": "DSEG14_Italic (14-Segment)",
        "preset_color": "Cyber Green",
        "exposure_intensity": 1.20,
        "core_glow": 1.10,
        "halation": 1.60,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.05,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "Y2K Digicam (Early 2000s)": {
        "date_mode": "custom",
        "date_string": "'03 08 15 14:20",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "ShareTechMono (LCD Digital)",
        "preset_color": "Golden Yellow",
        "exposure_intensity": 1.05,
        "core_glow": 0.60,
        "halation": 0.90,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.15,
        "margin_x": 1.40,
        "margin_y": 1.40,
    },
    "Compact Fine Dot (Minimal)": {
        "date_mode": "custom",
        "date_string": "'99 07 20 16:45",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "Silkscreen (Fine Dot)",
        "preset_color": "Fuji Orange",
        "exposure_intensity": 1.00,
        "core_glow": 0.40,
        "halation": 0.90,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.10,
        "margin_x": 1.50,
        "margin_y": 1.50,
    },
    "Monochrome 70s (Canodate E)": {
        "date_mode": "custom",
        "date_string": "74 12 25",
        "date_format": "YY MM DD",
        "show_time": false,
        "font_type": "FDS_Mechanical_70s (70s Mechanical)",
        "preset_color": "Paper White (Monochrome)",
        "exposure_intensity": 1.00,
        "core_glow": 0.50,
        "halation": 0.60,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
    "Vintage 70s Color (Datematic)": {
        "date_mode": "custom",
        "date_string": "'74 12 25",
        "date_format": "'YY MM DD",
        "show_time": false,
        "font_type": "FDS_Mechanical_70s (70s Mechanical)",
        "preset_color": "Bulb Warm Ivory",
        "exposure_intensity": 1.05,
        "core_glow": 0.70,
        "halation": 0.85,
        "optical_burn": true,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin_x": 1.00,
        "margin_y": 1.00,
    },
};

const TARGET_KEYS = [
    "date_mode",
    "date_string",
    "date_format",
    "show_time",
    "font_type",
    "preset_color",
    "exposure_intensity",
    "core_glow",
    "halation",
    "optical_burn",
    "position",
    "font_scale",
    "margin_x",
    "margin_y"
];

function repairShiftedWidgets(node) {
    if (!node || !node.widgets) return;

    const showTimeWidget = node.widgets.find(w => w.name === "show_time");
    const posWidget = node.widgets.find(w => w.name === "position");
    const fontScaleWidget = node.widgets.find(w => w.name === "font_scale");
    const marginXWidget = node.widgets.find(w => w.name === "margin_x");
    const marginYWidget = node.widgets.find(w => w.name === "margin_y");
    const seedWidget = node.widgets.find(w => w.name === "seed");

    if (!showTimeWidget || !posWidget || !fontScaleWidget || !marginXWidget || !marginYWidget) {
        return;
    }

    const validPositions = ["bottom_right", "bottom_left", "top_right", "top_left"];

    // ズレの検出条件:
    // 1. show_time に "bottom_right" 等の位置文字列が入っている
    // 2. または position に数値（font_scale の値）が入っている
    // 3. または margin_y に 3.0 超の値（seed の値）が入っている
    const isShifted = 
        (typeof showTimeWidget.value === "string" && validPositions.includes(showTimeWidget.value)) ||
        (typeof posWidget.value === "number") ||
        (typeof marginYWidget.value === "number" && marginYWidget.value > 3.0);

    if (isShifted) {
        console.warn("[FilmDateStamp] Detected shifted widgets on node", node.id, "- Executing auto-repair migration...");

        const shiftedPos = showTimeWidget.value;
        const shiftedFontScale = posWidget.value;
        const shiftedMarginX = fontScaleWidget.value;
        const shiftedMarginY = marginXWidget.value;
        const shiftedSeed = marginYWidget.value;

        // 正しい位置へ再配置
        showTimeWidget.value = false;
        posWidget.value = (typeof shiftedPos === "string" && validPositions.includes(shiftedPos)) ? shiftedPos : "bottom_right";
        fontScaleWidget.value = (typeof shiftedFontScale === "number" && shiftedFontScale >= 0.5 && shiftedFontScale <= 2.5) ? shiftedFontScale : 1.0;
        marginXWidget.value = (typeof shiftedMarginX === "number" && shiftedMarginX >= 0.0 && shiftedMarginX <= 3.0) ? shiftedMarginX : 1.0;
        marginYWidget.value = (typeof shiftedMarginY === "number" && shiftedMarginY >= 0.0 && shiftedMarginY <= 3.0) ? shiftedMarginY : 1.0;
        if (seedWidget) {
            seedWidget.value = (typeof shiftedSeed === "number") ? shiftedSeed : 0;
        }

        log("Auto-repair completed successfully for node", node.id);
        node.setDirtyCanvas(true, true);
    }
}

function setupFilmDateStamp(node) {
    if (!node || !node.widgets) return;

    // ズレ修復を最優先で実行
    repairShiftedWidgets(node);

    if (node._filmDateStampHooked) return;
    node._filmDateStampHooked = true;

    log("Setting up preset sync for node:", node.id);

    const stylePresetWidget = node.widgets.find(w => w.name === "style_preset");
    if (!stylePresetWidget) return;

    let isApplying = false;

    // 1. スタイルプリセット変更時: 各パラメータウィジェットへ値を自動反映
    const origPresetCb = stylePresetWidget.callback;
    stylePresetWidget.callback = function (value) {
        const res = origPresetCb ? origPresetCb.apply(this, arguments) : undefined;
        const selected = value !== undefined ? value : stylePresetWidget.value;

        if (selected && selected !== "Custom" && STYLE_PRESETS[selected]) {
            isApplying = true;
            const preset = STYLE_PRESETS[selected];
            log("Applying preset:", selected, preset);

            for (const key of TARGET_KEYS) {
                if (key in preset) {
                    const w = node.widgets.find(item => item.name === key);
                    if (w) {
                        w.value = preset[key];
                        if (w.callback) {
                            try {
                                w.callback(preset[key]);
                            } catch (e) {
                                console.error("[FilmDateStamp] Error in widget callback:", key, e);
                            }
                        }
                    }
                }
            }
            isApplying = false;
            node.setDirtyCanvas(true, true);
            if (app.graph) {
                app.graph.setDirtyCanvas(true, true);
            }
        }
        return res;
    };

    // 2. 個別パラメータ変更時: プリセットを自動で "Custom" に切り替え
    for (const key of TARGET_KEYS) {
        const w = node.widgets.find(item => item.name === key);
        if (w) {
            const origCb = w.callback;
            w.callback = function (val) {
                const res = origCb ? origCb.apply(this, arguments) : undefined;
                if (!isApplying && stylePresetWidget.value !== "Custom") {
                    log("Param changed:", key, "-> Switching to Custom");
                    stylePresetWidget.value = "Custom";
                    node.setDirtyCanvas(true, true);
                    if (app.graph) {
                        app.graph.setDirtyCanvas(true, true);
                    }
                }
                return res;
            };
        }
    }
}

app.registerExtension({
    name: "FilmDateStamp.PresetSync",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData?.name === "FilmDateStamp") {
            const origOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = origOnNodeCreated ? origOnNodeCreated.apply(this, arguments) : undefined;
                setupFilmDateStamp(this);
                return r;
            };

            const origOnConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function (info) {
                if (info && Array.isArray(info.widgets_values)) {
                    const validPositions = ["bottom_right", "bottom_left", "top_right", "top_left"];
                    // 旧フォーマット (15要素またはインデックス10がposition文字列)
                    if (typeof info.widgets_values[10] === "string" && validPositions.includes(info.widgets_values[10])) {
                        log("Pre-migration: inserting show_time=false at index 10 of widgets_values");
                        info.widgets_values.splice(10, 0, false);
                    }
                }
                const r = origOnConfigure ? origOnConfigure.apply(this, arguments) : undefined;
                setupFilmDateStamp(this);
                return r;
            };
        }
    },

    nodeCreated(node) {
        if (node.comfyClass === "FilmDateStamp") {
            setupFilmDateStamp(node);
        }
    },

    loadedGraphNode(node) {
        if (node.comfyClass === "FilmDateStamp") {
            setupFilmDateStamp(node);
        }
    },

    afterConfigureGraph() {
        if (app.graph && app.graph._nodes) {
            for (const node of app.graph._nodes) {
                if (node.comfyClass === "FilmDateStamp") {
                    setupFilmDateStamp(node);
                }
            }
        }
    }
});
