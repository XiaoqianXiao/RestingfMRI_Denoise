# RestingfMRI_Denoising
RestingfMRI_Denoising is a python based tool using fmriprep output to denoise resting state fMRI data
## Goals:
* Allow preprocessing of resting fMRI data automatically and base on customized demands.<br>
* Generalize the comparison results of different denoising settings to help the decision making of denoising settings.<br><br>
## inspired by:<br> 
[Ciric et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28302591/);<br>
[Parkes et al., 2018](https://pubmed.ncbi.nlm.nih.gov/29278773/);<br> 
fMRIprep (by Esteban et al.);<br> 
Fmriprep_denoising (by Scott Burwell);<br> 
Denoiser (by Chris Gorgolewski et al.);<br> 
fMRIDenoise (by Karolina Finc et al.);<br> 
XCP imaging pipeline (by Rastko Ciric et al.);<br> 
scripts structual followed fmridenoise and XCP imaging pipeline, also referred fmriprep_denoising for regressor calculation.
 

## Setup:
The RestingfMRI_Denoise using fMRIprep outputs as input. Before running RestingfMRI_Denoise, you must run fmripep first.
## Running:
There are three ways of using RestingfMRI_Denoise. <br />
The speed of running the tool itself is about: 2m per .nii.gz file.

* Docker image
    ```
    # pull the docker image of RestingfMRI_Denoise
    docker pull xiaoqianxiao/restingfmri_denoise:0.1.0
    # run the image container
    docker run --rm -ti -v <local directory with data>:<target path in container> --entrypoint=/bin/bash xiaoqianxiao/restingfmri_denoise:0.1.0
    RestingfMRI_Denoise <Your Data set> options
    ```

* Build on computer
    ```
    # installation
    python setup.py sdist bdist_wheel
    pip install "$(ls ./dist/*.whl)"
    # run in the terminal
    RestingfMRI_Denoise <Your Data set> options
    ```
    
    ```
    positional arguments:
        bids_dir              Path to fmriprep preprocessed BIDS dataset.

    options:
          -h, --help            show this help message and exit
          -sub SUBJECTS [SUBJECTS ...], --subjects SUBJECTS [SUBJECTS ...]
                                List of subjects, separated with spaces.
          -ses SESSIONS [SESSIONS ...], --sessions SESSIONS [SESSIONS ...]
                                List of session numbers, separated with spaces.
          -t TASKS [TASKS ...], --tasks TASKS [TASKS ...]
                                List of tasks names, separated with spaces.
          -p PIPELINES [PIPELINES ...], --pipelines PIPELINES [PIPELINES ...]
                                Name of pipelines used for denoising, can be both paths to c or name of pipelines from package
          -pa PARCELLATION [PARCELLATION ...], --parcellation PARCELLATION [PARCELLATION ...]
                                Name of parcellation used for denoising.
          -d DERIVATIVES [DERIVATIVES ...], --derivatives DERIVATIVES [DERIVATIVES ...]
                                Name (or list) of derivatives for which denoise should be run. By default
                                workflow looks for fmriprep dataset.
          --high-pass HIGH_PASS
                                High pass filter value, deafult 0.008.
          --low-pass LOW_PASS   Low pass filter value, default 0.08
          --profiler PROFILER   Run profiler along workflow execution to estimate resources usage PROFILER is
                                path to output log file.
          -g, --debug           Run RestingfMRI_Denoise in debug mode - richer output, stops on first unchandled
                                exception.
          --graph GRAPH         Create workflow graph at GRAPH path
          --dry                 Perform everything except actually running workflow
          -w WORK_DIR, --work_dir WORK_DIR
                                Path where intermediate results should be stored, default
                                /tmp/RestingfMRI_Denoise/
           ```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[example of pipeline json files](https://github.com/XiaoXiaoqian/flywheel_RestingfMRI_Denoise/blob/main/docs/pipeline_template.json).<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[list of pipelines build in tool](https://github.com/XiaoXiaoqian/flywheel_RestingfMRI_Denoise/blob/main/docs/pipelines).<br>
* Flywheel <br />
    Please see [here](https://github.com/XiaoXiaoqian/flywheel_RestingfMRI_Denoise) for more details.

