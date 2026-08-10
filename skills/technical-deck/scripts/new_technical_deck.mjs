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
pptx.subject = "Editable technical PowerPoint diagrams";
pptx.title = "Technical Diagram Starter";
pptx.company = "";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const C = {
  navy: "16324F",
  blue: "2F75B5",
  teal: "2A9D8F",
  green: "70AD47",
  amber: "E9A23B",
  red: "C94C4C",
  ink: "1F2937",
  gray: "64748B",
  line: "AAB7C4",
  pale: "EEF4F8",
  white: "FFFFFF",
};

function addTitle(slide, title, subtitle = "") {
  slide.addText(title, { x: 0.45, y: 0.22, w: 8.9, h: 0.38, fontFace: "Aptos Display", fontSize: 23, bold: true, color: C.navy, margin: 0 });
  if (subtitle) slide.addText(subtitle, { x: 9.25, y: 0.28, w: 3.55, h: 0.25, fontSize: 10, color: C.gray, align: "right", margin: 0 });
  slide.addShape(pptx.ShapeType.line, { x: 0.45, y: 0.72, w: 12.35, h: 0, line: { color: C.line, width: 1 } });
}

function box(slide, x, y, w, h, title, detail = "", accent = C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: C.white }, line: { color: accent, width: 1.5 }, shadow: { type: "outer", color: "A0A8B0", blur: 1, angle: 45, distance: 1, opacity: 0.13 } });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.09, h, fill: { color: accent }, line: { color: accent, transparency: 100 } });
  slide.addText(title, { x: x + 0.18, y: y + 0.12, w: w - 0.3, h: 0.28, fontSize: 15, bold: true, color: C.ink, margin: 0, fit: "shrink" });
  if (detail) slide.addText(detail, { x: x + 0.18, y: y + 0.47, w: w - 0.3, h: h - 0.58, fontSize: 10.5, color: C.gray, margin: 0, breakLine: false, valign: "top", fit: "shrink" });
}

function arrow(slide, x, y, w, h, label = "", color = C.blue, dashed = false) {
  slide.addShape(pptx.ShapeType.line, { x, y, w, h, line: { color, width: 1.8, dash: dashed ? "dash" : "solid", beginArrowType: "none", endArrowType: "triangle" } });
  if (label) slide.addText(label, { x: x + w / 2 - 0.65, y: y + h / 2 - 0.18, w: 1.3, h: 0.25, fontSize: 9.5, bold: true, color, align: "center", fill: { color: "F7F9FC", transparency: 8 }, margin: 0.02 });
}

function callout(slide, text, x, y, w, h, color = C.amber) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, fill: { color: "FFF7E8" }, line: { color, width: 1 } });
  slide.addText(text, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: h - 0.16, fontSize: 11, bold: true, color: C.ink, valign: "mid", margin: 0.03, fit: "shrink" });
}

