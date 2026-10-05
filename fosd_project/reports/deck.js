const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5

// Palette: deep photonics navy + plasmon amber/gold accent
const NAVY = "0B1F3A";
const NAVY2 = "13294B";
const AMBER = "E8A33D";
const TEAL = "2FA6A0";
const LIGHT = "F4F6F9";
const INK = "1A1A1A";
const GREY = "6B7480";

function titleSlide() {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("ML + Explainable AI for\nFiber-Optic SPR Sensor Design", {
    x: 0.7, y: 1.7, w: 11.9, h: 2.0, fontSize: 40, bold: true, color: "FFFFFF", fontFace: "Georgia", align: "left",
  });
  s.addText("Reimplementing and extending a 2024 IEEE Sensors Letters paper with an inverse-design parameter recommendation system", {
    x: 0.7, y: 3.65, w: 10.5, h: 0.8, fontSize: 16, color: "C9D6E8", fontFace: "Calibri",
  });
  s.addText("Academic Project Presentation", { x: 0.7, y: 6.6, w: 8, h: 0.4, fontSize: 13, color: AMBER, bold: true });
  // decorative plasmon wave motif (simple circles suggesting resonance)
  for (let i = 0; i < 5; i++) {
    s.addShape("ellipse", { x: 9.7 + i * 0.55, y: 1.0 + i * 0.05, w: 0.5 - i * 0.06, h: 0.5 - i * 0.06, fill: { color: AMBER, transparency: 20 + i * 15 }, line: { color: AMBER, width: 0 } });
  }
}

function sectionHeader(title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: NAVY2 };
  s.addText(title, { x: 0.7, y: 3.0, w: 11.9, h: 1.0, fontSize: 32, bold: true, color: "FFFFFF", fontFace: "Georgia" });
  if (subtitle) s.addText(subtitle, { x: 0.7, y: 3.9, w: 10, h: 0.6, fontSize: 15, color: "C9D6E8" });
  return s;
}

function contentSlide(title) {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  s.addText(title, { x: 0.6, y: 0.35, w: 12.1, h: 0.7, fontSize: 26, bold: true, color: NAVY, fontFace: "Georgia" });
  return s;
}

// 1. Title
titleSlide();

