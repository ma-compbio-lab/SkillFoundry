PYTHON ?= python3
CAMPAIGN_LABEL ?= protein-spatial-sequence-law-gwas-single-cell

.PHONY: validate build-site test test-verbose validate-sc-skills audit-skills smoke-matrix benchmark-skill-advantage framework-status framework-cycle framework-cycle-parallel framework-design-skill framework-evaluate-skills framework-evaluate-skills-parallel framework-campaign framework-campaign-status framework-submit-campaign smoke-openalex smoke-openalex-citation-chain smoke-europepmc smoke-crossref smoke-pubmed smoke-ensembl smoke-ncbi-gene smoke-literature-brief smoke-rcsb smoke-rcsb-entry smoke-clinicaltrials smoke-lifelines smoke-reactome smoke-reactome-enrichment smoke-reactome-pathway-analysis smoke-reactome-hierarchy smoke-string smoke-pride smoke-ebi-proteins smoke-interpro smoke-chembl smoke-encode smoke-biosamples smoke-metabolights smoke-quickgo smoke-networkx smoke-network-propagation smoke-cwl smoke-wdl smoke-rdkit smoke-rdkit-standardize smoke-rdkit-scaffolds smoke-rdkit-conformers smoke-deepchem smoke-openmm smoke-openmm-forcefield smoke-psi4 smoke-fgsea smoke-clusterprofiler smoke-snakemake smoke-nextflow smoke-nextflow-slurm smoke-nf-core smoke-scanpy smoke-scanpy-ranked-genes smoke-scanpy-combat smoke-scanpy-cell-annotation smoke-scanpy-dpt smoke-cellxgene-atlas smoke-pydeseq2 smoke-sourmash smoke-pysam smoke-fastqc smoke-macs3 smoke-skimage smoke-skimage-regionprops smoke-xarray smoke-rasterio smoke-matminer smoke-matminer-regression smoke-pymatgen-structure smoke-geopandas smoke-pymc smoke-arviz smoke-dowhy smoke-fairlearn smoke-skill-router smoke-langgraph-agent smoke-matplotlib smoke-plotly smoke-quarto smoke-link-audit smoke-precommit smoke-slurm smoke-slurm-accounting smoke-slurm-array smoke-scipy-ode smoke-gbif smoke-gbif-datasets smoke-scikitbio smoke-nibabel smoke-mne smoke-mne-connectivity smoke-nilearn smoke-uniprot smoke-fipy smoke-astropy smoke-plantcv smoke-opentrons smoke-frictionless smoke-rocrate smoke-minimap2 smoke-qcodes smoke-chaospy smoke-inspect-eval smoke-autoprotocol smoke-dash-dashboard smoke-protein-language-models

validate:
	$(PYTHON) scripts/validate_repository.py

build-site:
	$(PYTHON) scripts/build_site.py

test:
	$(PYTHON) scripts/run_tests.py

test-verbose:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

validate-sc-skills:
	$(PYTHON) scripts/validate_sc_skill_experiments.py --all --run-local-tests --json-out scratch/reviews/sc_skills_validation.json --markdown-out scratch/reviews/sc_skills_validation.md

audit-skills:
	$(PYTHON) scripts/audit_skill_suite.py --json-out scratch/reviews/skill_suite_audit.json --markdown-out scratch/reviews/skill_suite_audit.md

smoke-matrix:
	$(PYTHON) scripts/run_skill_smoke_matrix.py --json-out scratch/reviews/skill_smoke_matrix.json --markdown-out scratch/reviews/skill_smoke_matrix.md

benchmark-skill-advantage:
	$(PYTHON) scripts/benchmark_skill_advantage.py --json-out scratch/reviews/skill_advantage_benchmark.json --markdown-out scratch/reviews/skill_advantage_benchmark.md

framework-status:
	$(PYTHON) scripts/sciskill_framework.py --json status --focus-limit 8

framework-cycle:
	$(PYTHON) scripts/sciskill_framework.py cycle --loops 1 --verification-mode standard

framework-cycle-parallel:
	$(PYTHON) scripts/sciskill_framework.py --workspace-root scratch/framework/workspaces-$$USER cycle --loops 1 --focus-limit 12 --stage-workers 4 --background-validation-limit 16 --background-validation-workers 4 --verification-mode standard --label parallel-cycle

framework-design-skill:
	$(PYTHON) scripts/sciskill_framework.py design-skill --prompt "Design a skill for a user-specified scientific task." --verification-mode validate

framework-evaluate-skills:
	$(PYTHON) scripts/sciskill_framework.py --json evaluate-skills --limit 8 --verification-mode validate

framework-evaluate-skills-parallel:
	$(PYTHON) scripts/sciskill_framework.py evaluate-skills --limit 16 --workers 4 --verification-mode validate --label parallel-eval

framework-campaign:
	$(PYTHON) scripts/sciskill_framework.py --workspace-root scratch/framework/workspaces-$(CAMPAIGN_LABEL) campaign --label $(CAMPAIGN_LABEL) --focus-term protein --focus-term proteomics --focus-term spatial --focus-term sequence --focus-term law --focus-term legal --focus-term gwas --focus-term single-cell --focus-term "single cell" --focus-limit 12 --stage-workers 6 --background-validation-limit 24 --background-validation-workers 6 --evaluation-batch-size 24 --evaluation-workers 6 --verification-mode standard --max-runtime-minutes 120 --stop-buffer-minutes 10

framework-campaign-status:
	$(PYTHON) scripts/sciskill_framework.py campaign-status --label $(CAMPAIGN_LABEL)

framework-submit-campaign:
	sbatch slurm/jobs/framework_domain_campaign_cpu.sbatch

