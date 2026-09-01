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
    const btnNewAudit = document.getElementById('btn-new-audit');
    const flagsContainer = document.getElementById('flags-container');
    const filterTabs = document.querySelectorAll('.filter-tab');

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

    // Sample selection
    sampleItems.forEach(item => {
        item.addEventListener('click', () => {
            sampleItems.forEach(s => s.classList.remove('active'));
            item.classList.add('active');
            selectedSampleId = item.getAttribute('data-sample');
            selectedFile = null;
            selectedFileName.classList.add('hidden');
            selectedFileName.textContent = '';
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
            { id: 'step-3', label: 'Synthesizing statutory risk rationale & Hollywood mitigations...' },
            { id: 'step-4', label: 'Compiling ReportLab E&O Clearance Binder PDF...' }
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

        renderFlagsList(report.flags);
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

            const sourcesHtml = flag.verification.sources_checked && flag.verification.sources_checked.length > 0
                ? flag.verification.sources_checked.map(s => `<a href="${s}" target="_blank" class="source-link">${s.replace('https://', '').split('/')[0]}</a>`).join(', ')
                : 'USPTO / Copyright Database';

            card.innerHTML = `
                <div class="flag-header">
                    <div class="flag-title-area">
                        <span class="flag-timecode">${flag.timestamp_or_page}</span>
                        <span class="flag-category">${flag.category.replace('_', ' ')}</span>
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
            }
        });
    });

    // Download PDF Binder
    btnDownloadPdf.addEventListener('click', () => {
        if (!currentReport || !currentReport.id) return;
        window.open(`/api/reports/${currentReport.id}/pdf`, '_blank');
    });

    // New Audit button
    btnNewAudit.addEventListener('click', () => {
        resultsView.classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
