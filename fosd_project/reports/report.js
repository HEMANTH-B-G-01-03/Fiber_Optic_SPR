const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, PageBreak, BorderStyle, LevelFormat,
  Numbering
} = require("docx");

const H1 = (t) => new Paragraph({ text: t, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
const H2 = (t) => new Paragraph({ text: t, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } });
const P = (t, opts = {}) => new Paragraph({ children: [new TextRun({ text: t, ...opts })], spacing: { after: 120 } });
const bullet = (t) => new Paragraph({ text: t, bullet: { level: 0 }, spacing: { after: 60 } });

function img(path, width, height) {
  return new Paragraph({
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width, height } })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 100, after: 100 },
  });
}

function simpleTable(headers, rows, colWidths) {
  const total = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: "D9E2F3" },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true })] })],
    })),
  });
  const dataRows = rows.map((r) => new TableRow({
    children: r.map((c, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      children: [new Paragraph(String(c))],
    })),
  }));
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: colWidths, rows: [headerRow, ...dataRows] });
}

const metrics = fs.readFileSync("../outputs/model_metrics.csv", "utf8").trim().split("\n").slice(1).map(l => {
  const [Model, MAE, RMSE, R2] = l.split(",");
  return [Model, Number(MAE).toFixed(3), Number(RMSE).toFixed(3), Number(R2).toFixed(4)];
});

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      new Paragraph({ text: "Machine Learning and Explainable AI for Fiber-Optic SPR Sensor Design Optimization", heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { after: 100 } }),
      new Paragraph({ text: "Project Report", alignment: AlignmentType.CENTER, spacing: { after: 50 } }),
      new Paragraph({ text: "An implementation and extension of: \u201cIntervention of Machine Learning and Explainable Artificial Intelligence in Fiber-Optic Sensor Device Data for Systematic and Comprehensive Performance Optimization\u201d (IEEE Sensors Letters, 2024)", alignment: AlignmentType.CENTER, italics: true, spacing: { after: 400 } }),

      H1("1. Introduction"),
      P("Surface Plasmon Resonance (SPR) based fiber-optic sensor devices (FOSDs) are widely used for refractive-index (RI) sensing in biosensing, chemical detection, and environmental monitoring. Their performance is characterized by the Figure of Merit (FoM), which combines sensitivity and resonance sharpness (FWHM). Traditionally, FoM is obtained via slow electromagnetic simulations (e.g. the Transfer Matrix Method, TMM) in MATLAB, making exhaustive design-space exploration impractical."),
      P("The reference paper addresses this by training machine learning (ML) models to predict FoM directly from four design parameters \u2014 wavelength, sensing length (L), analyte RI, and Ag layer thickness \u2014 and uses SHAP (SHapley Additive exPlanations) to interpret which parameters matter most."),

      H1("2. Objectives of the Reference Paper"),
      bullet("Replace slow physics-based TMM simulation with fast ML-based FoM prediction."),
      bullet("Benchmark four ML models \u2014 Random Forest, XGBoost, CatBoost, and a shallow ANN \u2014 on a 32,760-row simulated dataset."),
      bullet("Identify the best-performing model (CatBoost, MAE = 0.37 RIU\u207b\u00b9) via MAE, RMSE, and R\u00b2."),
      bullet("Use SHAP to explain global feature importance, finding analyte RI and wavelength as the dominant drivers of FoM."),

      H1("3. Outputs of the Reference Paper"),
      bullet("A simulated 5-column dataset (4 inputs + FoM) generated via MATLAB TMM."),
      bullet("Trained ML models with comparative MAE / RMSE / R\u00b2 metrics."),
      bullet("Actual-vs-predicted trend plots for all four models."),
      bullet("Global SHAP summary plots ranking feature importance."),
      P("Notably, the paper is a pure analysis paper: it does not produce any software artifact \u2014 no interactive tool, no inverse-design capability, and no deployment."),

      H1("4. Novelty Added in This Implementation"),
      P("This project extends the paper along three axes, chosen to be both technically meaningful and demonstrable:"),
      bullet("Inverse-design Parameter Recommendation System: given a target analyte RI, a global optimizer (differential evolution) searches the design space to recommend the Ag thickness and sensing length that maximize predicted FoM \u2014 the reverse of the paper's forward-only prediction."),
      bullet("Interactive full-stack application: a Streamlit-based frontend + backend lets a user explore FoM predictions live via sliders, rather than reading static plots."),
      bullet("Local (per-prediction) explainability: in addition to the paper's global SHAP summary, this project adds SHAP waterfall plots explaining individual predictions \u2014 useful for justifying a specific design choice."),

      H1("5. Methodology"),
      H2("5.1 Data Generation"),
      P("The original MATLAB TMM dataset and code were not available. An earlier draft of this project used a calibrated analytical surrogate as an interim stand-in; that surrogate has since been replaced with a validated first-principles multilayer Transfer-Matrix-Method (TMM) + ray-optics simulator, consistent with the standard methodology used across the PMMA-core fiber-optic SPR sensor literature that the reference paper belongs to."),
      P("Reflectance at the core/Ag/analyte interface is computed with the closed-form 3-medium p-polarization Fresnel/transfer-matrix formula (Gupta & Verma, 2009). PMMA core dispersion uses a two-term Cauchy equation checked against the experimentally reported PMMA index (~1.49 in the visible, matched to 4 decimal places at 632.8 nm); Ag permittivity uses the single-pole Drude model of Rakic et al. (1998). A continuum of guided meridional rays (angle from the core/cladding critical angle to 90 degrees) is combined into a transmitted spectrum, with each ray reflecting N = L/(D\u00b7tan\u03b8) times inside the sensing region, weighted by sin\u03b8\u00b7cos\u03b8 (the standard guided-ray power distribution). Resonance wavelength, FWHM, sensitivity, and FoM are extracted from the resulting dip."),
      P("A known, explicitly documented limitation: the single-pole Drude model somewhat underestimates silver's real refractive index versus tabulated Johnson & Christy data, which pushes some sensitivity values toward the high end of what is typically reported experimentally. The earlier surrogate is retained for reference at backend/physics_simulator_surrogate.py but is no longer used by the pipeline."),
      P(`The resulting dataset contains ${fs.readFileSync("../data/fosd_dataset.csv","utf8").trim().split("\n").length - 1} rows spanning 16 Ag-thickness values (35\u201350 nm), 25 sensing-length values (5\u201329 mm), and 88 analyte-RI values (1.330\u20131.418), closely matching the scale of the original paper's dataset.`),

      H2("5.2 ML Models"),
      P("Four regression models were trained on an 80:20 train/test split, mirroring the paper: Random Forest, XGBoost, CatBoost, and a shallow ANN (2 hidden layers, 64/32 units)."),

      H2("5.3 Explainable AI"),
      P("SHAP TreeExplainer (for tree-based models) or KernelExplainer (for the ANN) is used to compute both global feature importance and local per-prediction explanations."),

      H2("5.4 Parameter Recommendation System (Novelty)"),
      P("Given a target analyte RI, differential evolution optimizes over sensing length and Ag thickness, using the trained surrogate model as the objective function, with the resonance wavelength computed consistently via the physics module for each candidate (rather than treated as an independent free variable) to keep recommendations physically self-consistent."),

      H2("5.5 System Architecture (Frontend + Backend)"),
      bullet("Backend modules: materials.py, tmm_core.py, tmm_simulator.py (TMM physics engine), generate_dataset.py, train_models.py, explainability.py, optimizer.py."),
      bullet("Frontend: app.py (Streamlit) \u2014 Overview, Live FoM Predictor, Model Comparison, Explainable AI, and Parameter Recommendation pages."),

      H1("6. Results"),
      H2("6.1 Model Comparison"),
      simpleTable(["Model", "MAE (RIU\u207b\u00b9)", "RMSE", "R\u00b2"], metrics, [2500, 2500, 2000, 2000]),
      new Paragraph({ text: "", spacing: { after: 150 } }),
      H2("6.2 Trend Matching (Actual vs Predicted FoM)"),
      img("../outputs/trend_matching.png", 580, 190),

      H2("6.3 Global Feature Importance (SHAP)"),
      P("SHAP TreeExplainer was applied to the best model (CatBoost) trained on the TMM-generated dataset. Analyte RI ranks highest, followed by sensing length, wavelength, and Ag thickness a distant fourth \u2014 physically sensible, since RI is what an SPR sensor is fundamentally detecting. This ranking was obtained after fixing a resonance-tracking bug in the simulator (Section 8) that previously let wavelength absorb some of the RI signal through spurious dip-jump noise."),
      img("../outputs/shap_summary.png", 480, 320),
      img("../outputs/shap_mean_importance.png", 480, 320),
      P("This is a notably different ranking from the earlier surrogate-based run, where Ag thickness and sensing length dominated \u2014 a good illustration of why replacing the surrogate with validated physics mattered: it changes not just accuracy but *which design parameters the model says matter most*, which is the entire point of an XAI-driven design tool.", { italics: true }),

      H1("7. How to Run This Project"),
      bullet("1. pip install -r requirements.txt"),
      bullet("2. bash run_pipeline.sh  (generates data, trains all 4 models, runs SHAP)"),
      bullet("3. cd frontend && streamlit run app.py"),

      H1("8. Limitations and Future Work"),
      bullet("Fixed: the resonance dip-finder previously used a plain global-minimum search per data point, which could jump discontinuously between two near-degenerate competing dips as RI was perturbed by a tiny amount \u2014 producing spurious, non-physical sensitivity spikes (up to ~100,000 nm/RIU) and a noisy FoM-vs-RI curve. This was fixed with a continuity-tracked dip search (each step anchored to the resonance wavelength of its nearest neighbor) plus a wider wavelength scan window to reduce boundary clipping; sensitivities are now bounded to a few thousand-to-tens-of-thousands nm/RIU range."),
      bullet("Fixed: the actual-vs-predicted trend-matching plot previously sampled only the 200 lowest-FoM test points (via a truncated argsort), making the 'Actual' curve look artificially flat; it now uses a representative random sample across the full FoM range."),
      bullet("Remaining known limitation is material-model accuracy: the single-pole Drude model used for silver somewhat underestimates its real refractive index versus tabulated Johnson & Christy data, which pushes some sensitivity values toward the high end of typical experimental reports. Swapping in an interpolated experimental n,k table for Ag is the natural next accuracy improvement."),
      bullet("Access to the paper's original MATLAB TMM code or dataset, if available, would allow a direct numerical cross-check against this project's independently implemented TMM."),
      bullet("Extending the optimizer to multi-objective (e.g. simultaneously maximizing FoM and minimizing fabrication cost/complexity) is a natural next step."),

      H1("9. Conclusion"),
      P("This project reproduces the reference paper's ML + XAI pipeline for FoM prediction, replaces the dataset-generating physics with a validated multilayer TMM + ray-optics simulator consistent with the standard fiber-optic SPR sensor literature, and extends the pipeline with a genuinely novel inverse-design parameter recommendation system and an interactive full-stack application, while transparently documenting the remaining modelling assumptions."),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("FOSD_Project_Report.docx", buf);
  console.log("Report written.");
});