smoke-openalex:
	$(PYTHON) skills/scientific-knowledge/openalex-literature-search/scripts/search_openalex.py --query "single-cell RNA-seq" --per-page 1

smoke-openalex-citation-chain:
	$(PYTHON) skills/scientific-knowledge/openalex-citation-chain-starter/scripts/run_openalex_citation_chain.py --work-id 10.1038/nature12373 --limit 3 --out scratch/openalex-citation-chain/hallmarks_citation_chain.json

smoke-europepmc:
	$(PYTHON) skills/scientific-knowledge/europepmc-method-triage/scripts/search_europepmc.py --query "single-cell RNA-seq" --page-size 1

smoke-crossref:
	$(PYTHON) skills/scientific-knowledge/crossref-metadata-search/scripts/search_crossref.py --query-title "single-cell RNA-seq" --rows 1

smoke-pubmed:
	$(PYTHON) skills/scientific-knowledge/ncbi-pubmed-search/scripts/search_pubmed.py --term "single-cell RNA-seq" --retmax 1

smoke-ensembl:
	$(PYTHON) skills/genomics/ensembl-gene-lookup/scripts/lookup_gene.py --symbol BRCA1

smoke-ncbi-gene:
	$(PYTHON) skills/genomics/ncbi-gene-search/scripts/search_ncbi_gene.py --symbol BRCA1 --species "homo sapiens" --retmax 1

smoke-literature-brief:
	$(PYTHON) skills/scientific-knowledge/multi-source-literature-brief/scripts/build_literature_brief.py --query "single-cell RNA-seq" --limit 1

smoke-rcsb:
	$(PYTHON) skills/structural-biology/rcsb-pdb-search/scripts/search_rcsb.py --query hemoglobin --rows 1

smoke-rcsb-entry:
	$(PYTHON) skills/structural-biology/rcsb-pdb-entry-summary/scripts/fetch_pdb_entry.py --entry-id 4HHB

smoke-clinicaltrials:
	$(PYTHON) skills/clinical-biomedical-data-science/clinicaltrials-study-search/scripts/search_clinicaltrials.py --condition melanoma --page-size 1

smoke-lifelines:
	./slurm/envs/statistics/bin/python skills/clinical-biomedical-data-science/lifelines-kaplan-meier-starter/scripts/run_lifelines_kaplan_meier.py --input skills/clinical-biomedical-data-science/lifelines-kaplan-meier-starter/examples/toy_survival_cohort.tsv --summary-out scratch/lifelines/kaplan_meier_summary.json --png-out scratch/lifelines/kaplan_meier_plot.png

smoke-reactome:
	$(PYTHON) skills/systems-biology/reactome-event-summary/scripts/fetch_reactome_event_summary.py --stable-id R-HSA-141409

smoke-reactome-enrichment:
	$(PYTHON) skills/systems-biology/reactome-identifiers-enrichment/scripts/analyze_reactome_identifiers.py --identifiers "BRCA1,TP53" --page-size 3

smoke-reactome-pathway-analysis:
	$(PYTHON) skills/systems-biology/reactome-pathway-analysis-starter/scripts/run_reactome_pathway_analysis.py --identifiers BRCA1,TP53,EGFR --top-n 5 --out scratch/reactome-pathway-analysis/top_pathways.json

smoke-reactome-hierarchy:
	$(PYTHON) skills/systems-biology/reactome-pathway-hierarchy-walk-starter/scripts/run_reactome_hierarchy_walk.py --species 9606 --stable-id R-HSA-141409 --out scratch/reactome-hierarchy/r_hsa_141409_hierarchy.json

smoke-string:
	$(PYTHON) skills/systems-biology/string-interaction-partners-starter/scripts/run_string_interaction_partners.py --identifier-file skills/systems-biology/string-interaction-partners-starter/examples/tp53_query.txt --species 9606 --limit 5 --required-score 700 --out scratch/string/tp53_partners.json

smoke-pride:
	$(PYTHON) skills/proteomics/pride-project-search/scripts/search_pride_projects.py --keyword phosphoproteomics --page-size 1

smoke-ebi-proteins:
	$(PYTHON) skills/proteomics/ebi-proteins-entry-summary/scripts/fetch_protein_summary.py --accession P38398

smoke-protein-language-models:
	$(PYTHON) skills/proteomics/protein-language-model-function-analysis-starter/scripts/run_protein_language_model_function_analysis.py --input skills/proteomics/protein-language-model-function-analysis-starter/examples/toy_sequences.fasta --labels skills/proteomics/protein-language-model-function-analysis-starter/examples/toy_labels.tsv --config skills/proteomics/protein-language-model-function-analysis-starter/examples/analysis_config.json --embeddings-out scratch/protein-lm/toy_embeddings.tsv --summary-out scratch/protein-lm/toy_summary.json

smoke-interpro:
	$(PYTHON) skills/proteomics/interpro-entry-summary/scripts/fetch_interpro_entry.py --accession IPR000023 --out scratch/interpro/ipr000023_summary.json

smoke-chembl:
	$(PYTHON) skills/drug-discovery-and-cheminformatics/chembl-molecule-search/scripts/search_chembl_molecules.py --query imatinib --limit 1

smoke-encode:
	$(PYTHON) skills/epigenomics-and-chromatin/encode-experiment-search/scripts/search_encode_experiments.py --search-term "ATAC-seq" --limit 1

smoke-biosamples:
	$(PYTHON) skills/data-acquisition-and-dataset-handling/biosamples-sample-search/scripts/search_biosamples_samples.py --text "breast cancer" --size 1

smoke-metabolights:
	$(PYTHON) skills/metabolomics-and-other-omics/metabolights-study-search/scripts/search_metabolights_studies.py --query diabetes --rows 1

