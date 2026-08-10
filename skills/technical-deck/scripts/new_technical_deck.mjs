#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";

const require = createRequire(import.meta.url);

function loadPptxGenJS() {
  const candidates = [];
  try {
    return require("pptxgenjs");
  } catch {}
  try {
    const npmRoot = execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim();
    candidates.push(path.join(npmRoot, "pptxgenjs"));
  } catch {}
  candidates.push(
    path.join(os.homedir(), "Library", "Application Support", "WutPack", "npm-global", "lib", "node_modules", "pptxgenjs"),
  );
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch {}
  }
  throw new Error("pptxgenjs not found. Install it with: npm install -g pptxgenjs");
}

const pptxgen = loadPptxGenJS();
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "WutPack";
pptx.subject = "Editable executive consulting diagrams";
pptx.title = "Fictional Growth Strategy Case";
pptx.company = "";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};
pptx.defineSlideMaster({
  title: "CONSULTING",
  background: { color: "F7F8FA" },
  objects: [
    { rect: { x: 0, y: 0, w: 13.333, h: 0.08, fill: { color: "123B5D" }, line: { transparency: 100 } } },
    { text: { text: "WUTPACK • FICTIONAL CASE", options: { x: 10.35, y: 7.1, w: 2.45, h: 0.18, fontSize: 8, color: "6B7785", align: "right", margin: 0 } } },
  ],
  slideNumber: { x: 12.86, y: 7.09, w: 0.2, h: 0.18, fontSize: 8, color: "6B7785", align: "right", margin: 0 },
});

const C = {
  navy: "123B5D",
  blue: "2C6EAA",
  sky: "DDEBF5",
  teal: "168C8C",
  tealPale: "DDF2F0",
  green: "3E8E6B",
  greenPale: "E3F1E9",
  amber: "D99A2B",
  amberPale: "FFF1D6",
  red: "B95050",
  ink: "202A35",
  gray: "647180",
  line: "B7C3CD",
  pale: "EDF1F4",
  white: "FFFFFF",
};

function addTitle(slide, title, kicker, takeaway) {
  slide.addText(kicker.toUpperCase(), { x: 0.55, y: 0.28, w: 3.2, h: 0.2, fontSize: 9, bold: true, color: C.teal, charSpacing: 1.4, margin: 0 });
  slide.addText(title, { x: 0.55, y: 0.52, w: 8.9, h: 0.48, fontSize: 24, bold: true, color: C.navy, margin: 0, fit: "shrink" });
  slide.addText(takeaway, { x: 9.3, y: 0.48, w: 3.5, h: 0.48, fontSize: 10.5, color: C.gray, align: "right", valign: "mid", margin: 0.02, fit: "shrink" });
  slide.addShape(pptx.ShapeType.line, { x: 0.55, y: 1.08, w: 12.25, h: 0, line: { color: C.line, width: 0.8 } });
}

function addCallout(slide, text, x, y, w, h, color = C.teal, fill = C.tealPale) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.04, fill: { color: fill }, line: { color, width: 1.2 } });
  slide.addText(text, { x: x + 0.14, y: y + 0.08, w: w - 0.28, h: h - 0.16, fontSize: 11.5, bold: true, color: C.ink, valign: "mid", margin: 0.02, fit: "shrink" });
}

function addPill(slide, text, x, y, w, fill, color = C.white) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h: 0.31, rectRadius: 0.08, fill: { color: fill }, line: { color: fill, transparency: 100 } });
  slide.addText(text, { x, y: y + 0.065, w, h: 0.14, fontSize: 8.5, bold: true, color, align: "center", margin: 0, fit: "shrink" });
}

