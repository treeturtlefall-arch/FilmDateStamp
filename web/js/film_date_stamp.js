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
        "date_string": "'98 12 24",
        "date_format": "'YY MM DD",
        "show_time": false,
        "font_type": "FDS7_Strict_Compact (80s -7°)",
        "preset_color": "Amber Classic",
        "exposure_intensity": 1.00,
        "core_glow": 1.00,
        "halation": 1.00,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin": 1.15,
    },
    "Japanese Snap (Disposable)": {
        "date_string": "'98 12 24 18:30",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
        "preset_color": "Fuji Orange",
        "exposure_intensity": 1.00,
        "core_glow": 0.50,
        "halation": 1.00,
        "position": "bottom_right",
        "font_scale": 1.20,
        "margin": 1.50,
    },
    "American West Coast": {
        "date_string": "12 24 '98",
        "date_format": "MM DD 'YY",
        "show_time": false,
        "font_type": "FDS7_Strict_Compact (80s -7°)",
        "preset_color": "Golden Yellow",
        "exposure_intensity": 1.00,
        "core_glow": 0.85,
        "halation": 1.00,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin": 1.15,
    },
    "American 80s (Red Quartz)": {
        "date_string": "12 24 '88",
        "date_format": "MM DD 'YY",
        "show_time": false,
        "font_type": "FDS7_Strict_SLR (80s 0°)",
        "preset_color": "Quartz Red",
        "exposure_intensity": 1.10,
        "core_glow": 1.00,
        "halation": 1.30,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin": 1.15,
    },
    "European Classic (Paris/Berlin)": {
        "date_string": "24.12.98",
        "date_format": "DD.MM.YY",
        "show_time": false,
        "font_type": "FDS7_Strict_SLR (80s 0°)",
        "preset_color": "Amber Classic",
        "exposure_intensity": 0.90,
        "core_glow": 0.70,
        "halation": 0.80,
        "position": "bottom_right",
        "font_scale": 0.95,
        "margin": 1.15,
    },
    "Y2K Digicam (Early 2000s)": {
        "date_string": "'03 08 15 14:20",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "ShareTechMono (LCD Digital)",
        "preset_color": "Golden Yellow",
        "exposure_intensity": 1.05,
        "core_glow": 0.60,
        "halation": 0.90,
        "position": "bottom_right",
        "font_scale": 1.15,
        "margin": 1.40,
    },
    "Compact Fine Dot (Minimal)": {
        "date_string": "'99 07 20 16:45",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
        "preset_color": "Fuji Orange",
        "exposure_intensity": 1.00,
        "core_glow": 0.40,
        "halation": 0.90,
        "position": "bottom_right",
        "font_scale": 1.10,
        "margin": 1.50,
    },
    "Monochrome 70s (Canodate E)": {
        "date_string": "74 12 25",
        "date_format": "YY MM DD",
        "show_time": false,
        "font_type": "FDS_Mechanical_70s (70s Mechanical)",
        "preset_color": "Paper White (Monochrome)",
        "exposure_intensity": 1.00,
        "core_glow": 0.50,
        "halation": 0.60,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin": 1.15,
    },
    "Vintage 70s Color (Datematic)": {
        "date_string": "'74 12 25",
        "date_format": "'YY MM DD",
        "show_time": false,
        "font_type": "FDS_Mechanical_70s (70s Mechanical)",
        "preset_color": "Bulb Warm Ivory",
        "exposure_intensity": 1.05,
        "core_glow": 0.70,
        "halation": 0.85,
        "position": "bottom_right",
        "font_scale": 1.00,
        "margin": 1.15,
    },
    // 空想・シミュレーティブ（Fiction / Speculative）プリセット
    "Cyber Telemetry (80s Sci-Fi)": {
        "date_string": "'98 12 24 23:59:59",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "Michroma (Cyber Telemetry)",
        "preset_color": "Cyber Green",
        "exposure_intensity": 1.35,
        "core_glow": 1.20,
        "halation": 1.45,
        "position": "bottom_right",
        "font_scale": 1.05,
        "margin": 0.90,
    },
    "Y2K Pop (Heisei Fancy)": {
        "date_string": "'98 12 24 18:30",
        "date_format": "'YY MM DD",
        "show_time": true,
        "font_type": "MochiyPopOne (Y2K Pop)",
        "preset_color": "Neo Pink",
        "exposure_intensity": 1.05,
        "core_glow": 0.50,
        "halation": 0.75,
        "position": "bottom_right",
        "font_scale": 1.15,
        "margin": 0.90,
    },
    "Arcane Occult (Crimson Script)": {
        "date_string": "'98 12 24",
        "date_format": "'YY MM DD",
        "show_time": false,
        "font_type": "EagleLake (Arcane Script)",
        "preset_color": "Crimson Red",
        "exposure_intensity": 1.05,
        "core_glow": 0.40,
        "halation": 0.60,
        "position": "bottom_right",
        "font_scale": 1.50,
        "margin": 0.85,
    },
};

const TARGET_KEYS = [
    "date_string",
    "date_format",
    "show_time",
    "font_type",
    "preset_color",
    "exposure_intensity",
    "core_glow",
    "halation",
    "position",
    "font_scale",
    "margin"
];

function setupFilmDateStamp(node) {
    if (!node || !node.widgets) return;

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
            nodeType.prototype.onConfigure = function () {
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
});
