#May want to rename this script to make it easy to get the usage
#Set up the workflows...
#1. Steps:...
#2. Fators:...
import os
import glob
from nipype import config
from nipype.pipeline import engine as pe
from nilearn import datasets

from RestingfMRI_Denoise.interfaces.prep_bids import BIDSGrab, BIDSDataSink
from RestingfMRI_Denoise.interfaces.confounds import Confounds, GroupConfounds
from RestingfMRI_Denoise.interfaces.denoising import Denoise
from RestingfMRI_Denoise.interfaces.connectivity import Connectivity, GroupConnectivity
from RestingfMRI_Denoise.interfaces.pipeline_selector import PipelineSelector
from RestingfMRI_Denoise.interfaces.quality_measures import QualityMeasures, PipelinesQualityMeasures, MergeGroupQualityMeasures
from RestingfMRI_Denoise.interfaces.report_creator import ReportCreator
from RestingfMRI_Denoise.parcellation import get_parcelation_file_path, get_distance_matrix_file_path
from RestingfMRI_Denoise.pipelines import get_pipelines_paths
import RestingfMRI_Denoise.utils.temps as temps
from pathlib import Path

pipelines_paths = get_pipelines_paths()
tool_dir = '/Users/xiaoqian/projects/myRepository/RestingfMRI_Denoise/RestingfMRI_Denoise'
bids_dir=os.path.join(tool_dir, 'tests')
derivatives = 'fmriprep'
parcellation_paths = get_parcelation_file_path('Schaefer2018_200Parcels_7Networks_order_FSLMNI152_1mm')
task = 'test'
session = 'baseline'
subject = '14'
smoothing = True
ica_aroma = False
high_pass = 0.008
low_pass = 0.08
base_dir='/tmp/Restingfmri_Denoise/'

workflow = pe.Workflow(name='RestingfMRI_Denoise', base_dir=base_dir)
pipelineselector = pe.Node(PipelineSelector(),
                           name="PipelineSelector")
pipelineselector.iterables = ('pipeline_path', pipelines_paths)

# Outputs: pipeline, pipeline_name, low_pass, high_pass

# 2) --- Loading BIDS structure
# Inputs: directory, task, derivatives
grabbing_bids = pe.Node(
                      BIDSGrab(
                          bids_dir=bids_dir,
                          derivatives=derivatives,
                          task=task,
                          session=session,
                          subject=subject
                          ),
                      name="BidsGrabber")
# Outputs: fmri_prep, conf_raw, conf_json, entities, tr_dict

# 3) --- Confounds preprocessing
# Inputs: pipeline, conf_raw, conf_json
temppath = os.path.join(base_dir, 'prep_conf')
prep_conf = pe.MapNode(
                      Confounds(
                          output_dir=temps.mkdtemp(temppath)
                          ),
                      iterfield=['conf_raw', 'conf_json', 'entities', 'fmri_prep_aroma'],
                      name="ConfPrep")
# Outputs: conf_prep, low_pass, high_pass

# 4) --- Denoising
# Inputs: fmri_prep, fmri_prep_aroma, conf_prep, pipeline, entity, tr_dict
iterate = ['fmri_prep', 'conf_prep', 'entities']
if not ica_aroma:
    iterate = iterate
else:
    iterate.append('fmri_prep_aroma')
temppath = os.path.join(base_dir, 'denoise')
denoise = pe.MapNode(
                    Denoise(
                        high_pass=high_pass,
                        low_pass=low_pass,
                        ica_aroma=ica_aroma,
                        output_dir=temps.mkdtemp(temppath)
                        ),
                    iterfield=iterate,
                    name="Denoiser", mem_gb=6)
# Outputs: fmri_denoised

# 5) --- Connectivity estimation
# Inputs: fmri_denoised
temppath = os.path.join(base_dir, 'connectivity')
connectivity = pe.MapNode(
                        Connectivity(
                            output_dir=temps.mkdtemp(temppath),
                            parcellation=parcellation_paths
                            ),
                        iterfield=['fmri_denoised'],
                        name='ConnCalc')
