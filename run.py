#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
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
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                    'Multiple participant level analyses can be run independently '
                    '(in parallel) using the same output_dir.',
                    choices=['participant', 'group'])
parser.add_argument('action', help='train or infer',
                    choices=['train', 'infer'])
parser.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                    'corresponds to sub-<participant_label> from the BIDS spec '
                    '(so it does not include "sub-"). If this parameter is not '
                    'provided all subjects should be analyzed. Multiple '
                    'participants can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--skip_bids_validator', help='Whether or not to perform BIDS dataset validation',
                    action='store_true')
parser.add_argument('-v', '--version', action='version',
                    version='nicMSlesions version {}'.format(__version__))


args = parser.parse_args()

if not args.skip_bids_validator:
    run('bids-validator %s' % args.bids_dir)

subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
# for all subjects
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split(
        "-")[-1] for subject_dir in subject_dirs]

tmpdir = tempfile.mkdtemp()
config = {
    'train_folder': tmpdir + args.bids_dir,
    'inference_folder': tmpdir + args.bids_dir,
    'test_folder': tmpdir + args.bids_dir,
    'output_folder': args.output_dir
}
# running participant level
if args.analysis_level == "participant":

    # find all T1s
    for subject_label in subjects_to_analyze:
        print('subject', subject_label)
        full_subj_dir = tmpdir + args.bids_dir + "/sub-" + subject_label
        os.makedirs(full_subj_dir, exist_ok=True)
        for T1_file in glob(os.path.join(args.bids_dir, "sub-%s" % subject_label,
                                         "anat", "*_T1w.nii*")) + glob(os.path.join(args.bids_dir, "sub-%s" % subject_label, "ses-*", "anat", "*_T1w.nii*")):
            try:
                os.symlink(T1_file, full_subj_dir + "/t1.nii.gz")
            except FileExistsError:
                print("Skipping additional run", T1_file,
                      "for subject", subject_label)
        for flair_file in glob(os.path.join(args.bids_dir, "sub-%s" % subject_label,
                                            "anat", "*_FLAIR.nii*")) + glob(os.path.join(args.bids_dir, "sub-%s" % subject_label, "ses-*", "anat", "*_FLAIR.nii*")):
            try:
                os.symlink(flair_file, full_subj_dir + "/flair.nii.gz")
            except FileExistsError:
                print("Skipping additional run", flair_file,
                      "for subject", subject_label)
    fn = 'nic_infer_segmentation_batch' if args.action == "infer" else 'nic_train_network_batch'
    cmd = "python /nicMSlesions/%s.py" % (fn)
    run(cmd, config)

# running group level
elif args.analysis_level == "group":
    brain_sizes = []
    for subject_label in subjects_to_analyze:
        for brain_file in glob(os.path.join(args.output_dir, "sub-%s*.nii*" % subject_label)):
            try:
                os.symlink(brain_file, full_subj_dir + "/flair.nii.gz")
            except FileExistsError:
                print("Skipping additional run", brain_file,
                      "for subject", subject_label)

shutil.rmtree(tmpdir)