// Slide 1: where-to-play matrix.
{
  const s = pptx.addSlide("CONSULTING");
  addTitle(s, "Prioritize Coastal and North for the first expansion wave", "Market-entry recommendation", "Attractiveness and ability to win point to two markets; Central remains a gated option.");

  const x = 0.85, y = 1.55, w = 7.55, h = 4.65;
  s.addShape(pptx.ShapeType.rect, { x, y, w: w / 2, h: h / 2, fill: { color: "F2F4F6" }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x: x + w / 2, y, w: w / 2, h: h / 2, fill: { color: C.greenPale }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x, y: y + h / 2, w: w / 2, h: h / 2, fill: { color: "F7F1E7" }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x: x + w / 2, y: y + h / 2, w: w / 2, h: h / 2, fill: { color: C.sky }, line: { transparency: 100 } });
  s.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: C.white, transparency: 100 }, line: { color: C.line, width: 1.1 } });
  s.addShape(pptx.ShapeType.line, { x: x + w / 2, y, w: 0, h, line: { color: C.white, width: 2.5 } });
  s.addShape(pptx.ShapeType.line, { x, y: y + h / 2, w, h: 0, line: { color: C.white, width: 2.5 } });

  s.addText("BUILD SELECTIVELY", { x: x + 0.18, y: y + 0.16, w: 1.7, h: 0.2, fontSize: 8.5, bold: true, color: C.gray, margin: 0 });
  s.addText("PRIORITIZE", { x: x + w / 2 + 0.18, y: y + 0.16, w: 1.35, h: 0.2, fontSize: 8.5, bold: true, color: C.green, margin: 0 });
  s.addText("DEPRIORITIZE", { x: x + 0.18, y: y + h / 2 + 0.16, w: 1.55, h: 0.2, fontSize: 8.5, bold: true, color: C.gray, margin: 0 });
  s.addText("PARTNER / TEST", { x: x + w / 2 + 0.18, y: y + h / 2 + 0.16, w: 1.55, h: 0.2, fontSize: 8.5, bold: true, color: C.blue, margin: 0 });

  const bubbles = [
    { label: "Coastal", score: "81", x: 6.7, y: 2.0, d: 1.05, color: C.teal },
    { label: "North", score: "78", x: 5.1, y: 2.65, d: 0.94, color: C.green },
    { label: "Central", score: "72", x: 5.85, y: 4.65, d: 0.82, color: C.blue },
    { label: "West", score: "58", x: 2.35, y: 4.75, d: 0.68, color: C.gray },
  ];
  for (const b of bubbles) {
    s.addShape(pptx.ShapeType.ellipse, { x: b.x, y: b.y, w: b.d, h: b.d, fill: { color: b.color, transparency: 8 }, line: { color: C.white, width: 1.5 }, shadow: { type: "outer", color: "8593A0", blur: 1, angle: 45, distance: 1, opacity: 0.14 } });
    s.addText(`${b.label}\n${b.score}`, { x: b.x, y: b.y + b.d * 0.26, w: b.d, h: b.d * 0.46, fontSize: 10.5, bold: true, color: C.white, align: "center", valign: "mid", margin: 0, fit: "shrink" });
  }

  s.addText("Market attractiveness  →", { x: 3.2, y: 6.28, w: 2.9, h: 0.22, fontSize: 10, bold: true, color: C.gray, align: "center", margin: 0 });
  s.addText("Ability to win  →", { x: 0.18, y: 3.1, w: 1.6, h: 0.22, fontSize: 10, bold: true, color: C.gray, rotate: 270, align: "center", margin: 0 });

  s.addShape(pptx.ShapeType.roundRect, { x: 8.8, y: 1.55, w: 4.0, h: 4.65, fill: { color: C.white }, line: { color: C.line, width: 1 } });
  s.addText("Recommendation", { x: 9.08, y: 1.83, w: 2.2, h: 0.28, fontSize: 16, bold: true, color: C.navy, margin: 0 });
  addPill(s, "WAVE 1", 11.45, 1.82, 0.95, C.teal);
  const recommendation = [
    { n: "1", title: "Launch Coastal", detail: "Fastest growth; protect economics with a partner-led model." },
    { n: "2", title: "Scale North", detail: "Strong fit and lower execution complexity support direct entry." },
    { n: "3", title: "Gate Central", detail: "Run a 90-day commercial test before committing fixed cost." },
  ];
  recommendation.forEach((item, i) => {
    const iy = 2.42 + i * 0.95;
    s.addShape(pptx.ShapeType.ellipse, { x: 9.08, y: iy, w: 0.38, h: 0.38, fill: { color: i < 2 ? C.teal : C.blue }, line: { transparency: 100 } });
    s.addText(item.n, { x: 9.08, y: iy + 0.095, w: 0.38, h: 0.12, fontSize: 9, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(item.title, { x: 9.62, y: iy - 0.01, w: 2.72, h: 0.22, fontSize: 12, bold: true, color: C.ink, margin: 0 });
    s.addText(item.detail, { x: 9.62, y: iy + 0.25, w: 2.72, h: 0.42, fontSize: 9.5, color: C.gray, margin: 0, fit: "shrink" });
  });
  addCallout(s, "Illustrative scoring only. Replace with sourced market, customer, and economics evidence.", 9.08, 5.35, 3.42, 0.58, C.amber, C.amberPale);
}

// Slide 2: value-creation roadmap.
{
  const s = pptx.addSlide("CONSULTING");
  addTitle(s, "Sequence quick wins before scaling the operating model", "Value-creation roadmap", "The first 90 days validate economics and owners; later waves scale only after explicit gates.");

  const labelX = 0.6, gridX = 3.0, gridY = 1.72, colW = 3.16, rowH = 0.98;
  const phases = [
    { title: "0–30 DAYS", subtitle: "Mobilize", color: C.navy },
    { title: "31–90 DAYS", subtitle: "Prove", color: C.blue },
    { title: "3–12 MONTHS", subtitle: "Scale", color: C.teal },
  ];
  phases.forEach((phase, i) => {
    const px = gridX + i * colW;
    s.addShape(pptx.ShapeType.rect, { x: px, y: 1.32, w: colW - 0.08, h: 0.58, fill: { color: phase.color }, line: { transparency: 100 } });
    s.addText(phase.title, { x: px + 0.12, y: 1.45, w: 1.5, h: 0.18, fontSize: 10, bold: true, color: C.white, margin: 0 });
    s.addText(phase.subtitle, { x: px + 1.68, y: 1.45, w: 1.15, h: 0.18, fontSize: 10, color: C.white, align: "right", margin: 0 });
  });

  const rows = [
    { label: "Commercial", owner: "CCO", items: ["Segment accounts\nand set price floors", "Pilot value pricing\nin two regions", "Roll winning offers\nacross channels"] },
    { label: "Operations", owner: "COO", items: ["Baseline service cost\nand bottlenecks", "Redesign dispatch\nand capacity rules", "Automate repeatable\nworkflow steps"] },
    { label: "Organization", owner: "CHRO", items: ["Name initiative owners\nand decision rights", "Install weekly value\nreview cadence", "Tie incentives to\nrealized value"] },
    { label: "Data & tech", owner: "CIO", items: ["Define KPI dictionary\nand source systems", "Ship executive cockpit\nand QA controls", "Scale governed data\nproducts and alerts"] },
  ];
  rows.forEach((row, ri) => {
    const ry = gridY + ri * rowH;
    s.addShape(pptx.ShapeType.rect, { x: labelX, y: ry, w: 2.2, h: rowH - 0.1, fill: { color: ri % 2 ? "F2F5F7" : C.white }, line: { color: C.line, width: 0.7 } });
    s.addText(row.label, { x: labelX + 0.15, y: ry + 0.18, w: 1.2, h: 0.22, fontSize: 12, bold: true, color: C.ink, margin: 0 });
    addPill(s, row.owner, labelX + 1.43, ry + 0.2, 0.55, C.gray);
    row.items.forEach((item, ci) => {
      const ix = gridX + ci * colW;
      const palette = [C.sky, C.greenPale, C.tealPale];
      const border = [C.blue, C.green, C.teal];
      s.addShape(pptx.ShapeType.roundRect, { x: ix + 0.12, y: ry + 0.08, w: colW - 0.32, h: rowH - 0.26, rectRadius: 0.04, fill: { color: palette[ci] }, line: { color: border[ci], width: 0.9 } });
      s.addText(item, { x: ix + 0.27, y: ry + 0.21, w: colW - 0.62, h: rowH - 0.52, fontSize: 10.5, color: C.ink, bold: ci === 0, align: "center", valign: "mid", margin: 0.01, fit: "shrink" });
    });
  });

  const gateY = 5.8;
  s.addShape(pptx.ShapeType.line, { x: 1.65, y: gateY, w: 10.35, h: 0, line: { color: C.line, width: 1.2 } });
  const gates = [
    { x: 3.0, label: "Baseline signed off" },
    { x: 6.16, label: "Pilot economics proven" },
    { x: 9.32, label: "Scale funding released" },
  ];
  gates.forEach((gate, i) => {
    s.addShape(pptx.ShapeType.diamond, { x: gate.x + 1.22, y: gateY - 0.16, w: 0.32, h: 0.32, fill: { color: i === 2 ? C.teal : C.amber }, line: { color: C.white, width: 1 } });
    s.addText(gate.label, { x: gate.x + 0.42, y: gateY + 0.25, w: 1.92, h: 0.22, fontSize: 9.2, bold: true, color: C.gray, align: "center", margin: 0, fit: "shrink" });
  });
  addCallout(s, "Governance principle: fund the next wave only after the prior gate has an owner, evidence, and realized-value check.", 0.82, 6.35, 11.65, 0.5, C.teal, C.tealPale);
}

// Slide 3: quantified value case.
{
  const s = pptx.addSlide("CONSULTING");
  addTitle(s, "$24M of annualized EBITDA potential is concentrated in three levers", "Illustrative value case", "Pricing, route density, and procurement contribute 75% of the modeled opportunity.");

  const header = ["Value lever", "EBITDA impact", "Confidence", "Accountable owner"].map((text) => ({
    text,
    options: { fill: C.navy, color: C.white, bold: true },
  }));
  const rows = [
    header,
    ["Value pricing", "$7M", "Medium", "CCO"],
    ["Route density", "$6M", "High", "COO"],
    ["Strategic sourcing", "$5M", "High", "CPO"],
    ["Sales productivity", "$4M", "Medium", "CCO"],
    ["Back-office automation", "$2M", "Low", "CIO"],
  ];
  s.addTable(rows, { x: 0.62, y: 1.48, w: 5.65, h: 3.45, border: { color: C.line, width: 0.8 }, fill: C.white, color: C.ink, fontFace: "Aptos", fontSize: 11.5, margin: 0.08, rowH: 0.52, autoFit: false, colW: [2.05, 1.25, 1.05, 1.3], bold: false });
  s.addText("Annualized EBITDA potential (USD millions)", { x: 6.72, y: 1.45, w: 5.65, h: 0.3, fontSize: 13, bold: true, color: C.ink, margin: 0 });
  const data = [{ name: "Impact", labels: ["Pricing", "Routing", "Sourcing", "Sales force", "Automation"], values: [7, 6, 5, 4, 2] }];
  s.addChart(pptx.ChartType.bar, data, { x: 6.62, y: 1.8, w: 5.85, h: 3.65, catAxisLabelFontSize: 10, valAxisLabelFontSize: 9, valAxisMinVal: 0, valAxisMaxVal: 8, valAxisMajorUnit: 2, valGridLine: { color: "D8E0E7", width: 1 }, showLegend: false, showTitle: false, chartColors: [C.teal], showValue: true, dataLabelPosition: "outEnd", showCatName: false, showValAxisTitle: false, showCatAxisTitle: false, border: { color: C.line, width: 1 } });

  addCallout(s, "Recommendation: mobilize the top three levers now; keep the remaining $6M as gated upside until pilots validate adoption and run-rate cost.", 0.78, 5.35, 7.2, 0.78, C.green, C.greenPale);
  s.addShape(pptx.ShapeType.roundRect, { x: 8.35, y: 5.35, w: 4.12, h: 0.78, fill: { color: C.white }, line: { color: C.line, width: 1 } });
  s.addText("MODEL BASIS", { x: 8.58, y: 5.53, w: 1.15, h: 0.18, fontSize: 8.5, bold: true, color: C.gray, margin: 0 });
  s.addText("Fictional case • illustrative values • no client data", { x: 9.68, y: 5.49, w: 2.5, h: 0.28, fontSize: 9.5, color: C.ink, align: "right", margin: 0, fit: "shrink" });
  s.addText("The table preserves exact modeled values; the chart communicates relative magnitude. Validate assumptions before any real decision.", { x: 0.78, y: 6.42, w: 11.3, h: 0.24, fontSize: 9.5, color: C.gray, margin: 0 });
}

const outputArg = process.argv.find((arg) => arg.startsWith("--output="));
const output = outputArg ? outputArg.slice("--output=".length) : "executive-consulting-demo.pptx";
await pptx.writeFile({ fileName: output });
console.log(output);
