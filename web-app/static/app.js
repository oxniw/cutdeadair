// ==============================================================================
// CUTDEADAIR — WEB APPLICATION JAVASCRIPT CONTROLLER
// Handles file upload, parameter controls, pre-flight scan, and progress polling
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {
  // Optional backend API base URL (empty string for same-origin or proxy)
  const API_BASE = window.CUTDEADAIR_API_BASE || "";

  // State
  let currentJobId = null;
  let currentFile = null;
  let pollInterval = null;

  // DOM Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const fileInfo = document.getElementById("file-info");
  const fileBadge = document.getElementById("file-badge");
  const fileName = document.getElementById("file-name");
  const fileSize = document.getElementById("file-size");
  const removeFileBtn = document.getElementById("remove-file-btn");
  const uploadProgress = document.getElementById("upload-progress-container");
  const uploadFill = document.getElementById("upload-progress-fill");

  const presetSelect = document.getElementById("preset-select");
  const presetDesc = document.getElementById("preset-desc");

  const thresholdSlider = document.getElementById("threshold-slider");
  const thresholdVal = document.getElementById("threshold-val");
  const minDurationSlider = document.getElementById("min-duration-slider");
  const minDurationVal = document.getElementById("min-duration-val");
  const marginSlider = document.getElementById("margin-slider");
  const marginVal = document.getElementById("margin-val");
  const targetPauseSlider = document.getElementById("target-pause-slider");
  const targetPauseVal = document.getElementById("target-pause-val");
  const targetPauseGroup = document.getElementById("target-pause-group");
  const modeRadios = document.querySelectorAll('input[name="cut-mode"]');

  const videoModeCheck = document.getElementById("video-mode-check");
  const extractAudioCheck = document.getElementById("extract-audio-check");
  const videoQualitySelect = document.getElementById("video-quality-select");

  const scanBtn = document.getElementById("scan-btn");
  const processBtn = document.getElementById("process-btn");

  const statOrig = document.getElementById("stat-orig");
  const statSilence = document.getElementById("stat-silence");
  const statEst = document.getElementById("stat-est");
  const statSaved = document.getElementById("stat-saved");
  const statMeanPower = document.getElementById("stat-mean-power");
  const statMaxPower = document.getElementById("stat-max-power");
  const statMediaType = document.getElementById("stat-media-type");
  const statProcessMode = document.getElementById("stat-process-mode");

  const renderProgressBox = document.getElementById("render-progress-container");
  const renderProgressFill = document.getElementById("render-progress-fill");
  const statusText = document.getElementById("status-text");
  const progressPct = document.getElementById("progress-pct");

  const downloadBox = document.getElementById("download-box");
  const downloadBtn = document.getElementById("download-btn");
  const resultSummary = document.getElementById("result-summary");

  // Presets Dictionary
  const PRESETS = {
    "Podcast / Voiceover": {
      desc: "Natural speech cadence, keeps breaths, shortens pauses to 0.3s.",
      threshold: -32.0,
      minDuration: 0.60,
      margin: 0.15,
      targetPause: 0.30,
      mode: "shorten",
    },
    "Aggressive Cut": {
      desc: "Fast video editing, cuts silence completely with tight padding.",
      threshold: -28.0,
      minDuration: 0.40,
      margin: 0.08,
      targetPause: 0.15,
      mode: "cut",
    },
    "Subtle Breath Retain": {
      desc: "Gentle narration trimming for audiobooks, preserving pace.",
      threshold: -38.0,
      minDuration: 1.00,
      margin: 0.25,
      targetPause: 0.45,
      mode: "shorten",
    },
  };

  // Slider Event Listeners
  thresholdSlider.addEventListener("input", (e) => {
    thresholdVal.textContent = `${parseFloat(e.target.value).toFixed(1)} dB`;
    markCustomPreset();
  });

  minDurationSlider.addEventListener("input", (e) => {
    minDurationVal.textContent = `${parseFloat(e.target.value).toFixed(2)} s`;
    markCustomPreset();
  });

  marginSlider.addEventListener("input", (e) => {
    marginVal.textContent = `${parseFloat(e.target.value).toFixed(2)} s`;
    markCustomPreset();
  });

  targetPauseSlider.addEventListener("input", (e) => {
    targetPauseVal.textContent = `${parseFloat(e.target.value).toFixed(2)} s`;
    markCustomPreset();
  });

  modeRadios.forEach((r) => {
    r.addEventListener("change", () => {
      syncModeVisibility();
      markCustomPreset();
    });
  });

  presetSelect.addEventListener("change", (e) => {
    const p = PRESETS[e.target.value];
    if (p) {
      presetDesc.textContent = p.desc;
      thresholdSlider.value = p.threshold;
      thresholdVal.textContent = `${p.threshold.toFixed(1)} dB`;

      minDurationSlider.value = p.minDuration;
      minDurationVal.textContent = `${p.minDuration.toFixed(2)} s`;

      marginSlider.value = p.margin;
      marginVal.textContent = `${p.margin.toFixed(2)} s`;

      targetPauseSlider.value = p.targetPause;
      targetPauseVal.textContent = `${p.targetPause.toFixed(2)} s`;

      document.querySelector(`input[name="cut-mode"][value="${p.mode}"]`).checked = true;
      syncModeVisibility();
    }
  });

  function markCustomPreset() {
    if (presetSelect.value !== "Custom") {
      presetSelect.value = "Custom";
      presetDesc.textContent = "Custom user parameters.";
    }
  }

  function syncModeVisibility() {
    const mode = document.querySelector('input[name="cut-mode"]:checked').value;
    if (mode === "shorten") {
      targetPauseGroup.classList.remove("hidden");
    } else {
      targetPauseGroup.classList.add("hidden");
    }
  }

  // Drag and Drop Handling
  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  removeFileBtn.addEventListener("click", resetUpload);

  function resetUpload() {
    if (currentJobId) {
      fetch(`${API_BASE}/api/job/${currentJobId}`, { method: "DELETE" }).catch(() => {});
    }
    currentJobId = null;
    currentFile = null;
    if (pollInterval) clearInterval(pollInterval);

    fileInput.value = "";
    fileInfo.classList.add("hidden");
    dropzone.classList.remove("hidden");
    uploadProgress.classList.add("hidden");
    uploadFill.style.width = "0%";

    scanBtn.disabled = true;
    processBtn.disabled = true;
    renderProgressBox.classList.add("hidden");
    downloadBox.classList.add("hidden");

    resetStats();
  }

  function resetStats() {
    statOrig.textContent = "—";
    statSilence.textContent = "—";
    statEst.textContent = "—";
    statSaved.textContent = "—";
    statMeanPower.textContent = "—";
    statMaxPower.textContent = "—";
    statMediaType.textContent = "—";
    statProcessMode.textContent = "—";
  }

  function formatTime(sec) {
    if (sec == null || isNaN(sec)) return "—";
    const totalSecs = Math.round(sec);
    const m = Math.floor(totalSecs / 60);
    const s = totalSecs % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  function handleFileSelected(file) {
    currentFile = file;
    const isVid = file.type.startsWith("video/") || /\.(mp4|mkv|mov|avi|webm|flv|ts)$/i.test(file.name);

    fileName.textContent = file.name;
    fileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    fileBadge.textContent = isVid ? "VIDEO" : "AUDIO";

    dropzone.classList.add("hidden");
    fileInfo.classList.remove("hidden");
    uploadProgress.classList.remove("hidden");
    uploadFill.style.width = "10%";

    // Upload file via streaming octet-stream
    uploadFile(file);
  }

  function uploadFile(file) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/api/upload`, true);
    xhr.setRequestHeader("Content-Type", "application/octet-stream");
    xhr.setRequestHeader("X-Filename", encodeURIComponent(file.name));

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 90);
        uploadFill.style.width = `${pct}%`;
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        const resp = JSON.parse(xhr.responseText);
        currentJobId = resp.job_id;
        uploadFill.style.width = "100%";
        setTimeout(() => {
          uploadProgress.classList.add("hidden");
        }, 300);

        scanBtn.disabled = false;
        processBtn.disabled = false;
      } else {
        alert(`Upload failed: ${xhr.responseText}`);
        resetUpload();
      }
    };

    xhr.onerror = () => {
      alert("Network error during upload.");
      resetUpload();
    };

    xhr.send(file);
  }

  function collectSettings() {
    const mode = document.querySelector('input[name="cut-mode"]:checked').value;
    return {
      threshold_db: parseFloat(thresholdSlider.value),
      min_silence_duration: parseFloat(minDurationSlider.value),
      margin_padding: parseFloat(marginSlider.value),
      target_pause: parseFloat(targetPauseSlider.value),
      mode: mode,
      is_video_mode: videoModeCheck.checked,
      export_audio_only: extractAudioCheck.checked,
      video_quality: videoQualitySelect.value,
    };
  }

  // Pre-flight Scan
  scanBtn.addEventListener("click", () => {
    if (!currentJobId) return;

    scanBtn.disabled = true;
    scanBtn.textContent = "SCANNING...";

    fetch(`${API_BASE}/api/scan/${currentJobId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectSettings()),
    })
      .then((res) => res.json())
      .then((data) => {
        scanBtn.disabled = false;
        scanBtn.textContent = "SCAN MEDIA";

        if (data.error) {
          alert(`Scan error: ${data.error}`);
          return;
        }

        statOrig.textContent = formatTime(data.total_duration);
        statSilence.textContent = `${formatTime(data.total_silence_duration)} (${data.silence_count} cuts)`;
        statEst.textContent = formatTime(data.estimated_output_duration);
        statSaved.textContent = `${formatTime(data.time_saved)} (-${data.percentage_saved.toFixed(1)}%)`;

        statMeanPower.textContent = data.mean_power_db != null ? `${data.mean_power_db.toFixed(1)} dB` : "—";
        statMaxPower.textContent = data.max_power_db != null ? `${data.max_power_db.toFixed(1)} dB` : "—";

        statMediaType.textContent = data.is_video ? "[VIDEO] Video Media" : "[AUDIO] Audio Media";
        statProcessMode.textContent = data.is_video && extractAudioCheck.checked ? "Extract Audio (.mp3)" : (data.is_video ? "Sync Video + Audio" : "Audio Cut");
      })
      .catch((err) => {
        scanBtn.disabled = false;
        scanBtn.textContent = "SCAN MEDIA";
        alert(`Request failed: ${err.message}`);
      });
  });

  // Start Processing
  processBtn.addEventListener("click", () => {
    if (!currentJobId) return;

    processBtn.disabled = true;
    scanBtn.disabled = true;
    downloadBox.classList.add("hidden");
    renderProgressBox.classList.remove("hidden");
    renderProgressFill.style.width = "0%";
    statusText.textContent = "Starting render pipeline...";
    progressPct.textContent = "0%";

    fetch(`${API_BASE}/api/process/${currentJobId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectSettings()),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          alert(`Processing error: ${data.error}`);
          processBtn.disabled = false;
          scanBtn.disabled = false;
          renderProgressBox.classList.add("hidden");
          return;
        }
        startPolling();
      })
      .catch((err) => {
        alert(`Processing trigger failed: ${err.message}`);
        processBtn.disabled = false;
        scanBtn.disabled = false;
        renderProgressBox.classList.add("hidden");
      });
  });

  function startPolling() {
    if (pollInterval) clearInterval(pollInterval);

    pollInterval = setInterval(() => {
      if (!currentJobId) {
        clearInterval(pollInterval);
        return;
      }

      fetch(`${API_BASE}/api/status/${currentJobId}`)
        .then((res) => res.json())
        .then((job) => {
          if (!job) return;

          const pct = Math.round((job.progress || 0) * 100);
          renderProgressFill.style.width = `${pct}%`;
          progressPct.textContent = `${pct}%`;
          statusText.textContent = job.message || "Working...";

          if (job.status === "done") {
            clearInterval(pollInterval);
            renderProgressFill.style.width = "100%";
            progressPct.textContent = "100%";
            statusText.textContent = "Complete!";

            processBtn.disabled = false;
            scanBtn.disabled = false;

            downloadBtn.href = `${API_BASE}/api/download/${currentJobId}`;
            resultSummary.textContent = `Success! Saved ${formatTime(job.summary?.time_saved)} of dead air.`;
            downloadBox.classList.remove("hidden");
          } else if (job.status === "failed") {
            clearInterval(pollInterval);
            processBtn.disabled = false;
            scanBtn.disabled = false;
            statusText.textContent = `Failed: ${job.error || "Unknown error"}`;
            alert(`Process failed: ${job.error}`);
          }
        })
        .catch(() => {});
    }, 800);
  }
});