# Outputs: conn_mat, carpet_plot

# 6) --- Group confounds
# Inputs: conf_summary, pipeline_name
# FIXME BEGIN
# This is part of temporary solution.
# Group nodes write to bids dir insted of tmp and let files be grabbed by datasink
os.makedirs(os.path.join(bids_dir, 'derivatives', 'denoise'), exist_ok=True)
# FIXME END
group_conf_summary = pe.Node(
                            GroupConfounds(
                                output_dir=os.path.join(bids_dir, 'derivatives', 'denoise'),
                                ),
                            name="GroupConf")
# Outputs: group_conf_summary

# 7) --- Group connectivity
# Inputs: corr_mat, pipeline_name
group_connectivity = pe.Node(
                            GroupConnectivity(
                                output_dir=os.path.join(bids_dir, 'derivatives', 'denoise'),
                                ),
                            name="GroupConn")
# Outputs: group_corr_mat

# 8) --- Quality measures
# Inputs: group_corr_mat, group_conf_summary, pipeline_name
quality_measures = pe.MapNode(
                              QualityMeasures(
                                  output_dir=os.path.join(bids_dir, 'derivatives', 'denoise'),
                                  distance_matrix=get_distance_matrix_file_path()
                                  ),
                              iterfield=['group_corr_mat', 'group_conf_summary'],
                              name="QualityMeasures")
# Outputs: fc_fd_summary, edges_weight, edges_weight_clean

# 9) --- Merge quality measures into lists for further processing
# Inputs: fc_fd_summary, edges_weight, edges_weight_clean
merge_quality_measures = pe.JoinNode(MergeGroupQualityMeasures(),
                                     joinsource=pipelineselector,
                                     name="Merge")
# Outputs: fc_fd_summary, edges_weight

# 10) --- Quality measures across pipelines
# Inputs: fc_fd_summary, edges_weight
pipelines_quality_measures = pe.Node(
                                    PipelinesQualityMeasures(
                                                          output_dir=os.path.join(bids_dir, 'derivatives', 'denoise'),
                                                          ),
                                    name="PipelinesQC")

# Outputs: pipelines_fc_fd_summary, pipelines_edges_weight

# 11) --- Report from data
report_creator = pe.JoinNode(
                        ReportCreator(
                            group_data_dir=os.path.join(bids_dir, 'derivatives', 'denoise')
                            ),
                        joinsource=pipelineselector,
                        joinfield=['pipelines', 'pipelines_names'],
                        name='ReportCreator')

# 12) --- Save derivatives
# TODO: Fill missing in/out
ds_confounds = pe.MapNode(BIDSDataSink(base_directory=bids_dir),
                iterfield=['in_file', 'entities'],
                name="ds_confounds")

ds_denoise = pe.MapNode(BIDSDataSink(base_directory=bids_dir),
                iterfield=['in_file', 'entities'],
                name="ds_denoise")

ds_connectivity = pe.MapNode(BIDSDataSink(base_directory=bids_dir),
                iterfield=['in_file', 'entities'],
                name="ds_connectivity")

ds_carpet_plot = pe.MapNode(BIDSDataSink(base_directory=bids_dir),
                             iterfield=['in_file', 'entities'],
                             name="ds_carpet_plot")

ds_matrix_plot = pe.MapNode(BIDSDataSink(base_directory=bids_dir),
                             iterfield=['in_file', 'entities'],
                             name="ds_matrix_plot")


