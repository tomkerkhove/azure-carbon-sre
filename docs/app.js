"use strict";

const defaults = {
  sourceUrl: "tomkerkhove/azure-carbon-sre",
  pathInRepo: "plugins/azure-carbon-sre",
  pluginName: "Azure Carbon SRE",
};

const query = new URLSearchParams(window.location.search);

function queryValue(name, fallback, maxLength, allowEmpty = false) {
  const parameter = query.get(name);
  if (parameter === null) {
    return fallback;
  }

  const value = parameter.trim();
  return value.length <= maxLength && (allowEmpty || value) ? value : fallback;
}

const plugin = {
  sourceUrl: queryValue("sourceUrl", defaults.sourceUrl, 500),
  pathInRepo: queryValue("pathInRepo", defaults.pathInRepo, 500, true),
  pluginName: queryValue("pluginName", defaults.pluginName, 80),
};

const pluginName = document.getElementById("plugin-name");
const sourceUrl = document.getElementById("source-url");
const pathInRepo = document.getElementById("path-in-repo");
const badgeMarkdown = document.getElementById("badge-markdown");
const status = document.getElementById("status");

pluginName.textContent = plugin.pluginName;
sourceUrl.value = plugin.sourceUrl;
pathInRepo.value = plugin.pathInRepo;
document.title = `Install ${plugin.pluginName} on Azure SRE Agent`;

const installQuery = new URLSearchParams(plugin);
const installUrl = `${window.location.origin}${window.location.pathname}?${installQuery}`;
const badgeImage =
  "https://img.shields.io/badge/Install%20on-Azure%20SRE%20Agent-0078D4" +
  "?logo=microsoftazure&logoColor=white";
badgeMarkdown.value =
  `[![Install on Azure SRE Agent](${badgeImage})](${installUrl})`;

async function copy(value, label) {
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }

  status.textContent = `${label} copied.`;
}

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.getElementById(button.dataset.copy);
    void copy(target.value, target.labels[0].textContent);
  });
});

document.getElementById("agent-form").addEventListener("submit", (event) => {
  event.preventDefault();

  const endpointValue = document.getElementById("agent-endpoint").value.trim();
  let endpoint;

  try {
    endpoint = new URL(endpointValue);
    if (
      endpoint.protocol !== "https:" ||
      endpoint.username ||
      endpoint.password ||
      endpoint.search ||
      endpoint.hash
    ) {
      throw new Error("invalid endpoint");
    }
  } catch {
    status.textContent = "Enter a valid HTTPS agent endpoint.";
    return;
  }

  window.open(endpoint, "_blank", "noopener,noreferrer");
  status.textContent =
    "Agent opened. Go to Builder > Plugins, select Install from URL, and use the values in step 2.";
});
