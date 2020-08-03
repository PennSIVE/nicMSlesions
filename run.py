#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
import glob
import shutil
from glob import glob

__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'version')).read()


def run(command, env={}):
    merged_env = os.environ
    merged_env.update(env)
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               env=merged_env)
    while True:
        line = process.stdout.readline()
        line = str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d" % process.returncode)


parser = argparse.ArgumentParser(
    description='nicMSlesions entrypoint script.')
parser.add_argument('input_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard (if t1 and flair tags are not provided).')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('action', help='train or infer',
                    choices=['train', 'infer'])
parser.add_argument('--skip_bids_validator', help='Whether or not to perform BIDS dataset validation',
                    action='store_true')
parser.add_argument('--t1_tag', help='T1 image file name if not using BIDS', nargs="?", default=None)
parser.add_argument('--flair_tag', help='Flair image file name if not using BIDS', nargs="?", default=None)
parser.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                    'corresponds to sub-<participant_label> from the BIDS spec '
                    '(so it does not include "sub-"). If this parameter is not '
                    'provided all subjects should be analyzed. Multiple '
                    'participants can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--model_name', help='Optional model name', nargs="?", default="baseline_2ch")
parser.add_argument('--t_bin', help='Threshold to binarize the output segmentations', nargs="?", default='0.5')
parser.add_argument('--l_min', help='Minimum lesion volume', nargs="?", default='10')
parser.add_argument('--min_error', help='Minimum accuracy for computed lesion volume', nargs="?", default='0.5')
parser.add_argument('--fraction_negatives', help='Fraction negatives', nargs="?", default='2.0')
parser.add_argument('--register', help='Register modalities', nargs="?", default='True')
parser.add_argument('--denoise', help='Denoise input', nargs="?", default='True')
parser.add_argument('--denoise_iter', help='Denoise iterations', nargs="?", default='3')
parser.add_argument('--skull_strip', help='Skull strip input', nargs="?", default='True')
parser.add_argument('--save_tmp', help='Save intermediate steps', nargs="?", default='True')
parser.add_argument('--debug', help='Save debug output', nargs="?", default='True')
parser.add_argument('-v', '--version', action='version',
                    version='nicMSlesions version {}'.format(__version__))


args = parser.parse_args()

tags_given = args.t1_tag != None and args.flair_tag != None
if not args.skip_bids_validator and tags_given:
    run('bids-validator %s' % args.input_dir)

subjects_to_analyze = []
if args.participant_label:
    # only for a subset of subjects
    subjects_to_analyze = args.participant_label
elif tags_given:
    subjects_to_analyze = ["01"]
else:
    # for all subjects
    subject_dirs = glob(os.path.join(args.input_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split(
        "-")[-1] for subject_dir in subject_dirs]

tmpdir = tempfile.mkdtemp()
config = {
    'train_folder': tmpdir,
    'test_folder': tmpdir,
    'experiment': args.model_name,
    'pretrained_model': args.model_name,
    'fract_negative_positive': args.fraction_negatives,
    't_bin': args.t_bin,
    'l_min': args.l_min,
    'min_error': args.min_error,
    'register_modalities': args.register,
    'denoise': args.denoise,
    'denoise_iter': args.denoise_iter,
    'skull_stripping': args.skull_strip,
    'save_tmp': args.save_tmp,
    'debug': args.debug
}

for subject_label in subjects_to_analyze:
    full_subj_dir = tmpdir + "/sub-" + subject_label
    os.makedirs(full_subj_dir, exist_ok=True)
    if tags_given:
        os.symlink(glob(args.input_dir + "/*%s*" % (args.t1_tag))[0], full_subj_dir + "/t1.nii.gz")
        os.symlink(glob(args.input_dir + "/*%s*" % (args.flair_tag))[0], full_subj_dir + "/flair.nii.gz")
    else:
        for T1_file in glob(os.path.join(args.input_dir, "sub-%s" % subject_label,
                                            "anat", "*_T1w.nii*")) + glob(os.path.join(args.input_dir, "sub-%s" % subject_label, "ses-*", "anat", "*_T1w.nii*")):
            try:
                os.symlink(T1_file, full_subj_dir + "/t1.nii.gz")
            except FileExistsError: # we're only taking a single image for each subject
                print("Skipping additional run", T1_file,
                        "for subject", subject_label)
        for flair_file in glob(os.path.join(args.input_dir, "sub-%s" % subject_label,
                                            "anat", "*_FLAIR.nii*")) + glob(os.path.join(args.input_dir, "sub-%s" % subject_label, "ses-*", "anat", "*_FLAIR.nii*")):
            try:
                os.symlink(flair_file, full_subj_dir + "/flair.nii.gz")
            except FileExistsError:
                print("Skipping additional run", flair_file,
                        "for subject", subject_label)
fn = 'nic_infer_segmentation_batch' if args.action == "infer" else 'nic_train_network_batch'
cmd = "python /opt/nicMSlesions/%s.py" % (fn)
run(cmd, config)
# move output from tmpdir to args.output_dir
shutil.move(tmpdir, args.output_dir)