smoke-quickgo:
	$(PYTHON) skills/systems-biology/quickgo-term-search/scripts/search_quickgo_terms.py --query apoptosis --limit 1

smoke-networkx:
	$(PYTHON) skills/systems-biology/networkx-graph-construction-starter/scripts/run_networkx_graph_construction.py --input skills/systems-biology/networkx-graph-construction-starter/examples/toy_pathway_edges.tsv --source-node EGFR --target-node STAT3 --out scratch/networkx/graph_summary.json

smoke-network-propagation:
	$(PYTHON) skills/systems-biology/networkx-network-propagation-starter/scripts/run_networkx_network_propagation.py --input skills/systems-biology/networkx-network-propagation-starter/examples/toy_network.tsv --seeds skills/systems-biology/networkx-network-propagation-starter/examples/toy_seeds.txt --top-k 5 --out scratch/networkx-propagation/summary.json

smoke-cwl:
	$(PYTHON) skills/reproducible-workflows/cwl-commandlinetool-starter/scripts/run_cwl_hello.py --message "hello from cwl smoke" --workspace scratch/cwl/workspace --summary-out scratch/cwl/summary.json

smoke-wdl:
	$(PYTHON) skills/reproducible-workflows/wdl-task-starter/scripts/run_wdl_hello.py --name WDL --workspace scratch/wdl/workspace --summary-out scratch/wdl/summary.json

smoke-rdkit:
	./slurm/envs/chem-tools/bin/python skills/drug-discovery-and-cheminformatics/rdkit-molecular-descriptors/scripts/compute_rdkit_descriptors.py --smiles "CC(=O)OC1=CC=CC=C1C(=O)O" --name aspirin --out scratch/rdkit/aspirin.json

smoke-rdkit-standardize:
	./slurm/envs/chem-tools/bin/python skills/drug-discovery-and-cheminformatics/rdkit-molecule-standardization/scripts/standardize_rdkit_molecule.py --smiles "CC(=O)[O-].[Na+]" --name sodium-acetate --out scratch/rdkit-standardize/sodium_acetate.json

smoke-rdkit-scaffolds:
	./slurm/envs/chem-tools/bin/python skills/drug-discovery-and-cheminformatics/rdkit-scaffold-analysis-starter/scripts/run_rdkit_scaffold_analysis.py --input skills/drug-discovery-and-cheminformatics/rdkit-scaffold-analysis-starter/examples/molecules.tsv --out scratch/rdkit-scaffolds/example_scaffold_summary.json

smoke-rdkit-conformers:
	./slurm/envs/chem-tools/bin/python skills/computational-chemistry-and-molecular-simulation/rdkit-conformer-generation-starter/scripts/run_rdkit_conformer_generation.py --input skills/computational-chemistry-and-molecular-simulation/rdkit-conformer-generation-starter/examples/molecules.tsv --num-confs 4 --out scratch/rdkit-conformers/summary.json

smoke-deepchem:
	./slurm/envs/deepchem/bin/python skills/drug-discovery-and-cheminformatics/deepchem-circular-featurization/scripts/compute_circular_fingerprints.py --out scratch/deepchem/fingerprints.json

smoke-openmm:
	./slurm/envs/chem-tools/bin/python skills/computational-chemistry-and-molecular-simulation/openmm-system-minimization/scripts/run_openmm_minimization.py --out scratch/openmm/minimization.json

smoke-openmm-forcefield:
	./slurm/envs/chem-tools/bin/python skills/computational-chemistry-and-molecular-simulation/openmm-forcefield-assignment-starter/scripts/run_openmm_forcefield_assignment.py --input skills/computational-chemistry-and-molecular-simulation/openmm-forcefield-assignment-starter/examples/two_waters.pdb --out scratch/openmm-forcefield/summary.json

smoke-psi4:
	./slurm/envs/psi4/bin/python skills/computational-chemistry-and-molecular-simulation/psi4-single-point-energy/scripts/run_psi4_single_point.py --out scratch/psi4/water_hf_sto3g_summary.json

smoke-fgsea:
	./slurm/envs/bioconductor/bin/Rscript skills/systems-biology/fgsea-preranked-enrichment/scripts/run_fgsea_preranked.R --out scratch/fgsea/summary.json

smoke-clusterprofiler:
	./slurm/envs/bioconductor/bin/Rscript skills/systems-biology/clusterprofiler-custom-enrichment/scripts/run_clusterprofiler_custom_enrichment.R --out scratch/clusterprofiler/summary.json

smoke-snakemake:
	$(PYTHON) skills/reproducible-workflows/snakemake-toy-workflow-starter/scripts/run_snakemake_workflow.py --workspace scratch/snakemake-toy-workflow --summary-out scratch/snakemake-toy-workflow/run_summary.json

smoke-nextflow:
	$(PYTHON) skills/reproducible-workflows/nextflow-hello-workflow/scripts/run_nextflow_hello.py --out-dir scratch/nextflow-hello/results --work-dir scratch/nextflow-hello/work

smoke-nextflow-slurm:
	$(PYTHON) skills/reproducible-workflows/nextflow-hello-workflow/scripts/run_nextflow_hello.py --executor slurm --partition cpu --out-dir scratch/nextflow-hello-slurm/results --work-dir scratch/nextflow-hello-slurm/work --summary-out scratch/nextflow-hello-slurm/summary.json

smoke-nf-core:
	$(PYTHON) skills/reproducible-workflows/nf-core-pipeline-list/scripts/list_nfcore_pipelines.py --sort pulled --limit 3

smoke-scanpy:
	./slurm/envs/scanpy/bin/python skills/transcriptomics/scanpy-qc-starter/scripts/run_scanpy_qc.py --input skills/transcriptomics/scanpy-qc-starter/examples/toy_counts.tsv --summary-out scratch/scanpy/summary.json --h5ad-out scratch/scanpy/toy_counts.h5ad

