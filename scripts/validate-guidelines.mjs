#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { load } from "js-yaml";

const repoRoot = process.cwd();
const indexPath = path.join(repoRoot, "guidelines-index.yaml");

const errors = [];
const warnings = [];

if (!fs.existsSync(indexPath)) {
  console.error("ERROR: guidelines-index.yaml not found.");
  process.exit(1);
}

const indexText = fs.readFileSync(indexPath, "utf8");
let indexData = null;

try {
  indexData = load(indexText);
} catch (e) {
  console.error(`ERROR: Invalid YAML in guidelines-index.yaml: ${e.message}`);
  process.exit(1);
}

if (!indexData || typeof indexData !== "object") {
  console.error("ERROR: guidelines-index.yaml is empty or invalid.");
  process.exit(1);
}

const normalizeRepoPath = (p) => String(p).trim().replace(/\\/g, "/").replace(/^\.\//, "");

const requiredMetadataFields = Array.isArray(indexData.validation?.required_metadata_fields)
  ? indexData.validation.required_metadata_fields.map((x) => String(x))
  : ["Version", "Owner", "Last Updated"];

if (!Array.isArray(indexData.validation?.required_metadata_fields)) {
  warnings.push("validation.required_metadata_fields not found. Using fallback fields.");
}

const domains = indexData.domains && typeof indexData.domains === "object" ? indexData.domains : {};
if (Object.keys(domains).length === 0) {
  errors.push("No domains defined in guidelines-index.yaml.");
}

const indexedFiles = new Map();
const normativeFiles = new Set();
const referencedPaths = new Set();
const scanRoots = new Set();

for (const [domainName, domainDef] of Object.entries(domains)) {
  const domainPath = domainDef?.path;
  if (!domainPath || typeof domainPath !== "string") {
    errors.push(`Domain '${domainName}' is missing a valid path.`);
    continue;
  }

  const normalizedDomainPath = normalizeRepoPath(domainPath);
  scanRoots.add(normalizedDomainPath);

  const absDomainPath = path.join(repoRoot, normalizedDomainPath);
  if (!fs.existsSync(absDomainPath)) {
    errors.push(`Missing domain directory: ${normalizedDomainPath}`);
  }

  const files = Array.isArray(domainDef?.files) ? domainDef.files : [];
  if (files.length === 0) {
    warnings.push(`Domain '${domainName}' has no indexed files.`);
  }

  for (const fileDef of files) {
    const rawPath = fileDef?.path;
    if (!rawPath || typeof rawPath !== "string") {
      errors.push(`Domain '${domainName}' has a file entry with invalid path.`);
      continue;
    }

    const filePath = normalizeRepoPath(rawPath);
    indexedFiles.set(filePath, fileDef?.kind || "unknown");

    const absPath = path.join(repoRoot, filePath);
    if (!fs.existsSync(absPath)) {
      errors.push(`Missing indexed file: ${filePath}`);
      continue;
    }

    if (fileDef?.kind === "normative") {
      normativeFiles.add(filePath);
    }

    if (Array.isArray(fileDef?.depends_on)) {
      for (const dep of fileDef.depends_on) {
        if (typeof dep === "string" && dep.trim().length > 0) {
          referencedPaths.add(normalizeRepoPath(dep));
        }
      }
    }
  }
}

if (normativeFiles.size === 0) {
  errors.push("No normative files found in guidelines-index.yaml.");
}

const onChange = indexData.update_rules?.on_change;
if (onChange && typeof onChange === "object") {
  for (const [sourcePath, ruleDef] of Object.entries(onChange)) {
    referencedPaths.add(normalizeRepoPath(sourcePath));
    if (Array.isArray(ruleDef?.must_review)) {
      for (const targetPath of ruleDef.must_review) {
        if (typeof targetPath === "string" && targetPath.trim().length > 0) {
          referencedPaths.add(normalizeRepoPath(targetPath));
        }
      }
    }
  }
}

for (const filePath of normativeFiles) {
  const absPath = path.join(repoRoot, filePath);
  if (!fs.existsSync(absPath)) {
    continue;
  }

  const content = fs.readFileSync(absPath, "utf8");
  for (const field of requiredMetadataFields) {
    const escaped = String(field).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`^${escaped}:\\s*\\S.*$`, "m");
    if (!re.test(content)) {
      errors.push(`${filePath} missing metadata field: ${field}`);
    }
  }
}