// Slide 1: architecture/block diagram.
{
  const s = pptx.addSlide();
  s.background = { color: "F7F9FC" };
  addTitle(s, "Controller-to-Flash Architecture", "Editable native PowerPoint shapes");
  s.addShape(pptx.ShapeType.roundRect, { x: 0.55, y: 1.0, w: 12.15, h: 5.65, fill: { color: "F1F5F9" }, line: { color: "C8D3DE", width: 1 } });
  s.addText("SYSTEM BOUNDARY", { x: 0.78, y: 1.12, w: 1.8, h: 0.22, fontSize: 9, bold: true, color: C.gray, margin: 0 });
  box(s, 0.9, 2.1, 2.25, 1.35, "Host / CPU", "Firmware\nWork queue", C.navy);
  box(s, 4.0, 1.55, 2.45, 1.35, "Flash Controller", "Command scheduler\nECC and retry", C.blue);
  box(s, 4.0, 3.65, 2.45, 1.35, "DMA Engine", "Burst transfers\nBuffer ownership", C.teal);
  box(s, 7.4, 1.35, 2.0, 1.15, "Die 0", "512 Mbit", C.green);
  box(s, 7.4, 2.75, 2.0, 1.15, "Die 1", "512 Mbit", C.green);
  box(s, 10.1, 1.35, 2.0, 1.15, "Die 2", "512 Mbit", C.green);
  box(s, 10.1, 2.75, 2.0, 1.15, "Die 3", "512 Mbit", C.green);
  arrow(s, 3.15, 2.55, 0.85, 0, "commands", C.blue);
  arrow(s, 6.45, 2.2, 0.95, 0, "SPI bus", C.green);
  segment(s, 6.45, 4.32, 9.75, 4.32, C.teal, 1.8);
  segment(s, 9.75, 4.32, 9.75, 3.32, C.teal, 1.8);
  arrow(s, 9.75, 3.32, 0.35, 0, "", C.teal);
  s.addText("data", { x: 7.65, y: 4.15, w: 0.75, h: 0.22, fontSize: 9.5, bold: true, color: C.teal, align: "center", fill: { color: "F7F9FC", transparency: 8 }, margin: 0 });
  arrow(s, 5.2, 3.65, 0, -0.75, "control", C.blue);
  callout(s, "State the command scope: per-die, broadcast, serialized, or interleaved.", 7.25, 4.65, 4.95, 0.72);
  s.addText("Solid = command/data path   •   Dashed = optional/asynchronous", { x: 0.9, y: 6.15, w: 5.8, h: 0.25, fontSize: 9.5, color: C.gray, margin: 0 });
}

function segment(slide, x1, y1, x2, y2, color = C.blue, width = 1.6) {
  slide.addShape(pptx.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width, beginArrowType: "none", endArrowType: "none" } });
}

// Slide 2: timing diagram.
{
  const s = pptx.addSlide();
  s.background = { color: "FFFFFF" };
  addTitle(s, "SPI Command Timing", "Shared axis • aligned transitions • explicit intervals");
  const x0 = 2.0, x1 = 12.45, top = 1.35, row = 0.93;
  for (let i = 0; i <= 10; i++) {
    const x = x0 + (x1 - x0) * i / 10;
    segment(s, x, top - 0.18, x, top + row * 4.15, "D9E1E8", 0.6);
    s.addText(`${i * 10}`, { x: x - 0.16, y: top - 0.45, w: 0.32, h: 0.18, fontSize: 8.5, color: C.gray, align: "center", margin: 0 });
  }
  s.addText("time (ns)", { x: 0.95, y: top - 0.45, w: 0.8, h: 0.18, fontSize: 9, color: C.gray, align: "right", margin: 0 });
  const labels = ["CS#", "CLK", "IO0 / MOSI", "BUSY#"];
  labels.forEach((label, i) => s.addText(label, { x: 0.55, y: top + i * row - 0.02, w: 1.2, h: 0.28, fontSize: 12, bold: true, color: C.ink, align: "right", margin: 0 }));
  const hi = 0.06, lo = 0.38;
  // CS#
  segment(s, x0, top + hi, 2.75, top + hi); segment(s, 2.75, top + hi, 2.75, top + lo); segment(s, 2.75, top + lo, 11.2, top + lo); segment(s, 11.2, top + lo, 11.2, top + hi); segment(s, 11.2, top + hi, x1, top + hi);
  // CLK
  const cy = top + row; let cx = 2.75; const step = 0.52;
  segment(s, x0, cy + lo, cx, cy + lo);
  for (let i = 0; i < 16; i++) { segment(s, cx, cy + lo, cx, cy + hi); segment(s, cx, cy + hi, cx + step / 2, cy + hi); segment(s, cx + step / 2, cy + hi, cx + step / 2, cy + lo); segment(s, cx + step / 2, cy + lo, cx + step, cy + lo); cx += step; }
  segment(s, cx, cy + lo, x1, cy + lo);
  // IO0 data boxes
  const dy = top + row * 2;
  segment(s, x0, dy + lo, 2.75, dy + lo);
  ["06h", "A23:A16", "A15:A8", "A7:A0"].forEach((label, i) => {
    const bx = 2.75 + i * 2.08;
    s.addShape(pptx.ShapeType.rect, { x: bx, y: dy - 0.03, w: 2.08, h: 0.45, fill: { color: i === 0 ? "EAF2F8" : "ECF7F4" }, line: { color: i === 0 ? C.blue : C.teal, width: 1 } });
    s.addText(label, { x: bx, y: dy + 0.07, w: 2.08, h: 0.18, fontSize: 10.5, bold: true, align: "center", color: C.ink, margin: 0 });
  });
  segment(s, 11.07, dy + lo, x1, dy + lo);
  // BUSY#
  const by = top + row * 3;
  segment(s, x0, by + hi, 11.2, by + hi); segment(s, 11.2, by + hi, 11.2, by + lo); segment(s, 11.2, by + lo, x1, by + lo);
  s.addShape(pptx.ShapeType.rect, { x: 2.75, y: top - 0.18, w: 0.52, h: row * 3.92, fill: { color: "FFF0CC", transparency: 55 }, line: { color: C.amber, transparency: 100 } });
  s.addText("tCSS", { x: 2.72, y: 5.25, w: 0.65, h: 0.22, fontSize: 10, bold: true, color: C.amber, align: "center", margin: 0 });
  callout(s, "Conditions: 3.0 V, 25 °C, Mode 0. Replace example values with sourced min/typ/max limits.", 2.0, 5.75, 10.45, 0.62, C.blue);
}

