from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SiteBuildTests(unittest.TestCase):
    def test_build_site_generates_expected_files(self) -> None:
        subprocess.run(
            ["python3", "scripts/build_site.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        skills = json.loads((ROOT / "site" / "skills.json").read_text(encoding="utf-8"))
        tree = json.loads((ROOT / "site" / "tree.json").read_text(encoding="utf-8"))
        graph = json.loads((ROOT / "site" / "graph.json").read_text(encoding="utf-8"))
        framework = json.loads((ROOT / "site" / "framework_runs.json").read_text(encoding="utf-8"))
        registry_count = sum(
            1
            for line in (ROOT / "registry" / "skills.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        manifest_count = sum(1 for _ in (ROOT / "reports" / "framework-runs").glob("*/manifest.json"))
        taxonomy = json.loads((ROOT / "registry" / "taxonomy.yaml").read_text(encoding="utf-8"))
        self.assertEqual(skills["count"], registry_count)
        self.assertEqual(tree["name"], "SciSkillUniverse")
        self.assertEqual(tree["skill_count"], registry_count)
        self.assertEqual(len(tree["children"]), len(taxonomy))
        self.assertEqual(framework["run_count"], manifest_count)
        self.assertIn("runs", framework)
        self.assertIn("latest_status", framework)
        if framework["latest_status"] is not None:
            self.assertEqual(framework["latest_status"]["summary"]["skill_count"], registry_count)
        self.assertEqual(tree["frontier_leaf_count"], 0)
        self.assertEqual(tree["todo_leaf_count"], 0)
        earth_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "earth_climate_and_geospatial_science")
        geo_leaf = next(node for node in earth_domain["children"] if node["topic_slug"] == "geospatial-feature-engineering")
        self.assertGreaterEqual(geo_leaf["skill_count"], 1)
        stats_domain = next(
            node for node in tree["children"] if node["taxonomy_key"] == "statistical_and_machine_learning_foundations_for_science"
        )
        bayes_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "bayesian-workflows")
        self.assertGreaterEqual(bayes_leaf["skill_count"], 1)
        agent_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "scientific_agents_and_automation")
        self.assertGreaterEqual(agent_domain["skill_count"], 1)
        agent_leaf = next(
            node for node in agent_domain["children"] if node["topic_slug"] == "agent-orchestration-over-skills-and-registries"
        )
        self.assertIn(
            "skill-registry-router-starter",
            {skill["slug"] for skill in agent_leaf.get("skills", [])},
        )
        evaluation_leaf = next(
            node for node in agent_domain["children"] if node["topic_slug"] == "evaluation-harnesses-for-scientific-agents"
        )
        self.assertIn(
            "inspect-evaluation-harness-starter",
            {skill["slug"] for skill in evaluation_leaf.get("skills", [])},
        )
        planning_leaf = next(
            node for node in agent_domain["children"] if node["topic_slug"] == "planning-and-execution-agents"
        )
        self.assertIn(
            "langgraph-planning-execution-agent-starter",
            {skill["slug"] for skill in planning_leaf.get("skills", [])},
        )
        knowledge_domain = next(
            node for node in tree["children"] if node["taxonomy_key"] == "scientific_knowledge_access_and_method_extraction"
        )
        citation_leaf = next(node for node in knowledge_domain["children"] if node["topic_slug"] == "citation-chaining")
        self.assertIn(
            "openalex-citation-chain-starter",
            {skill["slug"] for skill in citation_leaf.get("skills", [])},
        )
        paper_triage_leaf = next(node for node in knowledge_domain["children"] if node["topic_slug"] == "paper-triage-and-ranking")
        self.assertIn(
            "semantic-scholar-paper-triage-starter",
            {skill["slug"] for skill in paper_triage_leaf.get("skills", [])},
        )
        viz_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "visualization_and_reporting")
        self.assertGreaterEqual(viz_domain["skill_count"], 1)
        viz_leaf = next(node for node in viz_domain["children"] if node["topic_slug"] == "publication-plots")
        self.assertIn(
            "matplotlib-publication-plot-starter",
            {skill["slug"] for skill in viz_leaf.get("skills", [])},
        )
        dashboard_leaf = next(node for node in viz_domain["children"] if node["topic_slug"] == "dashboards")
        self.assertIn(
            "dash-scientific-dashboard-starter",
            {skill["slug"] for skill in dashboard_leaf.get("skills", [])},
        )
        interactive_viz_leaf = next(node for node in viz_domain["children"] if node["topic_slug"] == "interactive-reports")
        self.assertIn(
            "plotly-interactive-report-starter",
            {skill["slug"] for skill in interactive_viz_leaf.get("skills", [])},
        )
        workflow_domain = next(
            node for node in tree["children"] if node["taxonomy_key"] == "reproducible_workflows_and_workflow_engines"
        )
        reproducible_notebooks_leaf = next(
            node for node in workflow_domain["children"] if node["topic_slug"] == "reproducible-notebooks"
        )
        self.assertIn(
            "papermill-parameterized-notebook-starter",
            {skill["slug"] for skill in reproducible_notebooks_leaf.get("skills", [])},
        )
        ci_leaf = next(node for node in workflow_domain["children"] if node["topic_slug"] == "ci-for-scientific-pipelines")
        self.assertIn(
            "github-actions-scientific-ci-starter",
            {skill["slug"] for skill in ci_leaf.get("skills", [])},
        )
        meta_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "meta_maintenance")
        self.assertGreaterEqual(meta_domain["skill_count"], 1)
        meta_leaf = next(node for node in meta_domain["children"] if node["topic_slug"] == "broken-link-audits")
        self.assertIn(
            "registry-link-audit-starter",
            {skill["slug"] for skill in meta_leaf.get("skills", [])},
        )
        regression_testing_leaf = next(node for node in meta_domain["children"] if node["topic_slug"] == "regression-testing")
        self.assertIn(
            "precommit-regression-testing-starter",
            {skill["slug"] for skill in regression_testing_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(regression_testing_leaf["resource_count"], 1)
        imaging_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "imaging_and_phenotype_analysis")
        feature_leaf = next(node for node in imaging_domain["children"] if node["topic_slug"] == "feature-extraction")
        self.assertIn(
            "skimage-regionprops-feature-extraction",
            {skill["slug"] for skill in feature_leaf.get("skills", [])},
        )
        cheminfo_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "drug_discovery_and_cheminformatics")
        molecule_standardization_leaf = next(
            node for node in cheminfo_domain["children"] if node["topic_slug"] == "molecule-standardization"
        )
        self.assertIn(
            "rdkit-molecule-standardization",
            {skill["slug"] for skill in molecule_standardization_leaf.get("skills", [])},
        )
        scaffold_leaf = next(node for node in cheminfo_domain["children"] if node["topic_slug"] == "scaffold-analysis")
        self.assertIn(
            "rdkit-scaffold-analysis-starter",
            {skill["slug"] for skill in scaffold_leaf.get("skills", [])},
        )
        materials_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "materials_science_and_engineering")
        crystal_leaf = next(node for node in materials_domain["children"] if node["topic_slug"] == "crystal-structure-parsing")
        self.assertIn(
            "pymatgen-crystal-structure-parsing-starter",
            {skill["slug"] for skill in crystal_leaf.get("skills", [])},
        )
        materials_prediction_leaf = next(
            node for node in materials_domain["children"] if node["topic_slug"] == "materials-property-prediction"
        )
        self.assertIn(
            "matminer-property-regression-starter",
            {skill["slug"] for skill in materials_prediction_leaf.get("skills", [])},
        )
        earth_remote_leaf = next(node for node in earth_domain["children"] if node["topic_slug"] == "remote-sensing-preprocessing")
        self.assertGreaterEqual(earth_remote_leaf["resource_count"], 1)
        stats_uncertainty_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "uncertainty-estimation")
        self.assertIn(
            "arviz-posterior-diagnostics-starter",
            {skill["slug"] for skill in stats_uncertainty_leaf.get("skills", [])},
        )
        numerics_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "scientific_computing_and_numerical_methods")
        uq_leaf = next(node for node in numerics_domain["children"] if node["topic_slug"] == "uncertainty-aware-simulation")
        self.assertIn(
            "chaospy-uncertainty-propagation-starter",
            {skill["slug"] for skill in uq_leaf.get("skills", [])},
        )
        stats_causal_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "causal-inference")
        self.assertGreaterEqual(stats_causal_leaf["resource_count"], 1)
        transcriptomics_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "transcriptomics")
        diffexp_leaf = next(node for node in transcriptomics_domain["children"] if node["topic_slug"] == "differential-expression")
        self.assertGreaterEqual(diffexp_leaf["resource_count"], 1)
        self.assertIn(
            "pydeseq2-differential-expression-starter",
            {skill["slug"] for skill in diffexp_leaf.get("skills", [])},
        )
        integration_leaf = next(
            node for node in transcriptomics_domain["children"] if node["topic_slug"] == "single-cell-integration-batch-correction"
        )
        self.assertIn(
            "scanpy-combat-batch-correction-starter",
            {skill["slug"] for skill in integration_leaf.get("skills", [])},
        )
        atlas_leaf = next(node for node in transcriptomics_domain["children"] if node["topic_slug"] == "multi-sample-atlas-workflows")
        self.assertIn(
            "cellxgene-census-atlas-query-starter",
            {skill["slug"] for skill in atlas_leaf.get("skills", [])},
        )
        annotation_leaf = next(node for node in transcriptomics_domain["children"] if node["topic_slug"] == "cell-type-annotation")
        self.assertIn(
            "scanpy-cell-type-annotation-starter",
            {skill["slug"] for skill in annotation_leaf.get("skills", [])},
        )
        trajectory_leaf = next(node for node in transcriptomics_domain["children"] if node["topic_slug"] == "trajectory-inference")
        self.assertIn(
            "scanpy-dpt-trajectory-starter",
            {skill["slug"] for skill in trajectory_leaf.get("skills", [])},
        )
        genomics_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "genomics")
        format_leaf = next(node for node in genomics_domain["children"] if node["topic_slug"] == "fastq-bam-cram-basics")
        self.assertIn(
            "pysam-sam-bam-summary-starter",
            {skill["slug"] for skill in format_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(format_leaf["resource_count"], 1)
        metagenomics_leaf = next(node for node in genomics_domain["children"] if node["topic_slug"] == "metagenomics")
        self.assertIn(
            "sourmash-signature-compare-starter",
            {skill["slug"] for skill in metagenomics_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(metagenomics_leaf["resource_count"], 1)
        read_qc_leaf = next(node for node in genomics_domain["children"] if node["topic_slug"] == "read-qc-and-trimming")
        self.assertIn(
            "fastqc-multiqc-read-qc-starter",
            {skill["slug"] for skill in read_qc_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(read_qc_leaf["resource_count"], 2)
        alignment_leaf = next(node for node in genomics_domain["children"] if node["topic_slug"] == "alignment-and-mapping")
        self.assertIn(
            "minimap2-read-mapping-starter",
            {skill["slug"] for skill in alignment_leaf.get("skills", [])},
        )
        variant_filtering_leaf = next(node for node in genomics_domain["children"] if node["topic_slug"] == "variant-filtering")
        self.assertIn(
            "bcftools-variant-filtering-starter",
            {skill["slug"] for skill in variant_filtering_leaf.get("skills", [])},
        )
        self.assertIn(
            "rasterio-windowed-raster-preprocessing-starter",
            {skill["slug"] for skill in earth_remote_leaf.get("skills", [])},
        )
        self.assertIn(
            "dowhy-average-treatment-effect-starter",
            {skill["slug"] for skill in stats_causal_leaf.get("skills", [])},
        )
        clinical_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "clinical_biomedical_data_science")
        survival_leaf = next(node for node in clinical_domain["children"] if node["topic_slug"] == "survival-analysis")
        self.assertIn(
            "lifelines-kaplan-meier-starter",
            {skill["slug"] for skill in survival_leaf.get("skills", [])},
        )
        fairness_leaf = next(node for node in clinical_domain["children"] if node["topic_slug"] == "fairness-bias-analysis")
        self.assertIn(
            "fairlearn-bias-audit-starter",
            {skill["slug"] for skill in fairness_leaf.get("skills", [])},
        )
        proteomics_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "proteomics_and_protein_biology")
        protein_families_leaf = next(
            node for node in proteomics_domain["children"] if node["topic_slug"] == "protein-families-and-domains"
        )
        self.assertIn(
            "interpro-entry-summary",
            {skill["slug"] for skill in protein_families_leaf.get("skills", [])},
        )
        sequence_feature_leaf = next(
            node for node in proteomics_domain["children"] if node["topic_slug"] == "sequence-feature-annotation"
        )
        self.assertIn(
            "uniprot-sequence-feature-annotation-starter",
            {skill["slug"] for skill in sequence_feature_leaf.get("skills", [])},
        )
        systems_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "systems_biology_and_network_science")
        pathway_analysis_leaf = next(node for node in systems_domain["children"] if node["topic_slug"] == "pathway-analysis")
        self.assertIn(
            "reactome-pathway-analysis-starter",
            {skill["slug"] for skill in pathway_analysis_leaf.get("skills", [])},
        )
        reactome_identifier_leaf = next(
            node for node in systems_domain["children"] if node["topic_slug"] == "reactome-identifier-enrichment"
        )
        self.assertIn(
            "reactome-identifiers-enrichment",
            {skill["slug"] for skill in reactome_identifier_leaf.get("skills", [])},
        )
        bioconductor_leaf = next(
            node for node in systems_domain["children"] if node["topic_slug"] == "gene-set-tooling-from-bioconductor"
        )
        self.assertIn(
            "clusterprofiler-custom-enrichment",
            {skill["slug"] for skill in bioconductor_leaf.get("skills", [])},
        )
        graph_construction_leaf = next(node for node in systems_domain["children"] if node["topic_slug"] == "graph-construction")
        self.assertIn(
            "networkx-graph-construction-starter",
            {skill["slug"] for skill in graph_construction_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(graph_construction_leaf["resource_count"], 1)
        propagation_leaf = next(node for node in systems_domain["children"] if node["topic_slug"] == "network-propagation")
        self.assertIn(
            "networkx-network-propagation-starter",
            {skill["slug"] for skill in propagation_leaf.get("skills", [])},
        )
        hpc_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "hpc_slurm_and_scaling")
        monitoring_leaf = next(node for node in hpc_domain["children"] if node["topic_slug"] == "monitoring-and-accounting")
        self.assertIn(
            "slurm-monitoring-accounting-starter",
            {skill["slug"] for skill in monitoring_leaf.get("skills", [])},
        )
        job_arrays_leaf = next(node for node in hpc_domain["children"] if node["topic_slug"] == "job-arrays")
        self.assertIn(
            "slurm-job-array-starter",
            {skill["slug"] for skill in job_arrays_leaf.get("skills", [])},
        )
        multi_node_leaf = next(node for node in hpc_domain["children"] if node["topic_slug"] == "multi-node-jobs")
        self.assertIn(
            "multi-node-jobs-starter",
            {skill["slug"] for skill in multi_node_leaf.get("skills", [])},
        )
        comp_chem_domain = next(
            node
            for node in tree["children"]
            if node["taxonomy_key"] == "computational_chemistry_and_molecular_simulation"
        )
        conformer_leaf = next(
            node for node in comp_chem_domain["children"] if node["topic_slug"] == "small-molecule-conformer-generation"
        )
        self.assertIn(
            "rdkit-conformer-generation-starter",
            {skill["slug"] for skill in conformer_leaf.get("skills", [])},
        )
        forcefield_leaf = next(
            node for node in comp_chem_domain["children"] if node["topic_slug"] == "force-field-assignment"
        )
        self.assertIn(
            "openmm-forcefield-assignment-starter",
            {skill["slug"] for skill in forcefield_leaf.get("skills", [])},
        )
        robotics_domain = next(
            node
            for node in tree["children"]
            if node["taxonomy_key"] == "robotics_lab_automation_and_scientific_instrumentation"
        )
        planning_robotics_leaf = next(
            node for node in robotics_domain["children"] if node["topic_slug"] == "robotic-experiment-planning"
        )
        self.assertIn(
            "autoprotocol-experiment-plan-starter",
            {skill["slug"] for skill in planning_robotics_leaf.get("skills", [])},
        )
        notebook_report_leaf = next(node for node in viz_domain["children"] if node["topic_slug"] == "notebook-to-report-conversion")
        self.assertIn(
            "quarto-notebook-report-starter",
            {skill["slug"] for skill in notebook_report_leaf.get("skills", [])},
        )
        pathway_walk_leaf = next(
            node for node in systems_domain["children"] if node["topic_slug"] == "pathway-traversal-and-hierarchy-walks"
        )
        self.assertIn(
            "reactome-pathway-hierarchy-walk-starter",
            {skill["slug"] for skill in pathway_walk_leaf.get("skills", [])},
        )
        ppi_leaf = next(node for node in systems_domain["children"] if node["topic_slug"] == "protein-protein-interaction-analysis")
        self.assertIn(
            "string-interaction-partners-starter",
            {skill["slug"] for skill in ppi_leaf.get("skills", [])},
        )
        scientific_compute_domain = next(
            node for node in tree["children"] if node["taxonomy_key"] == "scientific_computing_and_numerical_methods"
        )
        data_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "data_acquisition_and_dataset_handling")
        chunking_leaf = next(node for node in data_domain["children"] if node["topic_slug"] == "chunking-sharding")
        self.assertIn(
            "zarr-chunked-array-store-starter",
            {skill["slug"] for skill in chunking_leaf.get("skills", [])},
        )
        validation_leaf = next(node for node in data_domain["children"] if node["topic_slug"] == "data-validation")
        self.assertIn(
            "frictionless-tabular-validation-starter",
            {skill["slug"] for skill in validation_leaf.get("skills", [])},
        )
        provenance_leaf = next(node for node in data_domain["children"] if node["topic_slug"] == "data-provenance-tracking")
        self.assertIn(
            "rocrate-metadata-bundle-starter",
            {skill["slug"] for skill in provenance_leaf.get("skills", [])},
        )
        compchem_domain = next(
            node for node in tree["children"] if node["taxonomy_key"] == "computational_chemistry_and_molecular_simulation"
        )
        md_leaf = next(node for node in compchem_domain["children"] if node["topic_slug"] == "molecular-dynamics-setup")
        self.assertIn(
            "openmm-langevin-dynamics-starter",
            {skill["slug"] for skill in md_leaf.get("skills", [])},
        )
        bayes_opt_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "bayesian-optimization")
        self.assertIn(
            "optuna-bayesian-optimization-starter",
            {skill["slug"] for skill in bayes_opt_leaf.get("skills", [])},
        )
        ode_leaf = next(
            node for node in scientific_compute_domain["children"] if node["topic_slug"] == "ode-sde-simulation-workflows"
        )
        self.assertIn(
            "scipy-ode-simulation-starter",
            {skill["slug"] for skill in ode_leaf.get("skills", [])},
        )
        pde_leaf = next(
            node for node in scientific_compute_domain["children"] if node["topic_slug"] == "pde-discretization-and-solvers"
        )
        self.assertIn(
            "fipy-diffusion-pde-starter",
            {skill["slug"] for skill in pde_leaf.get("skills", [])},
        )
        ecology_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "ecology_evolution_and_biodiversity")
        species_distribution_leaf = next(
            node for node in ecology_domain["children"] if node["topic_slug"] == "species-distribution-modeling"
        )
        self.assertIn(
            "gbif-species-occurrence-search-starter",
            {skill["slug"] for skill in species_distribution_leaf.get("skills", [])},
        )
        biodiversity_dataset_leaf = next(
            node for node in ecology_domain["children"] if node["topic_slug"] == "biodiversity-dataset-discovery"
        )
        self.assertIn(
            "gbif-dataset-search-starter",
            {skill["slug"] for skill in biodiversity_dataset_leaf.get("skills", [])},
        )
        phylogenetics_leaf = next(
            node for node in ecology_domain["children"] if node["topic_slug"] == "phylogenetic-comparative-workflows"
        )
        self.assertIn(
            "scikitbio-tree-comparison-starter",
            {skill["slug"] for skill in phylogenetics_leaf.get("skills", [])},
        )
        neuroscience_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "neuroscience_and_neuroimaging")
        neuro_io_leaf = next(
            node for node in neuroscience_domain["children"] if node["topic_slug"] == "neuroimaging-i-o-and-formats"
        )
        self.assertIn(
            "nibabel-nifti-summary-starter",
            {skill["slug"] for skill in neuro_io_leaf.get("skills", [])},
        )
        eeg_leaf = next(node for node in neuroscience_domain["children"] if node["topic_slug"] == "eeg-meg-preprocessing")
        self.assertIn(
            "mne-eeg-preprocessing-starter",
            {skill["slug"] for skill in eeg_leaf.get("skills", [])},
        )
        connectomics_leaf = next(
            node for node in neuroscience_domain["children"] if node["topic_slug"] == "connectomics-and-graph-analysis"
        )
        self.assertIn(
            "mne-connectivity-graph-starter",
            {skill["slug"] for skill in connectomics_leaf.get("skills", [])},
        )
        fmri_leaf = next(
            node for node in neuroscience_domain["children"] if node["topic_slug"] == "fmri-preprocessing-and-denoising"
        )
        self.assertIn(
            "nilearn-fmri-denoising-starter",
            {skill["slug"] for skill in fmri_leaf.get("skills", [])},
        )
        epigenomics_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "epigenomics_and_chromatin")
        peak_calling_leaf = next(node for node in epigenomics_domain["children"] if node["topic_slug"] == "peak-calling")
        self.assertIn(
            "macs3-peak-calling-starter",
            {skill["slug"] for skill in peak_calling_leaf.get("skills", [])},
        )
        physics_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "physics_and_astronomy")
        telescope_leaf = next(node for node in physics_domain["children"] if node["topic_slug"] == "telescope-image-preprocessing")
        self.assertIn(
            "astropy-fits-image-summary-starter",
            {skill["slug"] for skill in telescope_leaf.get("skills", [])},
        )
        agriculture_domain = next(
            node for node in tree["children"] if node["taxonomy_key"] == "agriculture_food_and_plant_science"
        )
        plant_leaf = next(node for node in agriculture_domain["children"] if node["topic_slug"] == "plant-phenotyping")
        self.assertIn(
            "plantcv-plant-phenotyping-starter",
            {skill["slug"] for skill in plant_leaf.get("skills", [])},
        )
        robotics_domain = next(
            node
            for node in tree["children"]
            if node["taxonomy_key"] == "robotics_lab_automation_and_scientific_instrumentation"
        )
        liquid_handling_leaf = next(
            node for node in robotics_domain["children"] if node["topic_slug"] == "liquid-handling-protocol-generation"
        )
        self.assertIn(
            "opentrons-liquid-handling-protocol-starter",
            {skill["slug"] for skill in liquid_handling_leaf.get("skills", [])},
        )
        instrument_leaf = next(
            node for node in robotics_domain["children"] if node["topic_slug"] == "instrument-control-and-scheduling"
        )
        self.assertIn(
            "qcodes-parameter-sweep-starter",
            {skill["slug"] for skill in instrument_leaf.get("skills", [])},
        )
        data_domain = next(node for node in tree["children"] if node["taxonomy_key"] == "data_acquisition_and_dataset_handling")
        compression_leaf = next(node for node in data_domain["children"] if node["topic_slug"] == "compression-decompression")
        self.assertIn(
            "numcodecs-compression-decompression-starter",
            {skill["slug"] for skill in compression_leaf.get("skills", [])},
        )
        conversion_leaf = next(node for node in data_domain["children"] if node["topic_slug"] == "format-conversion")
        self.assertIn(
            "pyarrow-format-conversion-starter",
            {skill["slug"] for skill in conversion_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(conversion_leaf["resource_count"], 2)
        stats_testing_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "statistical-testing")
        self.assertIn(
            "scipy-statistical-testing-starter",
            {skill["slug"] for skill in stats_testing_leaf.get("skills", [])},
        )
        dr_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "dimensionality-reduction")
        self.assertIn(
            "umap-dimensionality-reduction-starter",
            {skill["slug"] for skill in dr_leaf.get("skills", [])},
        )
        experimental_design_leaf = next(node for node in stats_domain["children"] if node["topic_slug"] == "experimental-design")
        self.assertIn(
            "pydoe3-experimental-design-starter",
            {skill["slug"] for skill in experimental_design_leaf.get("skills", [])},
        )
        geometry_leaf = next(node for node in compchem_domain["children"] if node["topic_slug"] == "geometry-optimization")
        self.assertIn(
            "ase-geometry-optimization-starter",
            {skill["slug"] for skill in geometry_leaf.get("skills", [])},
        )
        skill_dedup_leaf = next(node for node in meta_domain["children"] if node["topic_slug"] == "skill-deduplication")
        self.assertIn(
            "rapidfuzz-skill-deduplication-starter",
            {skill["slug"] for skill in skill_dedup_leaf.get("skills", [])},
        )
        resource_dedup_leaf = next(node for node in meta_domain["children"] if node["topic_slug"] == "resource-deduplication")
        self.assertIn(
            "datasketch-resource-deduplication-starter",
            {skill["slug"] for skill in resource_dedup_leaf.get("skills", [])},
        )
        summary_catalog_leaf = next(node for node in viz_domain["children"] if node["topic_slug"] == "summary-pages-and-catalogs")
        self.assertIn(
            "mkdocs-summary-catalog-starter",
            {skill["slug"] for skill in summary_catalog_leaf.get("skills", [])},
        )
        self.assertGreaterEqual(len(graph["edges"]), 20)



if __name__ == "__main__":
    unittest.main()
