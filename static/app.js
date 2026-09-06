document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const projectTitleInput = document.getElementById('project-title-input');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectedFileName = document.getElementById('selected-file-name');
    const browseBtn = document.querySelector('.browse-btn');
    const btnRunAudit = document.getElementById('btn-run-audit');
    const sampleItems = document.querySelectorAll('.sample-item');
    
    // Judge VIP Modal Elements
    const judgeStatusPill = document.getElementById('judge-status');
    const judgeStatusText = document.getElementById('judge-status-text');
    const judgeDot = document.getElementById('judge-dot');
    const judgeModal = document.getElementById('judge-modal');
    const closeJudgeModal = document.getElementById('close-judge-modal');
    const cancelJudgeModal = document.getElementById('cancel-judge-modal');
    const saveJudgePasskey = document.getElementById('save-judge-passkey');
    const judgePasskeyInput = document.getElementById('judge-passkey-input');

    // Check URL parameters for judge access (?access=... or ?passcode=...)
    const urlParams = new URLSearchParams(window.location.search);
    const queryAccessKey = urlParams.get('access') || urlParams.get('passcode') || urlParams.get('key');
    if (queryAccessKey) {
        localStorage.setItem('cineclear_judge_passkey', queryAccessKey);
    } else if (!localStorage.getItem('cineclear_judge_passkey')) {
        // Auto-set default judge token for hackathon testing
        localStorage.setItem('cineclear_judge_passkey', 'cineclear-judge-2026');
    }

    function getJudgePasskey() {
        return localStorage.getItem('cineclear_judge_passkey') || 'cineclear-judge-2026';
    }

    function isJudgeAuthActive() {
        return Boolean(localStorage.getItem('cineclear_judge_passkey'));
    }

    function updateJudgeUI() {
        if (!judgeStatusPill) return;
        if (isJudgeAuthActive()) {
            judgeStatusPill.classList.add('active-vip');
            judgeStatusPill.classList.remove('locked-guest');
            if (judgeDot) judgeDot.className = 'pulse-dot active';
            if (judgeStatusText) judgeStatusText.textContent = '⚖️ Judge VIP Active';
        } else {
            judgeStatusPill.classList.remove('active-vip');
            judgeStatusPill.classList.add('locked-guest');
            if (judgeDot) judgeDot.className = 'pulse-dot';
            if (judgeStatusText) judgeStatusText.textContent = '🔓 Unlock Judge Pass';
        }
    }
    updateJudgeUI();

    if (judgeStatusPill) {
        judgeStatusPill.addEventListener('click', () => {
            if (judgePasskeyInput) {
                judgePasskeyInput.value = getJudgePasskey();
            }
            judgeModal.style.display = 'flex';
        });
    }

    if (closeJudgeModal) {
        closeJudgeModal.addEventListener('click', () => judgeModal.style.display = 'none');
    }
    if (cancelJudgeModal) {
        cancelJudgeModal.addEventListener('click', () => judgeModal.style.display = 'none');
    }
    if (saveJudgePasskey) {
        saveJudgePasskey.addEventListener('click', () => {
            const key = judgePasskeyInput.value.trim() || 'cineclear-judge-2026';
            localStorage.setItem('cineclear_judge_passkey', key);
            updateJudgeUI();
            judgeModal.style.display = 'none';
        });
    }
    
    // Views
    const processingView = document.getElementById('processing-view');
    const resultsView = document.getElementById('results-view');
    const processingStepLabel = document.getElementById('processing-step-label');
    
    // Result elements
    const reportProjectTitle = document.getElementById('report-project-title');
    const reportMetaInfo = document.getElementById('report-meta-info');
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    const btnExportEdl = document.getElementById('btn-export-edl');
    const btnNewAudit = document.getElementById('btn-new-audit');
    const flagsContainer = document.getElementById('flags-container');
    const filterTabs = document.querySelectorAll('.filter-tab');

    // Visual Viewport & BBox elements
    const mediaViewportBox = document.getElementById('media-viewport-box');
    const previewImage = document.getElementById('preview-image');
    const bboxOverlay = document.getElementById('bbox-overlay');

    // Metrics
    const metricTotal = document.getElementById('metric-total');
    const metricCritical = document.getElementById('metric-critical');
    const metricHigh = document.getElementById('metric-high');
    const metricMedium = document.getElementById('metric-medium');
    const metricLow = document.getElementById('metric-low');
    
    const countAll = document.getElementById('count-all');
    const countCritical = document.getElementById('count-critical');
    const countHigh = document.getElementById('count-high');
    const countMedium = document.getElementById('count-medium');
    const countLow = document.getElementById('count-low');

    // State
    let selectedFile = null;
    let selectedSampleId = 'sample-photo';
    let currentReport = null;
    let activeFilter = 'ALL';
    let currentImageSrc = null;

    // Sample selection
    sampleItems.forEach(item => {
        item.addEventListener('click', (e) => {
            sampleItems.forEach(s => s.classList.remove('active'));
            item.classList.add('active');
            
            selectedSampleId = item.getAttribute('data-sample');
            selectedFile = null;
            selectedFileName.classList.add('hidden');
            selectedFileName.textContent = '';

            const titles = {
                'sample-photo': 'Hero Living Room (Production Set Still)',
                'sample-screenplay': 'Feature Screenplay Excerpt (PDF)',
                'sample-script-txt': 'Screenplay Scene 1-3 (Text)'
            };
            if (titles[selectedSampleId]) {
                projectTitleInput.value = titles[selectedSampleId];
            }

            // 1-Click execution: selecting a sample runs the audit immediately!
            btnRunAudit.click();
        });
    });

    // File selection
    if (browseBtn) {
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files && fileInput.files[0]) {
            handleFileSelection(fileInput.files[0]);
        }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    function handleFileSelection(file) {
        selectedFile = file;
        selectedSampleId = null;
        sampleItems.forEach(s => s.classList.remove('active'));
        selectedFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        selectedFileName.classList.remove('hidden');
    }

    // Run Audit
    btnRunAudit.addEventListener('click', async () => {
        const projectTitle = projectTitleInput.value.trim() || 'Untitled Production';
        
        // Setup image preview source for visualization
        const isImg = selectedFile && (selectedFile.type.startsWith('image/') || /\.(jpe?g|png|webp|bmp|gif)$/i.test(selectedFile.name));
        if (isImg) {
            currentImageSrc = URL.createObjectURL(selectedFile);
        } else if (selectedSampleId === 'sample-photo') {
            currentImageSrc = '/sample_media/sample_set_photo.jpg';
        } else {
            currentImageSrc = null;
        }

        // Show Processing View
        processingView.classList.remove('hidden');
        resultsView.classList.add('hidden');
        window.scrollTo({ top: processingView.offsetTop - 80, behavior: 'smooth' });

        resetPipelineProgress();

        try {
            const formData = new FormData();
            formData.append('project_title', projectTitle);
            
            if (selectedFile) {
                formData.append('file', selectedFile);
                formData.append('media_type', 'auto');
            } else if (selectedSampleId) {
                formData.append('sample_id', selectedSampleId);
                formData.append('media_type', 'auto');
            } else {
                formData.append('sample_id', 'sample-photo');
            }

            const headers = {};
            const judgeKey = getJudgePasskey();
            if (judgeKey) {
                headers['X-Judge-Access'] = judgeKey;
            }

            const response = await fetch('/api/audit/stream', {
                method: 'POST',
                headers: headers,
                body: formData
            });

            if (!response.ok) {
                if (response.status === 401) {
                    processingView.classList.add('hidden');
                    judgeModal.style.display = 'flex';
                    if (judgePasskeyInput) judgePasskeyInput.focus();
                    return;
                }
                let detail = 'Audit processing failed';
                try {
                    const errData = await response.json();
                    detail = errData.detail || detail;
                } catch (_) {
                    detail = (await response.text()) || detail;
                }
                throw new Error(detail);
            }

            currentReport = await consumeAuditStream(response);
            
            completePipelineProgress(() => {
                renderResults(currentReport);
                processingView.classList.add('hidden');
                resultsView.classList.remove('hidden');
                window.scrollTo({ top: resultsView.offsetTop - 80, behavior: 'smooth' });
            });

        } catch (error) {
            console.error('Audit failed:', error);
            alert(`Clearance Audit Error: ${error.message}`);
            processingView.classList.add('hidden');
        }
    });

    function pipelineEls() {
        return {
            steps: [
                document.getElementById('step-1'),
                document.getElementById('step-2'),
                document.getElementById('step-3'),
                document.getElementById('step-4')
            ],
            lines: document.querySelectorAll('.step-line'),
            bar: document.getElementById('pipeline-progress-bar')
        };
    }

    function resetPipelineProgress() {
        const { steps, lines, bar } = pipelineEls();
        steps.forEach((el, idx) => {
            if (!el) return;
            el.className = 'step-item';
            const c = el.querySelector('.step-circle');
            if (c) c.textContent = String(idx + 1);
        });
        lines.forEach(l => l.classList.remove('completed'));
        if (bar) bar.style.width = '4%';
        if (processingStepLabel) {
            processingStepLabel.textContent = 'Waiting for engine stage 1...';
        }
    }

    function applyEngineStage(evt) {
        const step = Number(evt.step) || 1;
        const idx = Math.max(0, Math.min(3, step - 1));
        const { steps, lines, bar } = pipelineEls();

        for (let j = 0; j < idx; j++) {
            if (steps[j]) {
                steps[j].className = 'step-item completed';
                const c = steps[j].querySelector('.step-circle');
                if (c) c.textContent = '✓';
            }
            if (lines[j]) lines[j].classList.add('completed');
        }

        if (evt.status === 'done') {
            if (steps[idx]) {
                steps[idx].className = 'step-item completed';
                const c = steps[idx].querySelector('.step-circle');
                if (c) c.textContent = '✓';
            }
            if (lines[idx]) lines[idx].classList.add('completed');
        } else if (steps[idx]) {
            steps[idx].className = 'step-item running';
        }

        if (bar && typeof evt.progress === 'number') {
            bar.style.width = `${Math.max(4, Math.min(100, evt.progress))}%`;
        }
        if (processingStepLabel && evt.label) {
            processingStepLabel.textContent = evt.label;
        }
    }

    async function consumeAuditStream(response) {
        if (!response.body || !response.body.getReader) {
            const fallback = await response.json();
            if (fallback && fallback.report) return fallback.report;
            return fallback;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let report = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed) continue;
                let evt;
                try {
                    evt = JSON.parse(trimmed);
                } catch (_) {
                    continue;
                }
                if (evt.type === 'stage') {
                    applyEngineStage(evt);
                } else if (evt.type === 'complete' && evt.report) {
                    report = evt.report;
                } else if (evt.type === 'error') {
                    throw new Error(evt.message || 'Audit processing failed');
                }
            }
        }

        if (!report && buffer.trim()) {
            try {
                const evt = JSON.parse(buffer.trim());
                if (evt.type === 'complete') report = evt.report;
                if (evt.type === 'error') throw new Error(evt.message || 'Audit processing failed');
            } catch (e) {
                if (e.message && e.message !== 'Audit processing failed') throw e;
            }
        }

        if (!report) {
            throw new Error('Audit stream ended without a report');
        }
        return report;
    }

    function completePipelineProgress(callback) {
        const { steps, lines, bar } = pipelineEls();
        steps.forEach(el => {
            if (!el) return;
            el.className = 'step-item completed';
            const c = el.querySelector('.step-circle');
            if (c) c.textContent = '✓';
        });
        lines.forEach(l => l.classList.add('completed'));
        if (bar) bar.style.width = '100%';
        if (processingStepLabel) {
            processingStepLabel.textContent = 'Clearance audit complete — rendering dossier...';
        }
        setTimeout(callback, 350);
    }

    // Render Results
    function renderResults(report) {
        reportProjectTitle.textContent = `${report.project_title} - E&O Clearance Dossier`;
        reportMetaInfo.textContent = `Analyzed Media: ${report.media_filename} | Media Type: ${report.media_type.toUpperCase()} | Generated: ${report.generated_at}`;

        // Counters
        metricTotal.textContent = report.total_flags;
        metricCritical.textContent = report.critical_count;
        metricHigh.textContent = report.high_count || 0;
        metricMedium.textContent = report.medium_count || 0;
        metricLow.textContent = report.low_count || 0;

        countAll.textContent = report.total_flags;
        countCritical.textContent = report.critical_count;
        countHigh.textContent = report.high_count || 0;
        countMedium.textContent = report.medium_count || 0;
        countLow.textContent = report.low_count || 0;

        // Populate Underwriter Insurability Assessment Banner
        const certBadge = document.getElementById('cert-status-badge');
        const certTitle = document.getElementById('cert-title');
        const certSubtitle = document.getElementById('cert-subtitle');
        const certScore = document.getElementById('cert-score-val');

        if (certBadge && certScore) {
            const critical = report.critical_count || 0;
            const high = report.high_count || 0;
            const medium = report.medium_count || 0;

            let score = 96;
            let status = 'CLEARED FOR WORLDWIDE DISTRIBUTION';
            let badgeClass = '';
            let subtitle = 'All identified background elements fall within statutory safe harbors (AWCPA / Rogers v. Grimaldi). Standard $5M E&O policy underwritable without exclusions.';

            if (critical > 0) {
                score = Math.max(38, 55 - critical * 8);
                status = 'UNINSURABLE // STATUTORY INJUNCTION RISK';
                badgeClass = 'danger';
                subtitle = `Detected ${critical} statutory invariant violation(s) (18 U.S.C. seal ban or unmasked phone PII). Emergency Greeking or Form-4A release required before underwriter binder sign-off.`;
            } else if (high > 0) {
                score = Math.max(72, 88 - high * 4);
                status = 'CONDITIONAL CLEARANCE // REMEDIATIONS REQUIRED';
                badgeClass = 'warning';
                subtitle = `Detected ${high} high-risk intellectual property item(s). Execute attached Form-4A artwork releases and VFX Greeking work orders to secure underwriter sign-off.`;
            } else if (medium > 0) {
                score = Math.max(88, 94 - medium * 2);
                status = 'SUBSTANTIAL CLEARANCE // MINOR REVIEW';
                badgeClass = 'warning';
                subtitle = `Detected ${medium} incidental brand/trademark element(s) with strong Fair Use defense. Counsel review recommended.`;
            }

            certBadge.className = `cert-status-badge ${badgeClass}`.trim();
            certBadge.textContent = status;
            certTitle.textContent = `${report.project_title} — E&O Underwriting Verdict`;
            certSubtitle.textContent = subtitle;
            certScore.textContent = `${score}%`;
            certScore.style.color = critical > 0 ? '#f87171' : high > 0 ? '#fbbf24' : '#34d399';
        }

        // Render Media Viewport with Bounding Boxes
        if (currentImageSrc && report.flags && report.flags.some(f => f.box_2d && f.box_2d.length === 4)) {
            mediaViewportBox.classList.remove('hidden');
            previewImage.src = currentImageSrc;
            previewImage.classList.remove('hidden');
            previewImage.onload = () => {
                renderBoundingBoxes(report.flags, previewImage, bboxOverlay);
            };
            renderBoundingBoxes(report.flags, previewImage, bboxOverlay);
        } else {
            mediaViewportBox.classList.add('hidden');
            previewImage.classList.add('hidden');
            bboxOverlay.innerHTML = '';
        }

        renderFlagsList(report.flags);
        renderRemediationPackage(report.remediation_package);
        setupBoxInteractivity();
    }

    // Render interactive Bounding Boxes over image
    function renderBoundingBoxes(flags, imgElement, svgOverlay) {
        svgOverlay.innerHTML = '';
        if (!flags || !imgElement || imgElement.classList.contains('hidden')) return;

        const riskColors = {
            'CRITICAL': '#dc2626',
            'HIGH': '#ea580c',
            'MEDIUM': '#d97706',
            'LOW': '#16a34a'
        };

        flags.forEach((flag, index) => {
            if (!flag.box_2d || flag.box_2d.length !== 4) return;
            const [ymin, xmin, ymax, xmax] = flag.box_2d;
            
            // Scale normalized 0-1000 coordinates to percentage
            const top = (ymin / 10).toFixed(2);
            const left = (xmin / 10).toFixed(2);
            const width = ((xmax - xmin) / 10).toFixed(2);
            const height = ((ymax - ymin) / 10).toFixed(2);
            const color = riskColors[flag.risk_level] || '#2563eb';

            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', `${left}%`);
            rect.setAttribute('y', `${top}%`);
            rect.setAttribute('width', `${width}%`);
            rect.setAttribute('height', `${height}%`);
            rect.setAttribute('fill', `${color}22`);
            rect.setAttribute('stroke', color);
            rect.setAttribute('stroke-width', '2.5');
            rect.setAttribute('stroke-dasharray', '6 3');
            rect.setAttribute('id', `bbox-flag-${index}`);
            rect.setAttribute('class', 'transition-all duration-200');

            // Label tag
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', `${left}%`);
            text.setAttribute('y', `${Math.max(ymin / 10 - 1.5, 4)}%`);
            text.setAttribute('fill', color);
            text.setAttribute('font-size', '11px');
            text.setAttribute('font-weight', 'bold');
            text.textContent = `[${flag.risk_level}] ${flag.detected_entity}`;

            svgOverlay.appendChild(rect);
            svgOverlay.appendChild(text);
        });
    }

    // Hook up Flag Card Hover -> Bounding Box Pulse
    function setupBoxInteractivity() {
        document.querySelectorAll('.flag-card').forEach((card, idx) => {
            card.addEventListener('mouseenter', () => {
                const box = document.getElementById(`bbox-flag-${idx}`);
                if (box) {
                    box.setAttribute('stroke-width', '5');
                    box.setAttribute('stroke-dasharray', 'none');
                    box.setAttribute('fill-opacity', '0.45');
                }
            });
            card.addEventListener('mouseleave', () => {
                const box = document.getElementById(`bbox-flag-${idx}`);
                if (box) {
                    box.setAttribute('stroke-width', '2.5');
                    box.setAttribute('stroke-dasharray', '6 3');
                    box.setAttribute('fill-opacity', '0.15');
                }
            });
        });
    }

    // Render Remediation Package
    function renderRemediationPackage(pkg) {
        const remContainer = document.getElementById('remediation-container');
        const remCards = document.getElementById('remediation-cards');
        if (!remContainer || !remCards) return;

        if (!pkg || (!pkg.vfx_work_orders?.length && !pkg.legal_releases?.length && !pkg.script_fixes?.length)) {
            remContainer.classList.add('hidden');
            return;
        }

        remContainer.classList.remove('hidden');
        remCards.innerHTML = '';

        // 1. Legal Releases
        if (pkg.legal_releases) {
            pkg.legal_releases.forEach(rel => {
                const card = document.createElement('div');
                card.className = 'remediation-card legal';
                card.innerHTML = `
                    <span class="rem-badge legal">LEGAL AGREEMENT</span>
                    <div class="rem-title">${rel.form_type}</div>
                    <div class="rem-details">
                        <strong>Licensor:</strong> ${rel.licensor_entity}<br/>
                        <strong>Property:</strong> ${rel.property_description}<br/>
                        <strong>Statute:</strong> ${rel.governing_statute}
                    </div>
                    <pre class="rem-code">${rel.agreement_text}</pre>
                `;
                remCards.appendChild(card);
            });
        }

        // 2. VFX Work Orders
        if (pkg.vfx_work_orders) {
            pkg.vfx_work_orders.forEach(vfx => {
                const card = document.createElement('div');
                card.className = 'remediation-card vfx';
                card.innerHTML = `
                    <span class="rem-badge vfx">VFX WORK ORDER [${vfx.priority}]</span>
                    <div class="rem-title">${vfx.target_entity} (${vfx.timestamp_or_page})</div>
                    <div class="rem-details">
                        <strong>Action:</strong> ${vfx.action_type}<br/>
                        <strong>Tracking Notes:</strong> ${vfx.tracking_notes}
                    </div>
                `;
                remCards.appendChild(card);
            });
        }

        // 3. Script Fixes
        if (pkg.script_fixes) {
            pkg.script_fixes.forEach(fix => {
                const card = document.createElement('div');
                card.className = 'remediation-card script';
                card.innerHTML = `
                    <span class="rem-badge script">SCRIPT PII FIX</span>
                    <div class="rem-title">${fix.page_number}: ${fix.original_text}</div>
                    <div class="rem-details">
                        <strong>Recommended:</strong> <span style="color:#34d399; font-weight:700;">${fix.recommended_replacement}</span><br/>
                        <strong>Rationale:</strong> ${fix.rationale}
                    </div>
                `;
                remCards.appendChild(card);
            });
        }

        // 4. PRO Music Cue Sheet
        if (pkg.music_cue_sheet && pkg.music_cue_sheet.cue_entries?.length) {
            pkg.music_cue_sheet.cue_entries.forEach(cue => {
                const card = document.createElement('div');
                card.className = 'remediation-card music';
                card.innerHTML = `
                    <span class="rem-badge music">PRO MUSIC CUE [${cue.cue_number}]</span>
                    <div class="rem-title">${cue.track_title} - ${cue.artist_performer}</div>
                    <div class="rem-details">
                        <strong>PRO / Publisher:</strong> ${cue.publisher_pro}<br/>
                        <strong>Master Owner:</strong> ${cue.master_rights_holder}<br/>
                        <strong>Usage &amp; Dur:</strong> ${cue.usage_type} (${cue.duration})<br/>
                        <strong style="color:#f87171;">Status:</strong> ${cue.clearance_status}
                    </div>
                `;
                remCards.appendChild(card);
            });
        }
    }

    // Render Filterable Flags
    function renderFlagsList(flags) {
        flagsContainer.innerHTML = '';

        const filtered = flags.filter(f => {
            if (activeFilter === 'ALL') return true;
            return f.risk_level === activeFilter;
        });

        if (filtered.length === 0) {
            flagsContainer.innerHTML = `
                <div class="glass-card" style="text-align:center; padding:32px; color:var(--text-dim);">
                    No clearance flags found matching filter <strong>${activeFilter}</strong>.
                </div>
            `;
            return;
        }

        filtered.forEach((flag, idx) => {
            const card = document.createElement('div');
            card.className = `flag-card risk-${flag.risk_level}`;
            card.setAttribute('data-index', idx);

            const sourcesHtml = flag.verification.sources_checked && flag.verification.sources_checked.length > 0
                ? flag.verification.sources_checked.map(s => `<a href="${s}" target="_blank" class="source-link">${s.replace('https://', '').split('/')[0]}</a>`).join(', ')
                : 'USPTO / Copyright Database';

            const bboxTag = flag.box_2d ? `<span style="background:rgba(59,130,246,0.2);color:#93c5fd;font-size:0.7rem;padding:2px 6px;border-radius:4px;font-family:'JetBrains Mono',monospace;">[BOX: ${flag.box_2d.join(', ')}]</span>` : '';

            card.innerHTML = `
                <div class="flag-header">
                    <div class="flag-title-area">
                        <span class="flag-timecode">${flag.timestamp_or_page}</span>
                        <span class="flag-category">${flag.category.replace('_', ' ')}</span>
                        ${bboxTag}
                    </div>
                    <span class="flag-risk-badge ${flag.risk_level}">${flag.risk_level} RISK</span>
                </div>

                <div class="flag-entity-name">${flag.detected_entity}</div>
                <div class="flag-description">${flag.visual_description}</div>

                <div class="grounding-box">
                    <div class="grounding-header">
                        <span>PARALLEL SEARCH GROUNDING &amp; STATUTORY CITATION</span>
                        <span>${flag.verification.is_public_domain ? '✅ Public Domain' : '⚠️ Proprietary'}</span>
                    </div>
                    <div class="grounding-query">Objective: "${flag.verification.search_objective}"</div>
                    <div class="grounding-statutory">${flag.verification.statutory_context}</div>
                    <div class="grounding-meta-row">
                        <span><strong>Rights Holder:</strong> ${flag.verification.rights_holder_identified || 'Pending Investigation'}</span>
                        <span><strong>Active TM:</strong> ${flag.verification.active_trademark_found ? 'YES' : 'NO'}</span>
                        <span><strong>Sources:</strong> ${sourcesHtml}</span>
                    </div>
                </div>

                ${flag.fair_use_scorecard ? `
                <div class="fair-use-box">
                    <div class="fair-use-header">
                        <span>⚖️ STATUTORY FAIR USE DEFENSE (17 U.S.C. § 107)</span>
                        <span class="defense-pill ${flag.fair_use_scorecard.composite_score >= 3.5 ? 'strong' : (flag.fair_use_scorecard.composite_score >= 2.5 ? 'moderate' : 'risk')}">
                            ${flag.fair_use_scorecard.defense_rating} (Score: ${flag.fair_use_scorecard.composite_score}/5.0)
                        </span>
                    </div>
                    <div class="fair-use-factors-grid">
                        <div class="factor-item">
                            <span class="factor-score">${flag.fair_use_scorecard.purpose_and_character.score}/5</span>
                            <div class="factor-text"><strong>Factor 1 (Purpose):</strong> ${flag.fair_use_scorecard.purpose_and_character.rationale}</div>
                        </div>
                        <div class="factor-item">
                            <span class="factor-score">${flag.fair_use_scorecard.nature_of_work.score}/5</span>
                            <div class="factor-text"><strong>Factor 2 (Nature):</strong> ${flag.fair_use_scorecard.nature_of_work.rationale}</div>
                        </div>
                        <div class="factor-item">
                            <span class="factor-score">${flag.fair_use_scorecard.amount_and_substantiality.score}/5</span>
                            <div class="factor-text"><strong>Factor 3 (Amount):</strong> ${flag.fair_use_scorecard.amount_and_substantiality.rationale}</div>
                        </div>
                        <div class="factor-item">
                            <span class="factor-score">${flag.fair_use_scorecard.market_harm.score}/5</span>
                            <div class="factor-text"><strong>Factor 4 (Market):</strong> ${flag.fair_use_scorecard.market_harm.rationale}</div>
                        </div>
                    </div>
                </div>` : ''}

                ${flag.territory_matrix && flag.territory_matrix.length > 0 ? `
                <div class="territory-box">
                    <div class="territory-header">🌐 MULTI-TERRITORY JURISDICTIONAL COMPLIANCE MATRIX</div>
                    <div class="territory-grid">
                        ${flag.territory_matrix.map(t => `
                            <div class="territory-card">
                                <div class="territory-name">${t.territory}</div>
                                <div class="territory-status">${t.clearance_status}</div>
                                <div class="territory-statute">${t.governing_statute}</div>
                                <div class="territory-notes">${t.jurisdictional_notes}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>` : ''}

                ${flag.arch_assessment ? `
                <div class="arch-box ${flag.arch_assessment.is_public_view_safe_harbor ? 'safe' : 'restricted'}">
                    <div class="arch-header">
                        <span>🏛️ AWCPA ARCHITECTURAL JURISDICTION (17 U.S.C. § 120(a))</span>
                        <span class="arch-badge ${flag.arch_assessment.is_public_view_safe_harbor ? 'safe' : 'restricted'}">
                            ${flag.arch_assessment.is_public_view_safe_harbor ? '✅ STATUTORY SAFE HARBOR' : '⚠️ RESTRICTED COMMERCIAL FACADE'}
                        </span>
                    </div>
                    <div class="arch-statute"><strong>Statute:</strong> ${flag.arch_assessment.governing_statute}</div>
                    <div class="arch-restrictions">${flag.arch_assessment.commercial_filing_restrictions}</div>
                    <div class="arch-recommendation"><strong>Recommendation:</strong> ${flag.arch_assessment.clearance_recommendation}</div>
                </div>` : ''}

                <div class="mitigation-box">
                    <div class="mitigation-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        </svg>
                    </div>
                    <div class="mitigation-text">${flag.mitigation_action}</div>
                </div>
            `;

            flagsContainer.appendChild(card);
        });
    }

    // Filter tab click
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeFilter = tab.getAttribute('data-filter');
            if (currentReport) {
                renderFlagsList(currentReport.flags);
                setupBoxInteractivity();
            }
        });
    });

    function filenameFromDisposition(header, fallback) {
        if (!header) return fallback;
        const star = header.match(/filename\*=UTF-8''([^;]+)/i);
        if (star) return decodeURIComponent(star[1].trim());
        const plain = header.match(/filename="?([^";]+)"?/i);
        if (plain) return plain[1].trim();
        return fallback;
    }

    function triggerBlobDownload(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 2000);
    }

    async function exportCompletedReport(kind) {
        if (!currentReport) {
            alert('Run a clearance audit before exporting.');
            return;
        }

        const isPdf = kind === 'pdf';
        const fallbackName = isPdf
            ? `EO_Clearance_Binder_${(currentReport.project_title || 'Audit').replace(/\s+/g, '_')}.pdf`
            : `CineClear_Markers_${(currentReport.project_title || 'Audit').replace(/\s+/g, '_')}.edl`;

        try {
            let response = await fetch(isPdf ? '/api/export/pdf' : '/api/export/edl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentReport)
            });

            if (!response.ok && currentReport.id) {
                response = await fetch(
                    isPdf
                        ? `/api/reports/${currentReport.id}/pdf`
                        : `/api/reports/${currentReport.id}/edl`
                );
            }

            if (!response.ok) {
                let detail = `Export failed (${response.status})`;
                try {
                    const err = await response.json();
                    detail = err.detail || detail;
                } catch (_) { /* ignore */ }
                throw new Error(detail);
            }

            const blob = await response.blob();
            const name = filenameFromDisposition(
                response.headers.get('content-disposition'),
                fallbackName
            );
            triggerBlobDownload(blob, name);
        } catch (error) {
            console.error('Export failed:', error);
            alert(`Export Error: ${error.message}`);
        }
    }

    if (btnDownloadPdf) {
        btnDownloadPdf.addEventListener('click', () => exportCompletedReport('pdf'));
    }
    const btnDownloadPdfBottom = document.getElementById('btn-download-pdf-bottom');
    if (btnDownloadPdfBottom) {
        btnDownloadPdfBottom.addEventListener('click', () => exportCompletedReport('pdf'));
    }
    if (btnExportEdl) {
        btnExportEdl.addEventListener('click', () => exportCompletedReport('edl'));
    }
    const btnExportEdlBottom = document.getElementById('btn-export-edl-bottom');
    if (btnExportEdlBottom) {
        btnExportEdlBottom.addEventListener('click', () => exportCompletedReport('edl'));
    }

    // New Audit button
    btnNewAudit.addEventListener('click', () => {
        resultsView.classList.add('hidden');
        mediaViewportBox.classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