smoke-scanpy-ranked-genes:
	./slurm/envs/scanpy/bin/python skills/transcriptomics/scanpy-ranked-genes-starter/scripts/run_scanpy_ranked_genes.py --input skills/transcriptomics/scanpy-ranked-genes-starter/examples/toy_counts.tsv --groups skills/transcriptomics/scanpy-ranked-genes-starter/examples/toy_groups.tsv --top-n 2 --out scratch/scanpy-ranked-genes/summary.json

smoke-scanpy-combat:
	./slurm/envs/scanpy/bin/python skills/transcriptomics/scanpy-combat-batch-correction-starter/scripts/run_scanpy_combat_batch_correction.py --counts skills/transcriptomics/scanpy-combat-batch-correction-starter/examples/toy_counts.tsv --metadata skills/transcriptomics/scanpy-combat-batch-correction-starter/examples/toy_metadata.tsv --summary-out scratch/scanpy-combat/summary.json

smoke-scanpy-cell-annotation:
	./slurm/envs/scanpy/bin/python skills/transcriptomics/scanpy-cell-type-annotation-starter/scripts/run_scanpy_cell_type_annotation.py --counts skills/transcriptomics/scanpy-cell-type-annotation-starter/examples/toy_counts.tsv --markers skills/transcriptomics/scanpy-cell-type-annotation-starter/examples/toy_markers.json --truth skills/transcriptomics/scanpy-cell-type-annotation-starter/examples/toy_truth.tsv --summary-out scratch/scanpy-cell-annotation/summary.json

smoke-scanpy-dpt:
	./slurm/envs/scanpy/bin/python skills/transcriptomics/scanpy-dpt-trajectory-starter/scripts/run_scanpy_dpt_trajectory.py --counts skills/transcriptomics/scanpy-dpt-trajectory-starter/examples/toy_counts.tsv --root-cell c0 --expected-order skills/transcriptomics/scanpy-dpt-trajectory-starter/examples/expected_order.txt --summary-out scratch/scanpy-dpt/summary.json

smoke-cellxgene-atlas:
	./slurm/envs/census/bin/python skills/transcriptomics/cellxgene-census-atlas-query-starter/scripts/run_cellxgene_census_atlas_query.py --keyword "Tabula Sapiens" --limit 5 --out scratch/census/tabula_sapiens_query.json

smoke-pydeseq2:
	./slurm/envs/transcriptomics/bin/python skills/transcriptomics/pydeseq2-differential-expression-starter/scripts/run_pydeseq2_differential_expression.py --counts skills/transcriptomics/pydeseq2-differential-expression-starter/examples/toy_counts.tsv --metadata skills/transcriptomics/pydeseq2-differential-expression-starter/examples/toy_metadata.tsv --out scratch/pydeseq2/differential_expression_summary.json

smoke-sourmash:
	./slurm/envs/metagenomics/bin/python skills/genomics/sourmash-signature-compare-starter/scripts/run_sourmash_signature_compare.py --out scratch/metagenomics/sourmash_compare_summary.json

smoke-pysam:
	./slurm/envs/genomics/bin/python skills/genomics/pysam-sam-bam-summary-starter/scripts/run_pysam_sam_bam_summary.py --input skills/genomics/pysam-sam-bam-summary-starter/examples/toy_reads.sam --out scratch/genomics/pysam_summary.json --bam-out scratch/genomics/toy_reads.bam

smoke-fastqc:
	$(PYTHON) skills/genomics/fastqc-multiqc-read-qc-starter/scripts/run_fastqc_multiqc_read_qc.py --input skills/genomics/fastqc-multiqc-read-qc-starter/examples/toy_reads.fastq --summary-out scratch/genomics/fastqc_multiqc_summary.json

smoke-gwas:
	$(PYTHON) skills/genomics/gwas-starter/scripts/run_gwas_summary_qc.py --input skills/genomics/gwas-starter/examples/toy_sumstats.tsv --config skills/genomics/gwas-starter/examples/qc_config.json --out-tsv scratch/gwas/gwas_qc.tsv --summary-out scratch/gwas/gwas_qc_summary.json

smoke-macs3:
	./slurm/envs/genomics/bin/python skills/epigenomics-and-chromatin/macs3-peak-calling-starter/scripts/run_macs3_peak_calling.py --treatment skills/epigenomics-and-chromatin/macs3-peak-calling-starter/examples/toy_treatment.bed --summary-out scratch/epigenomics/macs3_peak_summary.json

smoke-skimage:
	./slurm/envs/scientific-python/bin/python skills/imaging-and-phenotype-analysis/skimage-otsu-segmentation-starter/scripts/run_skimage_otsu_segmentation.py --out scratch/skimage/segmentation_summary.json

smoke-skimage-regionprops:
	./slurm/envs/scientific-python/bin/python skills/imaging-and-phenotype-analysis/skimage-regionprops-feature-extraction/scripts/run_skimage_regionprops_features.py --out scratch/skimage-regionprops/summary.json

smoke-xarray:
	./slurm/envs/scientific-python/bin/python skills/earth-climate-and-geospatial-science/xarray-climate-cube-starter/scripts/run_xarray_climate_cube.py --out scratch/xarray/climate_cube_summary.json

smoke-rasterio:
	./slurm/envs/geospatial/bin/python skills/earth-climate-and-geospatial-science/rasterio-windowed-raster-preprocessing-starter/scripts/run_rasterio_windowed_preprocessing.py --out scratch/geospatial/rasterio_preprocessing_summary.json

