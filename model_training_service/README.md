# This is a repository for the claim detection model for the DIME project.

The directory contains code and data for development of the Claim Detection model on Aalto Trion server. The directpry requires 4 main components for development:

1. Environment setup: `conda-env.yml`
2. Data and data preparation script: `./data` and `./data/data_preparation.py`
3. Model and model development script: `./model` and `./model/model_development.py`
4. Computing resource script: `submit.sh`

Optional: Logging and monitoring: `./logging` and `./logging/logging_monitoring.py`

## Environment setup


- The environment is set up using conda. The environment is defined in `conda-env.yml`. To [install Conda environment on triton](https://scicomp.aalto.fi/triton/apps/python-conda/#advanced-usage), run the following command:

```bash
module load mamba
cd `conda-env` directory
mamba env create -f conda-env.yml
```

[Optional]: If you want to update the environment after the first installation, run the following command:
```bash
mamba env update -f conda-env.yml
```

- To use the newly created environment through triton cmdline, activate it with the following command:

```bash
mamba activate claim-model-training-env
```

- To run [Jupyter notebook with the environment](https://scicomp.aalto.fi/triton/apps/jupyter/#installing-kernels-from-virtualenvs-or-anaconda-environments), run the following command:

```bash
conda env list # to find out the /path/to/conda_env
module load jupyterhub/live
envkernel conda --user --name INTERNAL_NAME --display-name="<My conda env name>" /path/to/conda_env
```

    Select kernel with "<My conda env name>" when running Jupyter notebook.