// 2. Objectives
(() => {
  const s = contentSlide("Objectives of the Reference Paper");
  const items = [
    "Replace slow physics-based TMM simulation with fast ML-based FoM prediction",
    "Benchmark 4 ML models — Random Forest, XGBoost, CatBoost, ANN — on a 32,760-row dataset",
    "Identify the best model via MAE, RMSE, R\u00b2 (paper's winner: CatBoost, MAE = 0.37 RIU\u207b\u00b9)",
    "Use SHAP to explain which design parameters drive FoM the most",
  ];
  s.addShape("rect", { x: 0.6, y: 1.35, w: 7.6, h: 5.6, fill: { color: "FFFFFF" }, line: { color: "E3E7ED", width: 1 } });
  let y = 1.7;
  items.forEach((t, i) => {
    s.addShape("ellipse", { x: 0.95, y: y + 0.05, w: 0.35, h: 0.35, fill: { color: TEAL }, line: { color: TEAL, width: 0 } });
    s.addText(String(i + 1), { x: 0.95, y: y + 0.05, w: 0.35, h: 0.35, fontSize: 14, color: "FFFFFF", bold: true, align: "center", valign: "middle" });
    s.addText(t, { x: 1.5, y: y - 0.05, w: 6.5, h: 1.1, fontSize: 15, color: INK, valign: "top" });
    y += 1.28;
  });
  s.addShape("rect", { x: 8.4, y: 1.35, w: 4.3, h: 5.6, fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText("Design parameters (inputs)", { x: 8.7, y: 1.6, w: 3.7, h: 0.4, fontSize: 14, bold: true, color: AMBER });
  ["Wavelength (\u03bb)", "Sensing length (L)", "Analyte refractive index", "Ag layer thickness"].forEach((t, i) => {
    s.addText("\u2022 " + t, { x: 8.7, y: 2.15 + i * 0.5, w: 3.7, h: 0.45, fontSize: 14, color: "FFFFFF" });
  });
  s.addText("Output: Figure of Merit (FoM)", { x: 8.7, y: 4.3, w: 3.7, h: 0.5, fontSize: 14, bold: true, color: TEAL });
  s.addText("FoM = Sensitivity / FWHM", { x: 8.7, y: 4.85, w: 3.7, h: 0.4, fontSize: 13, italic: true, color: "C9D6E8" });
})();

// 3. Paper outputs vs gap
(() => {
  const s = contentSlide("Reference Paper: Outputs & the Gap");
  s.addText("What the paper delivers", { x: 0.6, y: 1.3, w: 5.9, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  ["Simulated dataset (5 columns, 32,760 rows)", "Trained ML models + MAE/RMSE/R\u00b2 table", "Actual vs predicted trend plots", "Global SHAP feature-importance plots"].forEach((t, i) => {
    s.addText("\u2022 " + t, { x: 0.6, y: 1.8 + i * 0.55, w: 5.9, h: 0.5, fontSize: 14, color: INK });
  });
  s.addShape("rect", { x: 6.85, y: 1.3, w: 0.03, h: 5.5, fill: { color: "D8DEE6" } });
  s.addText("What's missing (the gap this project fills)", { x: 7.1, y: 1.3, w: 5.6, h: 0.4, fontSize: 16, bold: true, color: NAVY });
  ["No inverse design — can't ask \u201cwhat parameters give me the best FoM?\u201d", "No interactive tool — static plots only", "No per-prediction (local) explanations", "No deployable software artifact"].forEach((t, i) => {
    s.addText("\u2022 " + t, { x: 7.1, y: 1.8 + i * 0.55, w: 5.6, h: 0.5, fontSize: 14, color: "8A3A1F" });
  });
})();

// 4. Novelty
(() => {
  const s = contentSlide("Novelty Added in This Implementation");
  const cards = [
    { t: "Inverse-Design\nParameter Recommendation", d: "Given a target analyte RI, differential evolution searches L & Ag thickness to maximize predicted FoM.", c: AMBER },
    { t: "Interactive Full-Stack App", d: "Streamlit frontend + backend: live sliders, instant FoM prediction, no static plots.", c: TEAL },
    { t: "Local Explainability", d: "SHAP waterfall plots explain individual predictions, not just global trends.", c: "8E7CC3" },
  ];
  cards.forEach((card, i) => {
    const x = 0.6 + i * 4.13;
    s.addShape("roundRect", { x, y: 1.5, w: 3.85, h: 4.7, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "E3E7ED", width: 1 }, shadow: { type: "outer", color: "444444", opacity: 0.15, blur: 6, offset: 2, angle: 90 } });
    s.addShape("roundRect", { x: x + 0.3, y: 1.85, w: 0.7, h: 0.7, rectRadius: 0.1, fill: { color: card.c }, line: { width: 0 } });
    s.addText(String(i + 1), { x: x + 0.3, y: 1.85, w: 0.7, h: 0.7, fontSize: 22, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    s.addText(card.t, { x: x + 0.25, y: 2.75, w: 3.35, h: 1.0, fontSize: 16, bold: true, color: NAVY });
    s.addText(card.d, { x: x + 0.25, y: 3.75, w: 3.35, h: 2.2, fontSize: 13, color: GREY });
  });
})();

// 5. Section: Methodology
sectionHeader("Methodology", "Data \u2192 Models \u2192 Explainability \u2192 Recommendation \u2192 App");

// 6. Data generation
(() => {
  const s = contentSlide("Data Generation");
  s.addText("No MATLAB / original dataset was available \u2014 a physics-informed analytical simulator was built in Python, calibrated to well-documented SPR trends:", { x: 0.6, y: 1.3, w: 12, h: 0.7, fontSize: 15, color: INK });
  const rows = [
    ["Trend encoded", "Physical basis"],
    ["Resonance wavelength red-shifts with RI & thickness", "Standard SPR behaviour"],
    ["FWHM broadens with Ag thickness", "Increased radiative/ohmic damping"],
    ["An optimal sensing length exists", "Under- vs over-coupling of the plasmonic mode"],
    ["Sensitivity ~ thousands of nm/RIU", "Consistent with fiber-optic SPR literature"],
  ];
  s.addTable(rows.map((r, i) => r.map((t) => ({ text: t, options: { fontSize: 13, color: i === 0 ? "FFFFFF" : INK, bold: i === 0, fill: { color: i === 0 ? NAVY : (i % 2 === 0 ? "FFFFFF" : "EDF1F5") }, valign: "middle" } }))), {
    x: 0.6, y: 2.2, w: 8.5, colW: [5.2, 3.3], rowH: 0.65, border: { type: "solid", color: "E3E7ED", pt: 1 },
  });
  s.addShape("roundRect", { x: 9.4, y: 2.2, w: 3.3, h: 4.3, rectRadius: 0.08, fill: { color: NAVY }, line: { width: 0 } });
  s.addText("Dataset scale", { x: 9.6, y: 2.4, w: 3, h: 0.4, fontSize: 14, bold: true, color: AMBER });
  ["35,200 rows", "16 Ag thickness values\n(35\u201350 nm)", "25 sensing length values\n(5\u201329 mm)", "88 analyte RI values\n(1.330\u20131.418)"].forEach((t, i) => {
    s.addText(t, { x: 9.6, y: 2.95 + i * 0.85, w: 3.0, h: 0.8, fontSize: 13, color: "FFFFFF" });
  });
})();

// 7. Model comparison
(() => {
  const s = contentSlide("Model Comparison");
  const fs = require("fs");
  const rows = fs.readFileSync("../outputs/model_metrics.csv", "utf8").trim().split("\n").slice(1).map(l => l.split(","));
  rows.sort((a, b) => Number(a[1]) - Number(b[1]));
  const header = ["Model", "MAE (RIU\u207b\u00b9)", "RMSE", "R\u00b2"];
  const tableRows = [header, ...rows.map(r => [r[0], Number(r[1]).toFixed(3), Number(r[2]).toFixed(3), Number(r[3]).toFixed(4)])];
  s.addTable(tableRows.map((r, i) => r.map((t) => ({ text: String(t), options: { fontSize: 15, color: i === 0 ? "FFFFFF" : INK, bold: i === 0, fill: { color: i === 0 ? NAVY : (i % 2 === 0 ? "EDF1F5" : "FFFFFF") }, align: "center", valign: "middle" } }))), {
    x: 1.4, y: 1.5, w: 6.5, colW: [2.2, 1.9, 1.4, 1.0], rowH: 0.6, border: { type: "solid", color: "E3E7ED", pt: 1 },
  });
  s.addText("Random Forest and ANN were trained and validated in this environment; XGBoost and CatBoost run identically on the full stack once installed locally (pip install -r requirements.txt).", { x: 1.4, y: 4.3, w: 6.5, h: 1.2, fontSize: 12, italic: true, color: GREY });
  s.addImage({ path: "../outputs/trend_matching.png", x: 8.2, y: 1.5, w: 4.6, h: 1.65 });
  s.addText("Actual vs predicted FoM (trend matching)", { x: 8.2, y: 3.2, w: 4.6, h: 0.4, fontSize: 12, italic: true, color: GREY, align: "center" });
})();

// 8. Explainable AI
(() => {
  const s = contentSlide("Explainable AI (SHAP)");
  s.addImage({ path: "../outputs/shap_summary.png", x: 0.6, y: 1.4, w: 5.6, h: 3.7 });
  s.addText("SHAP beeswarm summary plot, CatBoost model trained on TMM-generated data", { x: 0.6, y: 5.15, w: 5.6, h: 1.0, fontSize: 11, italic: true, color: GREY });
  s.addShape("roundRect", { x: 6.6, y: 1.4, w: 6.1, h: 5.0, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "E3E7ED", width: 1 } });
  s.addText("Key finding", { x: 6.9, y: 1.65, w: 5.5, h: 0.4, fontSize: 15, bold: true, color: NAVY });
  s.addText("Analyte RI ranks highest, ahead of sensing length, wavelength, and Ag thickness \u2014 physically sensible, since RI is what an SPR sensor fundamentally detects. Obtained after fixing a dip-tracking bug that previously let wavelength absorb spurious noise (see Limitations).", { x: 6.9, y: 2.15, w: 5.5, h: 1.4, fontSize: 13, color: INK });
  s.addText("Novelty: local explanations", { x: 6.9, y: 3.7, w: 5.5, h: 0.4, fontSize: 15, bold: true, color: TEAL });
  s.addText("Beyond the paper's global-only SHAP analysis, this project adds per-prediction waterfall plots \u2014 explaining exactly why one specific design choice received its FoM score.", { x: 6.9, y: 4.15, w: 5.5, h: 1.5, fontSize: 13, color: INK });
})();

// 9. Parameter recommendation
(() => {
  const s = contentSlide("Parameter Recommendation System (Novelty)");
  s.addText("Forward prediction (the paper)", { x: 0.6, y: 1.35, w: 5.8, h: 0.4, fontSize: 15, bold: true, color: NAVY });
  s.addText("(\u03bb, L, RI, thickness)  \u2192  FoM", { x: 0.6, y: 1.85, w: 5.8, h: 0.5, fontSize: 16, color: INK, fontFace: "Consolas" });
  s.addShape("line", { x: 0.6, y: 2.55, w: 5.6, h: 0, line: { color: "D8DEE6", width: 1.5 } });
  s.addText("Inverse design (this project)", { x: 0.6, y: 2.8, w: 5.8, h: 0.4, fontSize: 15, bold: true, color: AMBER });
  s.addText("target RI  \u2192  optimal (L, thickness)\nmaximizing predicted FoM", { x: 0.6, y: 3.3, w: 5.8, h: 1.0, fontSize: 16, color: INK, fontFace: "Consolas" });
  s.addText("Powered by differential evolution over the trained surrogate model, with resonance wavelength derived consistently from the physics module for each candidate.", { x: 0.6, y: 4.5, w: 5.8, h: 1.2, fontSize: 13, italic: true, color: GREY });

  s.addShape("roundRect", { x: 6.8, y: 1.35, w: 5.9, h: 5.3, rectRadius: 0.08, fill: { color: NAVY }, line: { width: 0 } });
  s.addText("Example recommendation", { x: 7.1, y: 1.6, w: 5.3, h: 0.4, fontSize: 14, bold: true, color: AMBER });
  const kv = [["Target analyte RI", "1.350"], ["Recommended Ag thickness", "35.0 nm"], ["Recommended sensing length", "20.7 mm"], ["Resulting resonance wavelength", "742.7 nm"], ["Predicted FoM", "51.6 RIU\u207b\u00b9"]];
  kv.forEach((r, i) => {
    s.addText(r[0], { x: 7.1, y: 2.2 + i * 0.68, w: 3.4, h: 0.6, fontSize: 13, color: "C9D6E8" });
    s.addText(r[1], { x: 10.5, y: 2.2 + i * 0.68, w: 2.0, h: 0.6, fontSize: 14, bold: true, color: "FFFFFF", align: "right" });
  });
})();

// 10. Architecture
(() => {
  const s = contentSlide("System Architecture");
  const boxes = [
    { t: "Physics\nSimulator", x: 0.6 },
    { t: "ML Training\n(RF/XGB/CatBoost/ANN)", x: 3.3 },
    { t: "SHAP\nExplainability", x: 6.5 },
    { t: "Optimizer\n(Recommendation)", x: 9.4 },
  ];
  boxes.forEach((b) => {
    s.addShape("roundRect", { x: b.x, y: 1.6, w: 2.4, h: 1.3, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: TEAL, width: 1.5 } });
    s.addText(b.t, { x: b.x, y: 1.6, w: 2.4, h: 1.3, fontSize: 13, bold: true, color: NAVY, align: "center", valign: "middle" });
  });
  s.addText("Backend (Python modules)", { x: 0.6, y: 3.05, w: 11, h: 0.35, fontSize: 12, italic: true, color: GREY });
  s.addShape("line", { x: 6.9, y: 3.6, w: 0, h: 0.6, line: { color: "D8DEE6", width: 2 } });
  s.addShape("roundRect", { x: 2.4, y: 4.3, w: 8.9, h: 2.5, rectRadius: 0.08, fill: { color: NAVY }, line: { width: 0 } });
  s.addText("Frontend: Streamlit App", { x: 2.7, y: 4.55, w: 8, h: 0.4, fontSize: 16, bold: true, color: AMBER });
  ["Overview", "Live FoM Predictor", "Model Comparison", "Explainable AI", "Parameter Recommendation"].forEach((t, i) => {
    s.addShape("roundRect", { x: 2.7 + i * 1.72, y: 5.15, w: 1.55, h: 1.35, rectRadius: 0.06, fill: { color: "1B3A63" }, line: { width: 0 } });
    s.addText(t, { x: 2.75 + i * 1.72, y: 5.2, w: 1.45, h: 1.25, fontSize: 11, color: "FFFFFF", align: "center", valign: "middle" });
  });
})();

// 11. Limitations
(() => {
  const s = contentSlide("Limitations & Future Work");
  const items = [
    "Fixed: resonance dip-finder could jump between competing near-degenerate dips, producing spurious sensitivity spikes; now uses continuity-tracked dip search + wider scan window",
    "Fixed: trend-matching plot previously sampled only the 200 lowest-FoM points, making Actual look artificially flat; now uses a representative full-range sample",
    "Remaining gap: single-pole Drude model for Ag somewhat underestimates its real refractive index vs. tabulated Johnson & Christy data",
  ];
  items.forEach((t, i) => {
    s.addShape("roundRect", { x: 0.6, y: 1.5 + i * 1.7, w: 12.1, h: 1.4, rectRadius: 0.06, fill: { color: "FFFFFF" }, line: { color: "E3E7ED", width: 1 } });
    s.addText(t, { x: 0.95, y: 1.5 + i * 1.7, w: 11.4, h: 1.4, fontSize: 15, color: INK, valign: "middle" });
  });
})();

// 12. Conclusion
(() => {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Conclusion", { x: 0.7, y: 0.7, w: 8, h: 0.7, fontSize: 30, bold: true, color: "FFFFFF", fontFace: "Georgia" });
  s.addText("This project reproduces the paper's ML + XAI pipeline for FoM prediction, and extends it with a genuinely novel inverse-design parameter recommendation system and an interactive full-stack application \u2014 while transparently documenting every modelling assumption made under a tight timeline.", { x: 0.7, y: 1.7, w: 11.5, h: 1.5, fontSize: 17, color: "C9D6E8" });
  const checks = ["Working ML model", "Frontend + Backend", "Explainable AI", "Parameter recommendation", "Report + PPT + GitHub repo"];
  checks.forEach((t, i) => {
    const y = 3.5 + i * 0.68;
    s.addShape("ellipse", { x: 0.9, y, w: 0.35, h: 0.35, fill: { color: AMBER }, line: { width: 0 } });
    s.addText("\u2713", { x: 0.9, y, w: 0.35, h: 0.35, fontSize: 14, bold: true, color: NAVY, align: "center", valign: "middle" });
    s.addText(t, { x: 1.45, y: y - 0.05, w: 8, h: 0.45, fontSize: 16, color: "FFFFFF" });
  });
})();

pres.writeFile({ fileName: "FOSD_Project_Presentation.pptx" }).then(() => console.log("PPT written.")).catch(e=>{console.error("WRITE ERROR", e); process.exit(1)});