smoke-matminer:
	./slurm/envs/materials/bin/python skills/materials-science-and-engineering/matminer-composition-featurization/scripts/run_matminer_composition_features.py --formula Fe2O3 --formula LiFePO4 --out scratch/materials/matminer_features.json

smoke-matminer-regression:
	./slurm/envs/materials/bin/python skills/materials-science-and-engineering/matminer-property-regression-starter/scripts/run_matminer_property_regression.py --out scratch/materials/property_regression_summary.json

smoke-pymatgen-structure:
	./slurm/envs/materials/bin/python skills/materials-science-and-engineering/pymatgen-crystal-structure-parsing-starter/scripts/run_pymatgen_structure_summary.py --input skills/materials-science-and-engineering/pymatgen-crystal-structure-parsing-starter/examples/cscl.cif --out scratch/materials/cscl_structure_summary.json

smoke-geopandas:
	./slurm/envs/geospatial/bin/python skills/earth-climate-and-geospatial-science/geopandas-spatial-join-starter/scripts/run_geopandas_spatial_join.py --out scratch/geopandas/spatial_join_summary.json

smoke-pymc:
	./slurm/envs/statistics/bin/python skills/statistical-and-machine-learning-foundations-for-science/pymc-bayesian-linear-regression-starter/scripts/run_pymc_linear_regression.py --input skills/statistical-and-machine-learning-foundations-for-science/pymc-bayesian-linear-regression-starter/examples/toy_observations.tsv --out scratch/pymc/linear_regression_summary.json

smoke-arviz:
	./slurm/envs/statistics/bin/python skills/statistical-and-machine-learning-foundations-for-science/arviz-posterior-diagnostics-starter/scripts/run_arviz_posterior_diagnostics.py --out scratch/arviz/posterior_diagnostics_summary.json

smoke-dowhy:
	./slurm/envs/causal/bin/python skills/statistical-and-machine-learning-foundations-for-science/dowhy-average-treatment-effect-starter/scripts/run_dowhy_average_treatment_effect.py --out scratch/dowhy/average_treatment_effect_summary.json

smoke-fairlearn:
	./slurm/envs/statistics/bin/python skills/clinical-biomedical-data-science/fairlearn-bias-audit-starter/scripts/run_fairlearn_bias_audit.py --input skills/clinical-biomedical-data-science/fairlearn-bias-audit-starter/examples/toy_fairness_cohort.tsv --summary-out scratch/fairlearn/fairness_audit_summary.json

smoke-skill-router:
	$(PYTHON) skills/scientific-agents-and-automation/skill-registry-router-starter/scripts/route_skill_query.py --query "single-cell marker ranking" --top-k 3 --out scratch/router/router_single_cell_query.json

smoke-langgraph-agent:
	./slurm/envs/agents/bin/python skills/scientific-agents-and-automation/langgraph-planning-execution-agent-starter/scripts/run_langgraph_planning_agent.py --goal "single-cell marker ranking with an interactive report" --out scratch/agents/planning_agent_summary.json

smoke-matplotlib:
	./slurm/envs/statistics/bin/python skills/visualization-and-reporting/matplotlib-publication-plot-starter/scripts/render_publication_plot.py --input skills/visualization-and-reporting/matplotlib-publication-plot-starter/examples/toy_measurements.tsv --png-out scratch/matplotlib/publication_plot.png --summary-out scratch/matplotlib/publication_plot_summary.json

smoke-plotly:
	./slurm/envs/statistics/bin/python skills/visualization-and-reporting/plotly-interactive-report-starter/scripts/render_plotly_interactive_report.py --input skills/visualization-and-reporting/plotly-interactive-report-starter/examples/toy_measurements.tsv --html-out scratch/plotly/report.html --summary-out scratch/plotly/report_summary.json

smoke-quarto:
	$(PYTHON) skills/visualization-and-reporting/quarto-notebook-report-starter/scripts/render_quarto_notebook_report.py --input skills/visualization-and-reporting/quarto-notebook-report-starter/examples/toy_report.ipynb --html-out scratch/quarto/toy_report.html --summary-out scratch/quarto/toy_report_summary.json

smoke-papermill:
	./slurm/envs/reporting/bin/python skills/reproducible-workflows/papermill-parameterized-notebook-starter/scripts/run_papermill_parameterized_notebook.py --input skills/reproducible-workflows/papermill-parameterized-notebook-starter/examples/toy_parameters.ipynb --output-notebook scratch/papermill/toy_parameters_executed.ipynb --summary-out scratch/papermill/toy_parameters_summary.json --x 5 --y 7

smoke-gh-actions:
	$(PYTHON) skills/reproducible-workflows/github-actions-scientific-ci-starter/scripts/render_github_actions_scientific_ci.py --workflow-out scratch/github-actions/sciskill_ci.yml --summary-out scratch/github-actions/sciskill_ci_summary.json --smoke-target smoke-zarr --smoke-target smoke-openmm-md --smoke-target smoke-optuna

smoke-link-audit:
	$(PYTHON) skills/meta-maintenance/registry-link-audit-starter/scripts/audit_registry_links.py --resource-id matplotlib-docs --resource-id lychee-docs --out scratch/meta/link_audit_summary.json

smoke-precommit:
	$(PYTHON) skills/meta-maintenance/precommit-regression-testing-starter/scripts/run_precommit_regression.py --workspace scratch/precommit-regression --out scratch/precommit-regression/summary.json

smoke-slurm:
	$(PYTHON) skills/hpc/slurm-job-debug-template/scripts/submit_smoke_job.py --partition cpu --job-name make-smoke --sleep 1

smoke-slurm-accounting:
	$(PYTHON) skills/hpc/slurm-monitoring-accounting-starter/scripts/run_slurm_monitoring_accounting.py --partition cpu --job-name make-monitoring --sleep 2 --out scratch/slurm-monitoring/summary.json

