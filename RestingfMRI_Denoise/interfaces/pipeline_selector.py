import os
from nipype.interfaces.base import SimpleInterface, BaseInterfaceInputSpec, TraitedSpec
from traits.trait_types import List, Dict, File, Str, Float
from RestingfMRI_Denoise.utils.utils import load_pipeline_from_json
from RestingfMRI_Denoise.utils.json_validator import is_valid

class PipelineSelectorInputSpecification(BaseInterfaceInputSpec):
    pipeline_path = File(exists=True)

class PipelineSelectorOutPutSpecification(TraitedSpec):
    pipeline = Dict(items=True)
    pipeline_name = Str(desc="Name of denoising strategy")

class PipelineSelector(SimpleInterface):
    input_spec = PipelineSelectorInputSpecification
    output_spec = PipelineSelectorOutPutSpecification

    def _run_interface(self, runtime):
        js = load_pipeline_from_json(self.inputs.pipeline_path)
        if not is_valid(js):
            raise ValueError("""
            Json file {} is not a valid pipeline, 
            check schema at Restingfmri_Denoise.utils.json_validator.py
            """.format(os.path.basename(self.inputs.pipeline_path)))
        self._results['pipeline'] = js
        self._results['pipeline_name'] = js['name']
        return runtime

# rudimentary test # TODO: Move to this to proper unittests
if __name__ == '__main__':
    from nipype import Node
    import glob
    reader = Node(PipelineSelector(), name="pipeline_selector")
    for path in glob.glob("../pipelines/*"):
        path = os.path.abspath(path)
        print(path)
        reader.inputs.pipeline_path = path
        pipeline = reader.run()
    print(pipeline.outputs)
