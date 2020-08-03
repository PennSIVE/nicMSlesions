# BIDS wrapper for nicMSlesions
#### Docker Hub image tags
Listed [here](https://hub.docker.com/r/pennsive/nicmslesions/tags)
- gpu: requires `nvidia-docker` or singularity `--nv` flag (preferred)
- cpu: CPU-only, also latest tag (works everywhere)
- gui: noVNC (CPU only)
## Usage
```
usage:  [-h] [--skip_bids_validator] [--t1_tag [T1_TAG]]
        [--flair_tag [FLAIR_TAG]]
        [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
        [--model_name [MODEL_NAME]] [--t_bin [T_BIN]] [--l_min [L_MIN]]
        [--min_error [MIN_ERROR]]
        [--fraction_negatives [FRACTION_NEGATIVES]]
        [--register [REGISTER]] [--denoise [DENOISE]]
        [--denoise_iter [DENOISE_ITER]] [--skull_strip [SKULL_STRIP]]
        [--save_tmp [SAVE_TMP]] [--debug [DEBUG]] [-v]
        input_dir output_dir {train,infer}

positional arguments:
  input_dir             The directory with the input dataset formatted
                        according to the BIDS standard (if t1 and flair tags
                        are not provided).
  output_dir            The directory where the output files should be stored.
                        If you are running group level analysis this folder
                        should be prepopulated with the results of
                        theparticipant level analysis.
  {train,infer}         train or infer

optional arguments:
  -h, --help            show this help message and exit
  --skip_bids_validator
                        Whether or not to perform BIDS dataset validation
  --t1_tag [T1_TAG]     T1 image file name if not using BIDS
  --flair_tag [FLAIR_TAG]
                        Flair image file name if not using BIDS
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be
                        analyzed. The label corresponds to
                        sub-<participant_label> from the BIDS spec (so it does
                        not include "sub-"). If this parameter is not provided
                        all subjects should be analyzed. Multiple participants
                        can be specified with a space separated list.
  --model_name [MODEL_NAME]
                        Optional model name
  --t_bin [T_BIN]       Threshold to binarize the output segmentations
  --l_min [L_MIN]       Minimum lesion volume
  --min_error [MIN_ERROR]
                        Minimum accuracy for computed lesion volume
  --fraction_negatives [FRACTION_NEGATIVES]
                        Fraction negatives
  --register [REGISTER]
                        Register modalities
  --denoise [DENOISE]   Denoise input
  --denoise_iter [DENOISE_ITER]
                        Denoise iterations
  --skull_strip [SKULL_STRIP]
                        Skull strip input
  --save_tmp [SAVE_TMP]
                        Save intermediate steps
  --debug [DEBUG]       Save debug output
  -v, --version         show program's version number and exit
```
## Examples
#### Run inference
```
# with BIDS dataset (single subject)
docker run -v ~/Downloads/ds000001-download:/in:ro -v $PWD/out:/out pennsive/nicmslesions /in /out infer --participant_label 01 --model_name baseline_2ch

# with any two images
docker run -v ~/Downloads/ds000001-download/sub-01/anat:/in:ro -v $PWD/out:/out pennsive/nicmslesions /in /out infer --t1_tag T1 --flair_tag T2 --model_name baseline_2ch

# on the cluster with singularity
qsub -l h_vmem=32G -l V100 -b y -cwd \
singularity run --nv -B $PWD/ds000001-download:/in:ro -v $PWD/out:/out nicmslesions_gpu.sif \
/in /out infer --participant_label 01 --model_name baseline_2ch
```
If your data is not in BIDS you can provide the `--t1_tag` and `--flair_tag` to specify individual files as input
#### Run training (not yet BIDSified)
```
qsub -l h_vmem=64G -l V100 -b y -cwd \
singularity exec --nv -B ~/lesion_seg_training:/data -B ~/repos/nicMSlesions:/root/nicMSlesions/ -B /usr/local/cuda-9.0 nicmslesions_gpu.sif \
python /root/nicMSlesions/nic_train_network_batch.py
```
#### Run GUI
```
docker run --name MSlesions -v $PWD:/data --rm -d -p 6080:80 pennsive/nicmslesions:gui
```