smoke-slurm-array:
	$(PYTHON) skills/hpc/slurm-job-array-starter/scripts/run_slurm_job_array.py --partition cpu --job-name make-array --array-spec 0-1 --sleep 1 --out scratch/slurm-array/summary.json

smoke-scipy-ode:
	./slurm/envs/scientific-python/bin/python skills/scientific-computing-and-numerical-methods/scipy-ode-simulation-starter/scripts/run_scipy_ode_simulation.py --out scratch/scipy-ode/lotka_volterra_summary.json

smoke-zarr:
	$(PYTHON) skills/data-acquisition-and-dataset-handling/zarr-chunked-array-store-starter/scripts/run_zarr_chunked_array_store.py --input skills/data-acquisition-and-dataset-handling/zarr-chunked-array-store-starter/examples/toy_matrix.tsv --store-out scratch/zarr/toy_matrix.zarr --summary-out scratch/zarr/toy_matrix_summary.json

smoke-numcodecs:
	./slurm/envs/data-tools/bin/python skills/data-acquisition-and-dataset-handling/numcodecs-compression-decompression-starter/scripts/run_numcodecs_compression_decompression.py --input skills/data-acquisition-and-dataset-handling/numcodecs-compression-decompression-starter/examples/toy_matrix.tsv --out scratch/numcodecs/toy_matrix_summary.json

smoke-pyarrow:
	./slurm/envs/data-tools/bin/python skills/data-acquisition-and-dataset-handling/pyarrow-format-conversion-starter/scripts/run_pyarrow_format_conversion.py --input skills/data-acquisition-and-dataset-handling/pyarrow-format-conversion-starter/examples/toy_matrix.tsv --parquet-out scratch/pyarrow/toy_table.parquet --summary-out scratch/pyarrow/toy_table_summary.json

smoke-frictionless:
	./slurm/envs/data-tools/bin/python skills/data-acquisition-and-dataset-handling/frictionless-tabular-validation-starter/scripts/run_frictionless_tabular_validation.py --input skills/data-acquisition-and-dataset-handling/frictionless-tabular-validation-starter/examples/toy_people_valid.csv --schema skills/data-acquisition-and-dataset-handling/frictionless-tabular-validation-starter/examples/toy_people_schema.json --out scratch/data-validation/frictionless_summary.json

smoke-rocrate:
	./slurm/envs/data-tools/bin/python skills/data-acquisition-and-dataset-handling/rocrate-metadata-bundle-starter/scripts/build_rocrate_metadata_bundle.py --input skills/data-acquisition-and-dataset-handling/rocrate-metadata-bundle-starter/examples/toy_measurements.csv --crate-dir scratch/rocrate/toy_bundle --summary-out scratch/rocrate/toy_bundle_summary.json

smoke-minimap2:
	./slurm/envs/genomics/bin/python skills/genomics/minimap2-read-mapping-starter/scripts/run_minimap2_read_mapping.py --reference skills/genomics/minimap2-read-mapping-starter/examples/toy_reference.fa --reads skills/genomics/minimap2-read-mapping-starter/examples/toy_reads.fastq --bam-out scratch/genomics/minimap2/toy_reads.bam --summary-out scratch/genomics/minimap2/toy_reads_summary.json

smoke-openmm-md:
	./slurm/envs/chem-tools/bin/python skills/computational-chemistry-and-molecular-simulation/openmm-langevin-dynamics-starter/scripts/run_openmm_langevin_dynamics.py --out scratch/openmm/langevin_dynamics_summary.json

smoke-ase:
	./slurm/envs/chem-tools/bin/python skills/computational-chemistry-and-molecular-simulation/ase-geometry-optimization-starter/scripts/run_ase_geometry_optimization.py --input skills/computational-chemistry-and-molecular-simulation/ase-geometry-optimization-starter/examples/toy_argon_dimer.json --out scratch/chemistry/ase_geometry_optimization_summary.json

smoke-optuna:
	./slurm/envs/statistics/bin/python skills/statistical-and-machine-learning-foundations-for-science/optuna-bayesian-optimization-starter/scripts/run_optuna_bayesian_optimization.py --out scratch/optuna/bayesian_optimization_summary.json

smoke-scipy-stats:
	./slurm/envs/statistics/bin/python skills/statistical-and-machine-learning-foundations-for-science/scipy-statistical-testing-starter/scripts/run_scipy_statistical_testing.py --input skills/statistical-and-machine-learning-foundations-for-science/scipy-statistical-testing-starter/examples/toy_groups.tsv --out scratch/statistics/scipy_statistical_testing_summary.json

smoke-umap:
	./slurm/envs/statistics/bin/python skills/statistical-and-machine-learning-foundations-for-science/umap-dimensionality-reduction-starter/scripts/run_umap_dimensionality_reduction.py --input skills/statistical-and-machine-learning-foundations-for-science/umap-dimensionality-reduction-starter/examples/toy_embedding_input.tsv --out scratch/statistics/umap_embedding_summary.json

smoke-pydoe3:
	./slurm/envs/statistics/bin/python skills/statistical-and-machine-learning-foundations-for-science/pydoe3-experimental-design-starter/scripts/run_pydoe3_experimental_design.py --input skills/statistical-and-machine-learning-foundations-for-science/pydoe3-experimental-design-starter/examples/toy_factors.json --out scratch/statistics/experimental_design_summary.json

smoke-gbif:
	$(PYTHON) skills/ecology-evolution-and-biodiversity/gbif-species-occurrence-search-starter/scripts/run_gbif_species_occurrence_search.py --scientific-name "Puma concolor" --country US --out scratch/gbif/puma_concolor_us.json

