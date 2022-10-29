import os
from glob import glob
import pandas as pd
import numpy as np
from pathlib import Path

from nipype.utils.filemanip import split_filename
from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec, SimpleInterface,
    ImageFile, File, Directory, traits
    )
import nibabel as nb
from nilearn import datasets
from nilearn.image import load_img
from nilearn.image import clean_img, smooth_img
from nilearn.image import resample_to_img
from nilearn.image import resample_img

class DenoiseInputSpec(BaseInterfaceInputSpec):
    fmri_prep = ImageFile(
        exists=True,
        desc='Preprocessed fMRI file',
        mandatory=True
    )
    fmri_prep_aroma = ImageFile(
        desc='ICA-Aroma preprocessed fMRI file',
        mandatory=False
    )
    conf_prep = File(
        exists=True,
        desc="Confound file",
        mandatory=True
    )
    pipeline = traits.Dict(
        desc="Denoising pipeline",
        mandatory=True)
    entities = traits.Dict(
        desc="entities dictionary",
        mandatory=True
    )
    tr_dict = traits.Dict(
        desc="dictionary of tr for all tasks",
        mandatory=True
    )
    output_dir = Directory(
        exists=True,
        desc="Output path"
    )
    high_pass = traits.Float(
        desc="High-pass filter",
    )
    low_pass = traits.Float(
        desc="Low-pass filter"
    )
    ica_aroma = traits.Bool(
        mandatory=False,
        desc='ICA-Aroma files exists'
    )
    smoothing = traits.Bool(
        mandatory=False,
        desc='Optional smoothing'
    )

class DenoiseOutputSpec(TraitedSpec):
    fmri_denoised = File(
        exists=True,
        desc='Denoised fMRI file',
        mandatory=True
    )

class Denoise(SimpleInterface):
    input_spec = DenoiseInputSpec
    output_spec = DenoiseOutputSpec

    def _run_interface(self, runtime):
        pipeline_name = self.inputs.pipeline['name']
        _, base, _ = split_filename(self.inputs.fmri_prep)
        denoised_file = f'{self.inputs.output_dir}/{base}_denoised_pipeline-{pipeline_name}.nii.gz'
        if not os.path.isfile(denoised_file):
            smoothing = self.inputs.smoothing
            pipeline_aroma = self.inputs.pipeline['aroma']
            pipeline_acompcor = self.inputs.pipeline['confounds']['acompcor']
            img = nb.load(self.inputs.fmri_prep)
            fname = self.inputs.fmri_prep
            #brain mask
            path, base, _ = split_filename(fname)  # Path can be removed later
#            ori_mask = glob(path + '/*rest*space-MNI152NLin2009cAsym*brain*mask.nii*')[0]
#             if pipeline_aroma:
#                 if not self.inputs.fmri_prep_aroma:
#                     raise ValueError("No ICA-AROMA files found")
#                 img = nb.load(self.inputs.fmri_prep_aroma)
#                 cur_mask = resample_to_img(ori_mask, self.inputs.fmri_prep_aroma, interpolation='nearest')
#             else: cur_mask = ori_mask
            # Handle possibility of null pipeline
            try:
                conf = pd.read_csv(self.inputs.conf_prep,
                                   delimiter='\t'
                                   #low_memory=False,
                                   #engine='python'
                                   )
                conf = conf.values
            except pd.errors.EmptyDataError:
                conf = None
            # Determine proper TR
            task = self.inputs.entities['task']
            if task in self.inputs.tr_dict:
                tr = self.inputs.tr_dict[task]
            else:
                raise KeyError(f'{task} TR not found in tr_dict')
            if smoothing and not pipeline_aroma:
               img = smooth_img(img, fwhm=6)
            
            if pipeline_acompcor:
                denoised_img = clean_img(
                    img,
                    confounds=conf,
                    high_pass=self.inputs.high_pass,
                    t_r=tr
                    #mask_img = cur_mask
                )
            else:
                denoised_img = clean_img(
                    img,
                    confounds=conf,
                    high_pass=self.inputs.high_pass,
                    low_pass=self.inputs.low_pass,
                    t_r=tr
                    #mask_img = cur_mask
                )            
            nb.save(denoised_img, denoised_file)
        self._results['fmri_denoised'] = denoised_file
        return runtime

# --- TESTS
if __name__ == '__main__':
    ### INPUTS #################################################################
    os.chdir('/Users/xiaoqian/projects/myRepository/RestingfMRI_Denoise_Demo/Restingfmri_Denoise/interfaces')
    path = Path(os.getcwd())
    root = path.parent.absolute()
    test_dir = os.path.join(root, 'tests')
    datadir = test_dir
    subjectID = '14'
    sessionID = 'baseline'
    taskID = 'test'
    fmri_prep_dir = os.path.join(datadir, 'derivatives/fmriprep',
                             'sub-'+str(subjectID),
                             'ses-'+str(sessionID),
                             'func')
    fmri_prep = os.path.join(fmri_prep_dir, 
                             'sub-'+str(subjectID)
                             +'_ses-'+str(sessionID)
                             +'_task-'+str(taskID)
                             +'_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
    conf_prep = os.path.join(datadir, 'derivatives/confounds_out', 
                             'sub-'+str(subjectID)
                             +'_ses-'+str(sessionID)
                             +'_task-'+str(taskID)
                             +'_desc-confounds_regressors_prep.tsv')
    entities = {'task': 'test'}
    tr_dict = {'test': 2}
    pipeline = {'name': 'try',
               'aroma': 'False',
               'confounds': {'acompcor': 'False'}}
    output_dir = os.path.join(datadir, 'derivatives/denoising_out')
    low_pass = 0.08
    high_pass = 0.008

    ### RUN INTERFACE ##########################################################
    dn = Denoise()
    dn.inputs.fmri_prep = fmri_prep
    dn.inputs.conf_prep = conf_prep
    dn.inputs.entities = entities
    dn.inputs.tr_dict = tr_dict
    dn.inputs.output_dir = output_dir
    dn.inputs.low_pass = low_pass
    dn.inputs.high_pass = high_pass
    dn.inputs.pipeline = pipeline
    dn.inputs.pipeline['aroma'] = pipeline['aroma']
    dn.inputs.pipeline['confounds']['acompcor'] = pipeline['confounds']['acompcor']

    results = dn.run()
    print(results.outputs)