// Slide 3: comparison/trade study.
{
  const s = pptx.addSlide();
  s.background = { color: "F7F9FC" };
  addTitle(s, "Erase Strategy Trade Study", "Exact table + magnitude chart + decision implication");
  const rows = [
    ["Method", "Typical", "Guardband", "Best use"],
    ["4 KB loop", "100 units", "120 units", "Sparse updates"],
    ["64 KB loop", "25 units", "30 units", "Bulk erase"],
    ["Chip Erase", "14 units", "18 units", "Whole device"],
  ];
  s.addTable(rows, { x: 0.65, y: 1.25, w: 5.9, h: 2.45, border: { color: "AAB7C4", width: 1 }, fill: "FFFFFF", color: C.ink, fontFace: "Aptos", fontSize: 12, margin: 0.08, rowH: 0.52, bold: false, autoFit: false, colW: [1.55, 1.2, 1.2, 1.95] });
  s.addText("Illustrative normalized erase time", { x: 7.0, y: 1.2, w: 4.9, h: 0.28, fontSize: 14, bold: true, color: C.ink, margin: 0 });
  const data = [{ name: "Typical", labels: ["4 KB loop", "64 KB loop", "Chip Erase"], values: [100, 25, 14] }];
  s.addChart(pptx.ChartType.bar, data, { x: 6.95, y: 1.55, w: 5.55, h: 3.6, catAxisLabelFontSize: 10, valAxisLabelFontSize: 9, valAxisMinVal: 0, valAxisMaxVal: 110, valGridLine: { color: "D8E0E7", width: 1 }, showLegend: false, showTitle: false, chartColors: [C.blue], showValue: true, dataLabelPosition: "outEnd", showCatName: false, showValAxisTitle: false, showCatAxisTitle: false, border: { color: "C8D3DE", width: 1 } });
  callout(s, "Decision: Chip Erase is fastest for a full-device reset; use block/sector loops only when preservation or locality matters.", 0.75, 4.55, 5.65, 1.0, C.green);
  s.addText("Illustrative values only. Replace them with sourced data and label calculated or margin-adjusted values separately.", { x: 0.75, y: 6.15, w: 10.6, h: 0.27, fontSize: 10, color: C.gray, margin: 0 });
}

const outputArg = process.argv.find((arg) => arg.startsWith("--output="));
const output = outputArg ? outputArg.slice("--output=".length) : "technical-diagram-demo.pptx";
await pptx.writeFile({ fileName: output });
console.log(output);