# --- Connecting nodes
workflow.connect([
    (grabbing_bids, denoise, [('tr_dict', 'tr_dict')]),
    (grabbing_bids, denoise, [('fmri_prep', 'fmri_prep'),
                              ('fmri_prep_aroma', 'fmri_prep_aroma')]),
    (grabbing_bids, denoise, [('entities', 'entities')]),
    (grabbing_bids, prep_conf, [('conf_raw', 'conf_raw'),
                                ('conf_json', 'conf_json'),
                                ('entities', 'entities'),
                               ('fmri_prep_aroma', 'fmri_prep_aroma')]),
    (grabbing_bids, ds_confounds, [('entities', 'entities')]),
    (grabbing_bids, ds_denoise, [('entities', 'entities')]),
    (grabbing_bids, ds_connectivity, [('entities', 'entities')]),
    (grabbing_bids, ds_carpet_plot, [('entities', 'entities')]),
    (grabbing_bids, ds_matrix_plot, [('entities', 'entities')]),

    (pipelineselector, prep_conf, [('pipeline', 'pipeline')]),
    (pipelineselector, denoise, [('pipeline', 'pipeline')]),
    (prep_conf, group_conf_summary, [('conf_summary', 'conf_summary'),
                                    ('pipeline_name', 'pipeline_name')]),

    (pipelineselector, ds_denoise, [('pipeline_name', 'pipeline_name')]),
    (pipelineselector, ds_connectivity, [('pipeline_name', 'pipeline_name')]),
    (pipelineselector, ds_confounds, [('pipeline_name', 'pipeline_name')]),
    (pipelineselector, ds_carpet_plot, [('pipeline_name', 'pipeline_name')]),
    (pipelineselector, ds_matrix_plot, [('pipeline_name', 'pipeline_name')]),

    (prep_conf, denoise, [('conf_prep', 'conf_prep')]),
    (denoise, connectivity, [('fmri_denoised', 'fmri_denoised')]),

    (prep_conf, group_connectivity, [('pipeline_name', 'pipeline_name')]),
    (connectivity, group_connectivity, [('corr_mat', 'corr_mat')]),

    (prep_conf, ds_confounds, [('conf_prep', 'in_file')]),
    (denoise, ds_denoise, [('fmri_denoised', 'in_file')]),
    (connectivity, ds_connectivity, [('corr_mat', 'in_file')]),
    (connectivity, ds_carpet_plot, [('carpet_plot', 'in_file')]),
    (connectivity, ds_matrix_plot, [('matrix_plot', 'in_file')]),

    (group_connectivity, quality_measures, [('pipeline_name', 'pipeline_name'),
                                            ('group_corr_mat', 'group_corr_mat')]),
    (group_conf_summary, quality_measures, [('group_conf_summary', 'group_conf_summary')]),
    (quality_measures, merge_quality_measures, [('fc_fd_summary', 'fc_fd_summary'),
                                                ('edges_weight', 'edges_weight'),
                                                ('edges_weight_clean', 'edges_weight_clean'),
                                                ('exclude_list', 'exclude_list')]),
    (merge_quality_measures, pipelines_quality_measures,
        [('fc_fd_summary', 'fc_fd_summary'),
         ('edges_weight', 'edges_weight'),
         ('edges_weight_clean', 'edges_weight_clean')]),
    (merge_quality_measures, report_creator,
        [('exclude_list', 'excluded_subjects')]),
    (pipelines_quality_measures, report_creator,
        [('plot_pipeline_edges_density', 'plot_pipeline_edges_density'),
         ('plot_pipelines_edges_density_no_high_motion', 'plot_pipelines_edges_density_no_high_motion'),
         ('plot_pipelines_fc_fd_pearson', 'plot_pipelines_fc_fd_pearson'),
         ('plot_pipelines_fc_fd_uncorr', 'plot_pipelines_fc_fd_uncorr'),
         ('plot_pipelines_distance_dependence', 'plot_pipelines_distance_dependence')]),
    (pipelineselector, report_creator,
        [('pipeline', 'pipelines'),
         ('pipeline_name', 'pipelines_names')])
])






# Write graph of type orig
workflow.write_graph(graph2use='orig', dotfilename='./graph_orig.dot')

# Visualize graph
from IPython.display import Image
Image(filename="graph_orig.png")
