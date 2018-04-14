#!/usr/bin/env python
from __future__ import print_function
from sh import sbatch
import sh
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("job_scripts", nargs='+', help='a list of job scripts to execute')
parser.add_argument("--job_name", help='job name', type=str, required=True)
parser.add_argument("--mem_per_job", help='amount of memory allocated per job', type=int, default=10000)
parser.add_argument('--cpus_per_job', help='num. cpus per job', type=int, default=1)
parser.add_argument('--output', default='output.out', type=str)

args = parser.parse_args()
job_num = len(args.job_scripts)

jobs = []
print('submitting batched job [%s], %d sub-jobs' % (args.job_name, job_num))
for job_script in args.job_scripts:
	print('\tsubmitting: %s' % job_script)

slurm_script = """#!/usr/bin/env python

import sh, sys
jobs = []
for job_script in {job_scripts}:
	job = sh.bash(job_script, _bg=True, _out=sys.stdout)
	jobs.append(job)

for job in jobs: job.wait()
""".format(job_scripts='[%s]' % ', '.join(['"%s"' % job_script for job_script in args.job_scripts]))

job = sbatch('--gres', 'gpu:1',
             '--job-name', args.job_name,
             '--mem', args.mem_per_job * job_num,  # memory
             '--cpus-per-task', args.cpus_per_job * job_num,  # number of cpus
             '--time', 0,  # wait time: unlimited
             '--output', args.output,  # assume you don't need stdout
             _in=slurm_script)

print(job.stdout)