smoke-gbif-datasets:
	$(PYTHON) skills/ecology-evolution-and-biodiversity/gbif-dataset-search-starter/scripts/run_gbif_dataset_search.py --query puma --limit 3 --out scratch/gbif-datasets/puma_dataset_search.json

smoke-scikitbio:
	./slurm/envs/ecology/bin/python skills/ecology-evolution-and-biodiversity/scikitbio-tree-comparison-starter/scripts/run_scikitbio_tree_comparison.py --out scratch/ecology/tree_comparison_summary.json

smoke-nibabel:
	./slurm/envs/neuro/bin/python skills/neuroscience-and-neuroimaging/nibabel-nifti-summary-starter/scripts/run_nibabel_nifti_summary.py --nifti-out scratch/neuro/toy_bold.nii.gz --out scratch/neuro/toy_bold_summary.json

smoke-mne:
	./slurm/envs/neuro/bin/python skills/neuroscience-and-neuroimaging/mne-eeg-preprocessing-starter/scripts/run_mne_eeg_preprocessing.py --out scratch/neuro/mne_preprocessing_summary.json

smoke-mne-connectivity:
	./slurm/envs/neuro/bin/python skills/neuroscience-and-neuroimaging/mne-connectivity-graph-starter/scripts/run_mne_connectivity_graph.py --out scratch/neuro/mne_connectivity_graph_summary.json

smoke-nilearn:
	./slurm/envs/neuro/bin/python skills/neuroscience-and-neuroimaging/nilearn-fmri-denoising-starter/scripts/run_nilearn_fmri_denoising.py --out scratch/neuro/nilearn_denoising_summary.json

smoke-uniprot:
	$(PYTHON) skills/proteomics/uniprot-sequence-feature-annotation-starter/scripts/fetch_uniprot_sequence_feature_summary.py --accession P04637 --out scratch/uniprot/p04637_sequence_features.json

smoke-fipy:
	./slurm/envs/numerics/bin/python skills/scientific-computing-and-numerical-methods/fipy-diffusion-pde-starter/scripts/run_fipy_diffusion_pde.py --out scratch/numerics/fipy_diffusion_summary.json

smoke-astropy:
	./slurm/envs/astronomy/bin/python skills/physics-and-astronomy/astropy-fits-image-summary-starter/scripts/run_astropy_fits_image_summary.py --fits-out scratch/astronomy/toy_image.fits --out scratch/astronomy/toy_image_summary.json

smoke-plantcv:
	./slurm/envs/plant-science/bin/python skills/agriculture-food-and-plant-science/plantcv-plant-phenotyping-starter/scripts/run_plantcv_plant_phenotyping.py --image-out scratch/plantcv/toy_plant.png --mask-out scratch/plantcv/toy_plant_mask.png --out scratch/plantcv/toy_plant_summary.json

smoke-opentrons:
	./slurm/envs/automation/bin/python skills/robotics-lab-automation-and-scientific-instrumentation/opentrons-liquid-handling-protocol-starter/scripts/run_opentrons_liquid_handling_protocol.py --protocol-out scratch/opentrons/toy_protocol.py --out scratch/opentrons/toy_protocol_summary.json

smoke-qcodes:
	./slurm/envs/instrumentation/bin/python skills/robotics-lab-automation-and-scientific-instrumentation/qcodes-parameter-sweep-starter/scripts/run_qcodes_parameter_sweep.py --setpoints skills/robotics-lab-automation-and-scientific-instrumentation/qcodes-parameter-sweep-starter/examples/toy_setpoints.tsv --db-out scratch/qcodes/toy_sweep.db --summary-out scratch/qcodes/toy_sweep_summary.json

smoke-chaospy:
	./slurm/envs/numerics/bin/python skills/scientific-computing-and-numerical-methods/chaospy-uncertainty-propagation-starter/scripts/run_chaospy_uncertainty_propagation.py --config skills/scientific-computing-and-numerical-methods/chaospy-uncertainty-propagation-starter/examples/toy_parameters.json --out scratch/numerics/chaospy_uncertainty_summary.json

smoke-inspect-eval:
	./slurm/envs/agents/bin/python skills/scientific-agents-and-automation/inspect-evaluation-harness-starter/scripts/run_inspect_evaluation_harness.py --cases skills/scientific-agents-and-automation/inspect-evaluation-harness-starter/examples/toy_eval_cases.json --summary-out scratch/agents/inspect_evaluation_harness_summary.json --log-dir scratch/agents/inspect-eval-logs

smoke-autoprotocol:
	./slurm/envs/instrumentation/bin/python skills/robotics-lab-automation-and-scientific-instrumentation/autoprotocol-experiment-plan-starter/scripts/build_autoprotocol_experiment_plan.py --transfers skills/robotics-lab-automation-and-scientific-instrumentation/autoprotocol-experiment-plan-starter/examples/toy_transfers.tsv --protocol-json scratch/instrumentation/autoprotocol_plan.json --summary-out scratch/instrumentation/autoprotocol_plan_summary.json

smoke-dash-dashboard:
	./slurm/envs/reporting/bin/python skills/visualization-and-reporting/dash-scientific-dashboard-starter/scripts/build_dash_scientific_dashboard.py --input skills/visualization-and-reporting/dash-scientific-dashboard-starter/examples/toy_measurements.tsv --html-out scratch/dash/dashboard_preview.html --summary-out scratch/dash/dashboard_summary.json

smoke-rapidfuzz-dedup:
	./slurm/envs/maintenance/bin/python skills/meta-maintenance/rapidfuzz-skill-deduplication-starter/scripts/run_rapidfuzz_skill_deduplication.py --input skills/meta-maintenance/rapidfuzz-skill-deduplication-starter/examples/toy_skills.tsv --threshold 85 --out scratch/meta/rapidfuzz_dedup_summary.json