for (const refPath of referencedPaths) {
  const absPath = path.join(repoRoot, refPath);
  if (!fs.existsSync(absPath)) {
    errors.push(`Missing referenced dependency file: ${refPath}`);
  }
}

const walkMarkdown = (absDir, relDir, out) => {
  if (!fs.existsSync(absDir)) return;
  const entries = fs.readdirSync(absDir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.isDirectory() && (entry.name === ".git" || entry.name === "node_modules")) {
      continue;
    }
    const nextAbs = path.join(absDir, entry.name);
    const nextRel = relDir ? `${relDir}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      walkMarkdown(nextAbs, nextRel, out);
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith(".md")) {
      out.push(normalizeRepoPath(nextRel));
    }
  }
};

const allMd = [];
for (const root of scanRoots) {
  const absRoot = path.join(repoRoot, root);
  walkMarkdown(absRoot, root, allMd);
}

for (const mdPath of allMd) {
  if (!indexedFiles.has(mdPath) && !mdPath.endsWith("/README.md")) {
    warnings.push(`Markdown file not indexed in guidelines-index.yaml: ${mdPath}`);
  }
}

const phaseModel = indexData.phase_model;
if (phaseModel) {
  const phaseIndexFile = phaseModel.index_file;
  if (!phaseIndexFile || typeof phaseIndexFile !== "string") {
    errors.push("phase_model.index_file must be a valid file path.");
  } else {
    const normalizedPhaseIndexFile = normalizeRepoPath(phaseIndexFile);
    if (!fs.existsSync(path.join(repoRoot, normalizedPhaseIndexFile))) {
      errors.push(`Missing phase index file: ${normalizedPhaseIndexFile}`);
    }
  }

  if (!Array.isArray(phaseModel.phases) || phaseModel.phases.length === 0) {
    errors.push("phase_model.phases must be a non-empty array.");
  } else {
    for (const phaseDef of phaseModel.phases) {
      const phaseId = phaseDef?.id;
      const phaseRoles = phaseDef?.primary_roles;

      if (!phaseId || typeof phaseId !== "string") {
        errors.push("A phase_model entry is missing id.");
      }

      if (!Array.isArray(phaseRoles) || phaseRoles.length === 0) {
        errors.push(`Phase '${phaseId || "unknown"}' must define non-empty primary_roles.`);
      }
    }
  }

  if (!Array.isArray(phaseModel.roles) || phaseModel.roles.length === 0) {
    warnings.push("phase_model.roles is missing or empty.");
  } else if (Array.isArray(phaseModel.phases)) {
    const allowedRoles = new Set(phaseModel.roles.map((r) => String(r)));
    for (const phaseDef of phaseModel.phases) {
      const phaseId = phaseDef?.id || "unknown";
      const phaseRoles = Array.isArray(phaseDef?.primary_roles) ? phaseDef.primary_roles : [];
      for (const role of phaseRoles) {
        if (!allowedRoles.has(String(role))) {
          errors.push(`Phase '${phaseId}' references unknown role '${role}'.`);
        }
      }
    }
  }
}

if (warnings.length > 0) {
  for (const w of warnings) {
    console.warn(`WARN: ${w}`);
  }
}

if (errors.length > 0) {
  for (const e of errors) {
    console.error(`ERROR: ${e}`);
  }
  process.exit(1);
}

console.log(
  `OK: validated ${normativeFiles.size} normative files, ${indexedFiles.size} indexed files, ${referencedPaths.size} references, ${phaseModel?.phases?.length || 0} phases.`
);
