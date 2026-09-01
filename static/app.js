document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const projectTitleInput = document.getElementById('project-title-input');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectedFileName = document.getElementById('selected-file-name');
    const browseBtn = document.querySelector('.browse-btn');
    const btnRunAudit = document.getElementById('btn-run-audit');
    const sampleItems = document.querySelectorAll('.sample-item');
    
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
            const isButtonClick = e.target.classList.contains('btn-sample-select');
            
            sampleItems.forEach(s => {
                s.classList.remove('active');
                const b = s.querySelector('.btn-sample-select');
                if (b) b.textContent = 'Load Asset';
            });
            item.classList.add('active');
            const btn = item.querySelector('.btn-sample-select');
            if (btn) btn.textContent = '✓ Ready';
            
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

            // If user clicked the button directly, immediately run audit
            if (isButtonClick) {
                btnRunAudit.click();
            }
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

        // Animate pipeline steps
        animatePipelineSteps();

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

            const response = await fetch('/api/audit', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Audit processing failed');
            }

            currentReport = await response.json();
            
            // Finish pipeline and show results
            setTimeout(() => {
                renderResults(currentReport);
                processingView.classList.add('hidden');
                resultsView.classList.remove('hidden');
                window.scrollTo({ top: resultsView.offsetTop - 80, behavior: 'smooth' });
            }, 1200);

        } catch (error) {
            console.error('Audit failed:', error);
            alert(`Clearance Audit Error: ${error.message}`);
            processingView.classList.add('hidden');
        }
    });

    // Pipeline Step Animation
    function animatePipelineSteps() {
        const steps = [
            { id: 'step-1', label: 'Extracting visual keyframes & parsing script dialog...' },
            { id: 'step-2', label: 'Grounded Parallel Search: querying USPTO & legal databases...' },
            { id: 'step-3', label: 'Senior Counsel Critic Agent: enforcing statutory invariants...' },
            { id: 'step-4', label: 'Generating VFX work orders, releases & E&O PDF binder...' }
        ];

        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                // Update active state
                document.querySelectorAll('.step-item').forEach((el, idx) => {
                    if (idx <= currentStep) {
                        el.classList.add('active');
                    } else {
                        el.classList.remove('active');
                    }
                });
                processingStepLabel.textContent = steps[currentStep].label;
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 600);
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

    // Download PDF Binder
    btnDownloadPdf.addEventListener('click', () => {
        if (!currentReport || !currentReport.id) return;
        window.open(`/api/reports/${currentReport.id}/pdf`, '_blank');
    });

    // Export EDL Timeline Markers
    if (btnExportEdl) {
        btnExportEdl.addEventListener('click', () => {
            if (!currentReport || !currentReport.id) return;
            window.open(`/api/reports/${currentReport.id}/edl`, '_blank');
        });
    }

    // New Audit button
    btnNewAudit.addEventListener('click', () => {
        resultsView.classList.add('hidden');
        mediaViewportBox.classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