smoke-datasketch-dedup:
	./slurm/envs/maintenance/bin/python skills/meta-maintenance/datasketch-resource-deduplication-starter/scripts/run_datasketch_resource_deduplication.py --input skills/meta-maintenance/datasketch-resource-deduplication-starter/examples/toy_resources.jsonl --threshold 0.5 --out scratch/meta/datasketch_dedup_summary.json

smoke-mkdocs-catalog:
	./slurm/envs/reporting/bin/python skills/visualization-and-reporting/mkdocs-summary-catalog-starter/scripts/build_mkdocs_summary_catalog.py --input skills/visualization-and-reporting/mkdocs-summary-catalog-starter/examples/toy_catalog.json --workspace scratch/mkdocs-catalog --summary-out scratch/mkdocs-catalog/summary.json

.PHONY: smoke-metadata-harmonization smoke-synthetic-toy-dataset smoke-cooler-hic smoke-bcftools-filtering smoke-semantic-scholar-triage smoke-semantic-scholar-review smoke-figure-table-extraction smoke-dataset-code-links smoke-benchmark-table smoke-matminer-toy smoke-frontier-generated smoke-deepchem-molgraph

smoke-metadata-harmonization:
	$(PYTHON) skills/data-acquisition-and-dataset-handling/metadata-harmonization-starter/scripts/run_metadata_harmonization.py --input skills/data-acquisition-and-dataset-handling/metadata-harmonization-starter/examples/cohort_a.tsv --input skills/data-acquisition-and-dataset-handling/metadata-harmonization-starter/examples/cohort_b.tsv --mapping skills/data-acquisition-and-dataset-handling/metadata-harmonization-starter/examples/column_mapping.json --out-tsv scratch/metadata-harmonization/harmonized_metadata.tsv --summary-out scratch/metadata-harmonization/harmonized_metadata_summary.json

smoke-synthetic-toy-dataset:
	$(PYTHON) skills/data-acquisition-and-dataset-handling/synthetic-toy-dataset-generator-starter/scripts/generate_synthetic_toy_dataset.py --sample-count 6 --feature-count 4 --seed 17 --out-dir scratch/synthetic-toy-dataset/toy_bundle --summary-out scratch/synthetic-toy-dataset/toy_bundle_summary.json

smoke-cooler-hic:
	./slurm/envs/scientific-python/bin/python skills/epigenomics-and-chromatin/cooler-hic-matrix-summary-starter/scripts/run_cooler_hic_matrix_summary.py --out scratch/epigenomics/cooler_hic_summary.json --cooler-out scratch/epigenomics/toy_contacts.cool

smoke-bcftools-filtering:
	$(PYTHON) skills/genomics/bcftools-variant-filtering-starter/scripts/run_bcftools_variant_filtering.py --input skills/genomics/bcftools-variant-filtering-starter/examples/toy_variants.vcf --out scratch/genomics/bcftools_variant_filtering_summary.json --filtered-vcf-out scratch/genomics/toy_variants.filtered.vcf.gz

smoke-semantic-scholar-triage:
	$(PYTHON) skills/scientific-knowledge/semantic-scholar-paper-triage-starter/scripts/run_semantic_scholar_paper_triage.py --input skills/scientific-knowledge/semantic-scholar-paper-triage-starter/examples/candidate_papers.json --query "single-cell RNA-seq atlas integration" --out scratch/scientific-knowledge/paper_triage_summary.json

smoke-semantic-scholar-review:
	$(PYTHON) skills/scientific-knowledge/semantic-scholar-review-paper-mining-starter/scripts/run_semantic_scholar_review_mining.py --input skills/scientific-knowledge/semantic-scholar-review-paper-mining-starter/examples/paper_metadata.json --out scratch/scientific-knowledge/review_papers.json

smoke-figure-table-extraction:
	$(PYTHON) skills/scientific-knowledge/figure-table-caption-extraction-starter/scripts/run_figure_table_caption_extraction.py --input skills/scientific-knowledge/figure-table-caption-extraction-starter/examples/paper_excerpt.txt --out scratch/scientific-knowledge/captions.json

smoke-dataset-code-links:
	$(PYTHON) skills/scientific-knowledge/dataset-code-link-extraction-starter/scripts/run_dataset_code_link_extraction.py --input skills/scientific-knowledge/dataset-code-link-extraction-starter/examples/paper_text.md --out scratch/scientific-knowledge/dataset_code_links.json

smoke-benchmark-table:
	$(PYTHON) skills/scientific-knowledge/benchmark-table-mining-starter/scripts/run_benchmark_table_mining.py --input skills/scientific-knowledge/benchmark-table-mining-starter/examples/benchmark_note.md --out scratch/scientific-knowledge/benchmark_tables.json

smoke-matminer-toy:
	./slurm/envs/materials/bin/python skills/materials-science-and-engineering/matminer-toy-property-prediction-starter/scripts/run_matminer_toy_property_prediction.py --input skills/materials-science-and-engineering/matminer-toy-property-prediction-starter/examples/toy_materials.tsv --out scratch/materials/property_prediction_summary.json

smoke-frontier-generated:
	$(PYTHON) -m unittest tests.smoke.test_phase43_frontier_completion_skills.Phase43FrontierCompletionSkillTests.test_generated_frontier_starters_emit_summaries -v

smoke-deepchem-molgraph:
	./slurm/envs/chemtools/bin/python skills/computational-chemistry-and-molecular-simulation/deepchem-molgraph-featurization/scripts/featurize_molecules.py --input skills/computational-chemistry-and-molecular-simulation/deepchem-molgraph-featurization/examples/molecules.tsv --out scratch/deepchem/molgraph_featurization.json
